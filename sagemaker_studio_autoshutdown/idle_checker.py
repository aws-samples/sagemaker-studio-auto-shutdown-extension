# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import asyncio
import json
import time
import traceback
from contextlib import suppress
from datetime import datetime

from notebook.utils import url_path_join


class IdleChecker(object):
    def __init__(self):
        self.interval = 10  # frequency for checking idle sessions in seconds
        self._running = False
        self.count = 0
        self.task = None
        self.errors = None
        self.idle_time = 7200  # default idle time in seconds
        self.ignore_connections = True
        self.tornado_client = None
        self._xsrf_token = None
        self.base_url = None
        self.app_url = "http://0.0.0.0:8888"
        self.keep_terminals = False
        self.inservice_apps = {}

    # Function to GET the xsrf token
    async def fetch_xsrf_token(self):
        url = url_path_join(self.app_url, self.base_url, "tree")
        self.log.info("URL: " + str(url))
        response = await self.tornado_client.fetch(url, method="GET")
        self.log.info("response headers: " + str(response.headers))
        if "Set-Cookie" in response.headers:
            return response.headers["Set-Cookie"].split(";")[0].split("=")[1]

        return None

    # Invoke idle_checks() function
    async def run_idle_checks(self):
        while True:
            self.count += 1
            await asyncio.sleep(self.interval)
            try:
                self._xsrf_token = await self.fetch_xsrf_token()
                await self.idle_checks()
            except Exception:
                self.errors = traceback.format_exc()
                self.log.error(self.errors)

    # Entrypoint function to get the value from handlers(POST API call) and start background job
    def start(self, base_url, log_handler, client, idle_time, keep_terminals):
        self.idle_time = idle_time
        self.tornado_client = client
        self.base_url = base_url
        self.log = log_handler
        self.keep_terminals = keep_terminals

        if not self._running:
            self.count += 1
            self._running = True
            self.task = asyncio.ensure_future(self.run_idle_checks())

    async def stop(self):
        if self._running:
            self._running = False
            if self.task:
                self.task.cancel()
                with suppress(asyncio.CancelledError):
                    await self.task

    def get_runcounts(self):
        return self.count

    def get_runerrors(self):
        return self.errors

    # Function to check if the notebook is in Idle state
    def is_idle(self, last_activity, seconds=False):
        last_activity = datetime.strptime(last_activity, "%Y-%m-%dT%H:%M:%S.%fz")
        self.log.info(
            "comparing idle time limit "
            + str(self.idle_time)
            + " and elapsed time "
            + str((datetime.now() - last_activity).total_seconds())
        )
        if (datetime.now() - last_activity).total_seconds() > self.idle_time:
            self.log.info(
                "Notebook is idle. Last activity time = " + str(last_activity)
            )
            return True
        else:
            self.log.info(
                "Notebook is not idle. Last activity time = " + str(last_activity)
            )
            return False

    # Function to get the list of Kernel sessions
    async def get_sessions(self):
        url = url_path_join(self.app_url, self.base_url, "api", "sessions")
        response = await self.tornado_client.fetch(url, method="GET")
        sessions = json.loads(response.body)
        self.log.info(" Kernel Session is = " + str(sessions))
        return sessions

    # Function to get the list of System Terminals
    async def get_terminals(self):
        terminal_url = url_path_join(self.app_url, self.base_url, "api", "terminals")
        terminal_response = await self.tornado_client.fetch(terminal_url, method="GET")
        terminals = json.loads(terminal_response.body)
        return terminals

    # Function to get the list of running Apps
    async def get_apps(self):
        url = url_path_join(self.app_url, self.base_url, "sagemaker", "api", "apps")
        response = await self.tornado_client.fetch(url, method="GET")
        apps = json.loads(response.body)
        self.log.info(" Running App name is = " + str(apps))
        return apps

    # Function to build app information ( kernel sessions and image terminals)
    async def build_app_info(self):
        apps = await self.get_apps()
        apps_info = {}
        for app in apps:
            apps_info[app["app_name"]] = {"app": app, "sessions": [], "terminals": []}

        sessions = await self.get_sessions()
        for notebook in sessions:
            if notebook["kernel"]:
                notebook_app_name = notebook["kernel"]["app_name"]
                apps_info[notebook_app_name]["sessions"].append(notebook)

        terminals = await self.get_terminals()
        for terminal in terminals:
            if terminal["name"].find("arn:") != 0:
                continue
                
            env_arn, terminal_id, instance_type, *other = terminal["name"].split("__")
            
            self.log.info("Env Arn = " + str(env_arn))
            self.log.info("Terminal Id = " + str(terminal_id))
            self.log.info("Instance Type = "+ str(instance_type))

            for app in apps:
                if (
                    app["environment_arn"] == env_arn
                    and app["instance_type"] == instance_type
                ):
                    apps_info[app["app_name"]]["terminals"].append(terminal)
                    break

        self.log.info(str(apps_info))
        return apps_info

    # Function to delete a kernel session
    async def delete_session(self, session):
        headers = {}
        headers["X-Xsrftoken"] = self._xsrf_token
        headers["Cookie"] = "_xsrf=" + self._xsrf_token
        kernel_id = session["kernel"]["id"]
        self.log.info("deleting kernel : " + str(kernel_id))
        url = url_path_join(
            self.app_url, self.base_url, "api", "kernels", str(kernel_id)
        )
        deleted = await self.tornado_client.fetch(url, method="DELETE", headers=headers)
        self.log.info("Delete kernel response: " + str(deleted))

    # Function to delete an application
    async def delete_application(self, app_id):
        headers = {}
        headers["X-Xsrftoken"] = self._xsrf_token
        headers["Cookie"] = "_xsrf=" + self._xsrf_token
        self.log.info("deleting app : " + str(app_id))
        url = url_path_join(
            self.app_url, self.base_url, "sagemaker", "api", "apps", str(app_id)
        )
        deleted_apps = await self.tornado_client.fetch(
            url, method="DELETE", headers=headers
        )
        self.log.info("Delete App response: " + str(deleted_apps))
        if deleted_apps.code == 204 or deleted_apps.code == 200:
            self.inservice_apps.pop(app_id, None)

    # Function to check the notebook status
    def check_notebook(self, notebook):
        terminate = True
        if notebook["kernel"]["execution_state"] == "idle":
            self.log.info("found idle session:" + str(notebook))
            if not self.ignore_connections:
                if notebook["kernel"]["connections"] == 0:
                    if not self.is_idle(notebook["kernel"]["last_activity"]):
                        terminate = False
                else:
                    terminate = False
            else:
                if not self.is_idle(notebook["kernel"]["last_activity"]):
                    terminate = False
        else:
            terminate = False
        return terminate

    # Run idle checks apps and image terminals
    async def idle_checks(self):
        apps_info = await self.build_app_info()
        inservice_apps = self.inservice_apps
        deleted_apps = list(set(inservice_apps.keys()).difference(set(apps_info.keys())))
        for deleted_app in deleted_apps:
            inservice_apps.pop(deleted_app, None)
            self.log.info("inservice app not inservice anymore : " + str(deleted_app))

        for app_name, app in apps_info.items():
            num_sessions = len(app["sessions"])
            num_terminals = len(app["terminals"])

            if num_sessions > 0 or num_terminals > 0:
                self.log.info(
                    "# of sessions: "
                    + str(num_sessions)
                    + "; # of terminals: "
                    + str(num_terminals)
                )

            if num_sessions == 0 and num_terminals == 0:
                # Check if app is active and kill
                # Check if the current app is part of the in service apps
                if app_name not in inservice_apps:
                    # Regsiter a new inservice app
                    inservice_apps[app_name] = time.time()

                else:
                    if int(time.time() - inservice_apps[app_name]) > self.idle_time:
                        self.log.info(
                            "Keep alive time for terminal reached : " + str(app_name)
                        )
                        await self.delete_application(app_name)

            # elif num_sessions < 1 and num_terminals > 0 and self.keep_terminals == True:
            elif num_sessions < 1 and num_terminals > 0 and self.keep_terminals:
                self.log.info("keep terminals flag is True. Not killing the terminals.")
                pass

            elif (
                # num_sessions < 1 and num_terminals > 0 and self.keep_terminals == False
                num_sessions < 1
                and num_terminals > 0
                and not self.keep_terminals
            ):
                self.log.info("keep terminals flag: " + str(self.keep_terminals))
                # Wait for the inservice app
                self.log.info("New inservice app found : " + str(app_name))

                # Check if the current app is part of the in service apps
                if app_name not in inservice_apps:
                    # Regsiter a new inservice app
                    inservice_apps[app_name] = time.time()

                else:
                    if int(time.time() - inservice_apps[app_name]) > self.idle_time:
                        self.log.info(
                            "Keepalive time for terminal reached : " + str(app_name)
                        )
                        await self.delete_application(app_name)

            elif num_sessions > 0:
                # let's check if we have idle notebooks to kill
                nb_deleted = 0
                for notebook in app["sessions"]:
                    if self.check_notebook(notebook):
                        await self.delete_session(notebook)
                        nb_deleted += 1
                if num_sessions == nb_deleted:
                    await self.delete_application(app_name)
