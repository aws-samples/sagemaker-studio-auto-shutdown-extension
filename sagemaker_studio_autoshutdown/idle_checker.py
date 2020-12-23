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

import time, os, sys, sched
import asyncio
from contextlib import suppress
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import traceback
import tornado
from notebook.utils import url_path_join

class IdleChecker(object):
    def __init__(self):
        self.interval = 10
        self._running = False
        self.count = 0
        self.task = None
        self.errors = None
        self.idle_time = 120
        self.ignore_connections = True
        self.tornado_client = None
        self._xsrf_token = None
        self.base_url = None
        self.app_url = "http://0.0.0.0:8888"

    async def fetch_xsrf_token(self):
        url = url_path_join(self.app_url, self.base_url, "tree")
        self.log.info("URL: " + str(url))
        response = await self.tornado_client.fetch(url, method="GET")
        self.log.info("response headers: " + str(response.headers))
        
        if 'Set-Cookie' in response.headers:
            return response.headers['Set-Cookie'].split(";")[0].split("=")[1]
            
        return None


    async def run_idle_checks(self):
        while True:
            self.count += 1
            await asyncio.sleep(self.interval)
            
            # do something here
            try:
                self._xsrf_token = await self.fetch_xsrf_token()
                await self.idle_checks()
            except Exception as e:
                self.errors = traceback.format_exc()
                self.log.error(self.errors)

    def start(self, base_url, log_handler, client, idle_time):
        self.idle_time = idle_time
        self.tornado_client = client
        self.base_url = base_url
        self.log = log_handler
        
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
    
    def is_idle(self, last_activity, seconds=False):
        last_activity = datetime.strptime(last_activity,"%Y-%m-%dT%H:%M:%S.%fz")
        self.log.info("comparing " + str(self.idle_time) + " and " + str((datetime.now() - last_activity).total_seconds()))
        if (datetime.now() - last_activity).total_seconds() > self.idle_time:
            self.log.info('Notebook is idle. Last activity time = ' + str(last_activity))
            return True
        else:
            self.log.info('Notebook is not idle. Last activity time = ' + str(last_activity))
            return False

    async def idle_checks(self):
        idle = {}
        idle = defaultdict(lambda: True)
        kernels_state = {}

        # get sessions. app_name is not found in Kernels api, so have to call the sessions api
        url = url_path_join(self.app_url, self.base_url, "api", "sessions")
        response = await self.tornado_client.fetch(url, method="GET")
        sessions = json.loads(response.body)
        self.log.info(str(sessions))

        if len(sessions) > 0:
            for notebook in sessions:
                kernels_state[notebook['kernel']['id']] = True # set default to True
                idle[notebook['kernel']['app_name']] = True

            self.log.info("There are some alive sessions")
            for notebook in sessions:
                # Idleness is defined by Jupyter
                # https://github.com/jupyter/notebook/issues/4634
                if notebook['kernel']['execution_state'] == 'idle':
                    self.log.info("found idle session:" + str(notebook))
                    
                    if not self.ignore_connections:
                        if notebook['kernel']['connections'] == 0:
                            if not self.is_idle(notebook['kernel']['last_activity']):
                                idle[notebook['kernel']['app_name']] = False
                                kernels_state[notebook['kernel']['id']] = False
                        else:
                            idle[notebook['kernel']['app_name']] = False
                            kernels_state[notebook['kernel']['id']] = False
                    else:
                        if not self.is_idle(notebook['kernel']['last_activity']):
                            idle[notebook['kernel']['app_name']] = False    
                            kernels_state[notebook['kernel']['id']] = False                    

                else:
                    idle[notebook['kernel']['app_name']] = False
                    kernels_state[notebook['kernel']['id']] = False

        else:
            #TODO: there are no sessions.. Checking for running Apps.
            self.log.info("There are no sessions found!")
            pass


        headers = {}
        headers['X-Xsrftoken'] = self._xsrf_token
        headers['Cookie'] = "_xsrf=" + self._xsrf_token
        
        #delete kernels
        for kernel_id in kernels_state:
            self.log.info("check idleness for kernel ID : " + str(kernel_id) + ", " + str(kernels_state[kernel_id]))
            if kernels_state[kernel_id]:
                # get kernel by ID
                self.log.info("deleting kernel : " + str(kernel_id))
                url = url_path_join(self.app_url, self.base_url, "api", "kernels", str(kernel_id))
                deleted = await self.tornado_client.fetch(url,
                    method="DELETE", 
                    headers=headers)
                self.log.info("Delete kernel response: " + str(deleted))

        #delete apps
        for session in idle: 
            self.log.info("check idleness for App : " + str(session) + ", " + str(idle[session]))
            if idle[session]: # This means kernel is idle
                self.log.info("idle found : " + str(session))
                
                url = url_path_join(self.app_url, self.base_url, "sagemaker", "api", "apps", str(session))
                deleted_apps = await self.tornado_client.fetch(url, 
                    method="DELETE", 
                    headers=headers)
                self.log.info("Delete App response: " + str(deleted_apps))    


