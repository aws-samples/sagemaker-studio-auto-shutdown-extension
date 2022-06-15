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

import json

import tornado
import urllib3
from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join

from .idle_checker import IdleChecker

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = None

idle_checker = IdleChecker()


class SettingsHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self):
        global base_url
        global idle_checker
        input_data = self.get_json_body()
<<<<<<< HEAD
=======
        self.log.info("XXX: " + str(input_data))
>>>>>>> feat(extensions): formatted
        idle_checker.idle_time = int(input_data["idle_time"]) * 60  # convert to seconds
        if "keep_terminals" in input_data:
            idle_checker.keep_terminals = input_data["keep_terminals"]
        data = {
            "idle_time": str(idle_checker.idle_time),
            "keep_terminals": idle_checker.keep_terminals,
        }
        self.finish(json.dumps(data))


class RouteHandler(APIHandler):

    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    async def get(self):
        global idle_checker

        self.finish(
            json.dumps(
                {
                    "idle_time": idle_checker.idle_time,
                    "keep_terminals": idle_checker.keep_terminals,
<<<<<<< HEAD
                    "count": idle_checker.get_runcounts()
=======
                    "count": idle_checker.get_runcounts(),
                    "errors": str(idle_checker.get_runerrors()),
>>>>>>> feat(extensions): formatted
                }
            )
        )

    @tornado.web.authenticated
    async def post(self):
        global base_url
        global idle_checker

        client = tornado.httpclient.AsyncHTTPClient()
        input_data = self.get_json_body()
        idle_time = int(input_data["idle_time"]) * 60  # convert to seconds
<<<<<<< HEAD
        # Get the value of keep_terminals -- New line
        keep_terminals = input_data["keep_terminals"]

        try:
            data = {
                "greetings": "Hello, from JupyterLab Sagemaker Studio AutoShutdown Extension!"
            }
            # start background job
            idle_checker.start(
                self.base_url, self.log, client, idle_time, keep_terminals
=======

        try:
            data = {
                "greetings": "Hello, enjoy JupyterLab Sagemaker Studio AutoShutdown Extension!"
            }
            # start background job
            idle_checker.start(
                self.base_url, self.log, client, idle_time, keep_terminals=False
>>>>>>> feat(extensions): formatted
            )
            data["count"] = idle_checker.get_runcounts()
            self.finish(json.dumps(data))
        except Exception as e:
            # Other errors are possible, such as IOError.
            self.log.error("Error: " + str(e))


<<<<<<< HEAD
# Function to setup the web handdlers
=======
>>>>>>> feat(extensions): formatted
def setup_handlers(web_app, url_path):
    global base_url

    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, url_path, "idle_checker")
    route_pattern2 = url_path_join(base_url, url_path, "settings")
    handlers = [(route_pattern, RouteHandler), (route_pattern2, SettingsHandler)]
    web_app.add_handlers(host_pattern, handlers)
