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

import React, { ChangeEvent } from 'react';
import { inputColumnClass } from '../style/InputColumn';

export class InputColumn extends React.Component<{}, {}> {
  render() {
    return (
      <table className={inputColumnClass + ' inputColumnMarker'}>
        <tbody>{this.props.children}</tbody>
      </table>
    );
  }
}

export interface LabeledTextInputProps {
  label: string;
  value: number;
  title: string;
  onChange(event: ChangeEvent): void;
}

export class LabeledTextInput extends React.Component<LabeledTextInputProps, {}> {
  render() {
    return (
      <tr>
        <td>{this.props.label}</td>
        <td>
          <input onChange={this.props.onChange} value={this.props.value} title={this.props.title} type="number" min="1" max="525600" step="1" />
        </td>
      </tr>
    );
  }
}
