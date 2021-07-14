"""Lambda function to log in to SageMaker Studio as a user and run setup commands

SageMaker Studio user profile name is provided in the input event (UserProfileName or userProfileName).

SageMaker Studio domain ID is either:
- Provided in the input event (DomainId or domainId), or else
- Configured via ENV_DOMAIN_ID environment variable, or else
- Queried by the Lambda using SageMaker ListDomains API

Commands to be executed are hard-coded in the COMMAND_SCRIPT variable below.
"""

# Python Built-Ins:
import json
import logging
import os
import re
import time

# External Dependencies:
import boto3
import requests
import websocket

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
smclient = boto3.client("sagemaker")

ENV_DOMAIN_ID = os.environ.get("SAGEMAKER_DOMAIN_ID")
COMMAND_SCRIPT = [
    "rm -rf ~/.auto-shutdown",
    "git clone https://github.com/aws-samples/sagemaker-studio-auto-shutdown-extension.git --depth 1 ~/.auto-shutdown",
    "pwd && ls",
    "cd ~/.auto-shutdown && ./install_tarball.sh",
]
# Regular expression for determining when the terminal has finished executing the last command and is ready
# for next input:
PROMPT_REGEX = r"bash-[\d\.]+\$ $"

def get_domain_id() -> str:
    if ENV_DOMAIN_ID:
        return ENV_DOMAIN_ID

    logger.debug("Auto-discovering SMStudio domain ID via ListDomains API")
    domains_resp = smclient.list_domains()
    domains = domains_resp["Domains"]
    if len(domains) < 0:
        raise ValueError(f"No SageMaker Studio domains in this region!")
    elif len(domains) > 1:
        raise ValueError(
            f"Cannot automatically select SageMaker Studio domain: multiple ({len(domains)}) were found"
        )

    return domains[0]["DomainId"]


def lambda_handler(event, context):
    logger.debug("Received: %s", event)
    domain_id = event.get("DomainId", event.get("domainId"))
    if domain_id is None:
        domain_id = get_domain_id()

    user_profile_name = event.get("UserProfileName", event.get("userProfileName"))
    if user_profile_name is None:
        raise ValueError(
            f"Input event must include top-level property 'UserProfileName' (or 'userProfileName')"
        )

    logger.info(f"Processing request for {domain_id}/{user_profile_name}")
    run_commands(domain_id, user_profile_name)


def run_commands(domain_id: str, user_profile_name: str):
    logger.info(f"[{domain_id}/{user_profile_name}] Generating presigned URL")
    # (This will only work for IAM-authenticated Studio domains)
    presigned_resp = smclient.create_presigned_domain_url(
        DomainId=domain_id,
        UserProfileName=user_profile_name,
    )
    sagemaker_login_url = presigned_resp["AuthorizedUrl"]

    # Login URL like https://d-....studio.{AWSRegion}.sagemaker.aws/auth?token=...
    # API relative to https://d-....studio.{AWSRegion}.sagemaker.aws/jupyter/default
    api_base_url = sagemaker_login_url.partition("?")[0].rpartition("/")[0] + "/jupyter/default"

    # Need to make our requests via a session so cookies/etc persist:
    reqsess = requests.Session()
    logger.info(f"[{domain_id}/{user_profile_name}] Logging in")
    login_resp = reqsess.get(sagemaker_login_url)

    # If JupyterServer app only just started up, it may not be ready yet: In which case we need to wait for
    # it to start. Here we'll use the same 2sec /app polling logic as implemented by the SMStudio front-end
    # at the time of writing:
    if "_xsrf" not in reqsess.cookies:
        logger.info(f"[{domain_id}/{user_profile_name}] Waiting for JupyterServer start-up...")
        app_status = "Unknown"
        base_url = sagemaker_login_url.partition("?")[0].rpartition("/")[0]
        while app_status not in {"InService", "Terminated"}:
            time.sleep(2)
            app_status = reqsess.get(f"{base_url}/app?appType=JupyterServer&appName=default").text
            logger.debug(f"Got app_status {app_status}")

        if app_status == "InService":
            logger.info(f"[{domain_id}/{user_profile_name}] JupyterServer app ready")
            ready_resp = reqsess.get(api_base_url)
        else:
            raise ValueError(f"JupyterServer app in unusable status '{app_status}'")


    logger.info(f"[{domain_id}/{user_profile_name}] Creating terminal")
    terminal_resp = reqsess.post(
        f"{api_base_url}/api/terminals",
        # The XSRF token is required on any state-changing request types e.g. POST/DELETE/etc, but seems
        # that it can be put either in header or query string.
        # For more information on this pattern, you can see e.g:
        # https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
        params={ "_xsrf": reqsess.cookies["_xsrf"] },
    )
    terminal = terminal_resp.json()
    terminal_name = terminal["name"]  # Typically e.g. '1'.

    # Actually using a terminal (or notebook kernel) is done via websocket channels
    ws_base_url = "wss://" + api_base_url.partition("://")[2] + "/terminals/websocket"
    cookies = reqsess.cookies.get_dict()

    logger.info(f"[{domain_id}/{user_profile_name}] Connecting to:\n{ws_base_url}/{terminal_name}")
    ws = websocket.create_connection(
        f"{ws_base_url}/{terminal_name}",
        cookie="; ".join(["%s=%s" %(i, j) for i, j in cookies.items()]),
    )

    try:
        logger.info(f"[{domain_id}/{user_profile_name}] Waiting for setup message")
        setup = None
        while setup is not None:
            res = json.loads(ws.recv())
            if res[0] == "setup":
                setup = res[1]  # Just get {} in all my tests

        # Send commands one by one, waiting for each to complete and re-show prompt:
        prompt_exp = re.compile(PROMPT_REGEX, re.MULTILINE)
        for ix, c in enumerate(COMMAND_SCRIPT):
            ws.send(json.dumps(["stdin", c + "\n"]))
            # Assuming echo is on, stdin messages will be echoed to stdout anyway so no need to log

            while True:
                res = json.loads(ws.recv())
                # res[0] is the stream so will be e.g. 'stdout', 'stderr'
                # res[1] is the content
                logger.info(f"[{domain_id}/{user_profile_name}] {res[0]}: {res[1]}")
                # You may want to apply some more RegExs here to log a little less verbosely, or actively
                # check for failure/success of your particular script.
                if res[0] == "stdout" and prompt_exp.search(res[1]):
                    break
                # No need to push too hard in recv()ing the tiniest possible chunks!
                time.sleep(0.1)

        logger.info(f"[{domain_id}/{user_profile_name}] Complete")
    finally:
        ws.close()
