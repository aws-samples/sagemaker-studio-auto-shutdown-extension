/* Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"). You
 * may not use this file except in compliance with the License. A copy of
 * the License is located at
 *
 *     http://aws.amazon.com/apache2.0/
 *
 * or in the "license" file accompanying this file. This file is
 * distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
 * ANY KIND, either express or implied. See the License for the specific
 * language governing permissions and limitations under the License.
 */

import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IStateDB } from '@jupyterlab/coreutils';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IIconRegistry } from '@jupyterlab/ui-components';
import { ReadonlyJSONObject } from '@phosphor/coreutils';
import { requestAPIServer } from './sagemaker-studio-autoshutdown';
import { AutoShutDownWidget } from './widgets/AutoShutDownWidget';


/**
 * Initialization data for the sagemaker-studio-autoshutdown extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'sagemaker-studio-autoshutdown',
  autoStart: true,
  requires: [ILayoutRestorer, IIconRegistry, IRenderMimeRegistry, IStateDB],
  activate: async (app: JupyterFrontEnd,
    restorer: ILayoutRestorer,
    iconRegistry: IIconRegistry,
    rendermime: IRenderMimeRegistry,
    stateDB: IStateDB,) => {
    console.log('JupyterLab extension sagemaker-studio-autoshutdown is activated!');

    let IDLE_TIME = 3600
    const KEY = 'sagemaker-auto-shutdown:settings:data';

    // Create the schedule widget sidebar
    const autoShutDownWidget = new AutoShutDownWidget(stateDB);
    autoShutDownWidget.id = 'jp-autoshutdown';
    autoShutDownWidget.title.iconClass = 'jp-SideBar-tabIcon jp-sampleIcon autoshutdown-sidebar-icon';
    autoShutDownWidget.title.caption = 'Auto ShutDown';

    // Let the application restorer track the running panel for restoration of
    // application state (e.g. setting the running panel as the current side bar
    // widget).
    restorer.add(autoShutDownWidget, 'autoshutdown-sidebar');

    // Rank has been chosen somewhat arbitrarily to give priority to the running
    // sessions widget in the sidebar.
    app.shell.add(autoShutDownWidget, 'left', { rank: 220 });
    // POST request

    app.restored.then(() => stateDB.fetch(KEY)).then((s) => {
      const state = s as ReadonlyJSONObject;
      if (state) {
        if (state['IDLE_TIME']) {
          console.log(state['IDLE_TIME'])
          IDLE_TIME = Number(state['IDLE_TIME'])
        }

      }
    }).then(async () => {
      const dataToSend = {
        idle_time: IDLE_TIME
      };
      try {
        const reply = await requestAPIServer<any>('idle_checker', {
          body: JSON.stringify(dataToSend),
          method: 'POST'
        });
        console.log(reply);
      } catch (reason) {
        console.error(
          `Error on POST /sagemaker-studio-autoshutdown/idle_checker ${dataToSend}.\n${reason}`
        );
      }
    });

  }
};

export default extension;
