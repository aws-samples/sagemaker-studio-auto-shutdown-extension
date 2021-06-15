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

import { IStateDB } from "@jupyterlab/coreutils";
import { ReadonlyJSONObject } from "@phosphor/coreutils";
import * as React from "react";
import { requestAPIServer } from "../sagemaker-studio-autoshutdown";
import {
  runSidebarSectionClass,
  sidebarButtonClass,
  alertAreaClass
} from "../style/SettingsPanel";
import { AlertProps } from "./Alert";
import { InputColumn, LabeledTextInput } from "./InputColumn";
import { Alert } from "./Alert"


const KEY = "sagemaker-auto-shutdown:settings:data";

/** Interface for AutoShutDownPanel component props */
export interface IAutoShutDownPanelProps {
  stateDB: IStateDB;
}

interface PersistentState {
  IDLE_TIME: number;
  keepTerminals: boolean;
}

interface IAutoShutDownPanelState extends PersistentState {
  alerts: (AlertProps & { key: string })[];
}

/** A React component for the autoshutdown extension's main display */
export class AutoShutDownPanel extends React.Component<
  IAutoShutDownPanelProps,
  IAutoShutDownPanelState
  > {
  constructor(props: IAutoShutDownPanelProps) {
    super(props);
    this.state = {
      IDLE_TIME: 120,
      keepTerminals: false,
      alerts: [],
    };

    this.loadState();
  }

  /**
   * Renders the component.
   *
   * @returns React element
   */
  render = (): React.ReactElement => {
    const notebookIndependent = <div>{this.renderViewButtons()}</div>;
    return <div>{notebookIndependent}</div>;
  };

  private renderViewButtons() {
    return (
      <form onSubmit={this.handleSubmit}>
        <div className={runSidebarSectionClass}>
          <InputColumn>
            <LabeledTextInput
              label="Idle time limit (in minutes):"
              value={this.state.IDLE_TIME}
              title="time after which to shutdown"
              onChange={this.onIdleTimeChange}
            />
          </InputColumn>
        </div>

        <div className={runSidebarSectionClass}>
          <label>
            Keep Terminals: 
            <input name="keepTerminals" type="checkbox" checked="{this.state.keepTerminals" />
          </label>
        </div>

        <div className={runSidebarSectionClass}>
          <input
            className={sidebarButtonClass}
            type="button"
            title="Updates settings and refresh"
            value="Submit"
            onClick={this.handleSubmit}
          />
        </div>

        <div className={alertAreaClass}>
          {this.state.alerts.map((alert) => (
            <Alert key={`alert-${alert.key}`} type={alert.type} message={alert.message} />
          ))}
        </div>

      </form>
    );
  }

  private onIdleTimeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ): void => {
      
      if(isNaN(Number(event.target.value)) || isNaN(parseInt(event.target.value))) {
          event.target.value=this.state.IDLE_TIME.toString();
      }
      const valid = event.target.validity.valid;
      if(!valid) {
          event.target.value=this.state.IDLE_TIME.toString(); 
      } 
    this.setState({ IDLE_TIME: parseInt(event.target.value) }, () => this.saveState());
  };

  private handleSubmit = async (): Promise<void> => {
    console.log("Updating settings!!!");

    console.log("Idle Time value to update is : " + this.state.IDLE_TIME);

    const dataToSend = { idle_time: this.state.IDLE_TIME };
    this.clearAlerts();
    try {
      const reply = await requestAPIServer<any>("settings", {
        body: JSON.stringify(dataToSend),
        method: "POST",
      });
      console.log(reply);
      this.addAlert({ message: `Updated settings` });
    } catch (reason) {
      console.error(
        `Error on POST /sagemaker-studio-autoshutdown/settings ${dataToSend}.\n${reason}`
      );
      this.addAlert({
        type: "error",
        message: `Error updating settings! "`,
      });
    }

    setInterval(() => this.clearAlerts(), 5000);
  };

  private alertKey = 0;
  private addAlert(alert: AlertProps) {
    const key = this.alertKey++;

    const keyedAlert: AlertProps & { key: string } = {
      ...alert,
      key: `alert-${key}`,
    };
    this.setState({ alerts: [keyedAlert] });
  }

  private clearAlerts() {
    this.setState({ alerts: [] });
  }

  private saveState() {
    const state = {
      IDLE_TIME: this.state.IDLE_TIME,
      keepTerminal: this.state.keepTerminal
    };

    this.props.stateDB.save(KEY, state);
  }

  private loadState() {
    this.props.stateDB.fetch(KEY).then((s) => {
      const state = s as ReadonlyJSONObject;
      if (state) {
        this.setState({
          IDLE_TIME: state["IDLE_TIME"] as number,
          keepTerminal: state["keepTerminal"] as boolean
        });
      }
    });
  }
}
