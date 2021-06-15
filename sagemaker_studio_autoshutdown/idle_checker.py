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
from .my_test import get_apps, get_sessions, get_terminals

class IdleChecker(object):
    def __init__(self):
        self.interval = 10
        self._running = False
        self.count = 0
        self.task = None
        self.errors = None
        self.idle_time = 7200 #seconds
        self.ignore_connections = True
        self.tornado_client = None
        self._xsrf_token = None
        self.base_url = None
        self.app_url = "http://0.0.0.0:8888"
        self.keep_terminals = False
        self.zombie_app = defaultdict(lambda: False)
        self.zombia_app_activity = {}

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
    
    def is_idle(self, last_activity, seconds=False):
        last_activity = datetime.strptime(last_activity,"%Y-%m-%dT%H:%M:%S.%fz")
        self.log.info("comparing " + str(self.idle_time) + " and " + str((datetime.now() - last_activity).total_seconds()))
        if (datetime.now() - last_activity).total_seconds() > self.idle_time:
            self.log.info('Notebook is idle. Last activity time = ' + str(last_activity))
            return True
        else:
            self.log.info('Notebook is not idle. Last activity time = ' + str(last_activity))
            return False

    async def get_sessions(self):
        url = url_path_join(self.app_url, self.base_url, "api", "sessions")
        response = await self.tornado_client.fetch(url, method="GET")
        sessions = json.loads(response.body)
        self.log.info(str(sessions))
        return sessions
    
    async def get_terminals(self):
        terminal_url = url_path_join(self.app_url, self.base_url, "api", "terminals")
        terminal_response = await self.tornado_client.fetch(terminal_url, method="GET")
        terminals = json.loads(terminal_response.body)
        self.log.info(str(terminals))
        return terminals

    async def get_apps(self):
        url = url_path_join(self.app_url, self.base_url, "sagemaker", "api", "apps")
        response = await self.tornado_client.fetch(url, method="GET")
        apps = json.loads(response.body)
        self.log.info(str(apps))
        return apps

    async def build_app_info(self):
        apps = await self.get_apps()
        apps_info = {}
        for app in apps:
            apps_info[app['app_name']] = {
                'app': app,
                'sessions': [],
                'terminals': []
            }

        sessions = await self.get_sessions()
        for notebook in sessions:
            notebook_app_name = notebook['kernel']['app_name']
            apps_info[notebook_app_name]['sessions'].append(notebook)

        terminals = await self.get_terminals()
        for terminal in terminals:
            if terminal['name'].find('arn:') != 0:
                continue
            env_arn, terminal_id, instance_type = terminal['name'].split('__')
            for app in apps:
                if app['environment_arn'] == env_arn and app['instance_type'] == instance_type:
                    apps_info[app['app_name']]['terminals'].append(terminal)
                    break        

        self.log.info(str(apps_info))
        return apps_info

    async def delete_session(self, session):
        headers = {}
        headers['X-Xsrftoken'] = self._xsrf_token
        headers['Cookie'] = "_xsrf=" + self._xsrf_token
        kernel_id = session['kernel']['id']
        self.log.info("deleting kernel : " + str(kernel_id))
        url = url_path_join(self.app_url, self.base_url, "api", "kernels", str(kernel_id))
        deleted = await self.tornado_client.fetch(url,
            method="DELETE", 
            headers=headers)
        self.log.info("Delete kernel response: " + str(deleted))

    async def delete_application(self, app):
        headers = {}
        headers['X-Xsrftoken'] = self._xsrf_token
        headers['Cookie'] = "_xsrf=" + self._xsrf_token
        app_id = app['app_name']
        self.log.info("deleting app : " + str(app_id))       
        url = url_path_join(self.app_url, self.base_url, "sagemaker", "api", "apps", str(app_id))
        deleted_apps = await self.tornado_client.fetch(url, 
            method="DELETE", 
            headers=headers)
        self.log.info("Delete App response: " + str(deleted_apps))    
    
    def check_notebook(self, notebook):
        terminate = True
        if notebook['kernel']['execution_state'] == 'idle':
            self.log.info("found idle session:" + str(notebook))                    
            if not self.ignore_connections:
                if notebook['kernel']['connections'] == 0:
                    if not self.is_idle(notebook['kernel']['last_activity']):
                        terminate = False
                else:
                    terminate = False
            else:
                if not self.is_idle(notebook['kernel']['last_activity']):
                    terminate = False
        else:
            terminate = False
        return terminate
    
    async def idle_checks(self):
        apps_info = await self.build_app_info()
        for app_name, app in apps_info.items():
            
            if len(app['sessions']) < 1 and len(app['terminals']) > 0 and not self.keep_terminals:
                # TODO: delete terminals individually first                
                await self.delete_application(app)
            elif len(app['sessions']) > 0:
                for notebook in app['sessions']:
                    if self.check_notebook(notebook):
                        await self.delete_session(notebook)
