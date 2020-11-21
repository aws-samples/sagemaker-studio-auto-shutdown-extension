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

import { ReactWidget } from '@jupyterlab/apputils';
import { IStateDB } from '@jupyterlab/coreutils';
import { Widget } from '@phosphor/widgets';
import * as React from 'react';
import { AutoShutDownPanel } from '../components/AutoShutDownPanel';
import { autoShutDownWidgetStyle } from '../style/AutoShutDownWidgetStyle';

/**
 * A class that exposes the Autoshutdown plugin Widget.
 */
export class AutoShutDownWidget extends ReactWidget {
  constructor(
    stateDB: IStateDB,
    options?: Widget.IOptions,
  ) {
    super(options);
    this.node.id = 'ShutDownSession-root';
    this.addClass(autoShutDownWidgetStyle);
    this.stateDB = stateDB;
    console.log('ShutDown widget created');
  }

  render() {
    return (
      <AutoShutDownPanel
        stateDB={this.stateDB}
      />
    );
  }

  private stateDB: IStateDB;
}
