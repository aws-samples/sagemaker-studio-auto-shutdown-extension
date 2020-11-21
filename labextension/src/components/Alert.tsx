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

import * as React from "react";
import {
  alert,
  alertDanger,
  alertWarning,
  alertInfo,
  alertSuccess,
} from "../style/Alert";

export interface AlertProps {
  type?: string;
  message: string;
}

export class Alert extends React.Component<AlertProps, {}> {
  render() {
    return (
      <div className={`${alert} ${this.alertClass(this.props.type)}`}>
        {this.props.message}
      </div>
    );
  }

  private alertClass(type: string) {
    const classes: Record<string, string> = {
      error: alertDanger,
      alert: alertWarning,
      notice: alertInfo,
      success: alertSuccess,
    };
    return classes[type] || classes.success;
  }
}
