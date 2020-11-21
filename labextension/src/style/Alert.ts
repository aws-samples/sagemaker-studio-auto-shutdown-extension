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

import { style } from 'typestyle';

// Alert styles are cloned from Bootstrap 3
export const alert = style({
  padding: '15px',
  marginBottom: '20px',
  border: '1px solid transparent',
  borderRadius: '4px',
});

export const alertDanger = style({
  color: '#a94442',
  backgroundColor: '#f2dede',
  borderColor: '#ebccd1',
});

export const alertWarning = style({
  color: '#8a6d3b',
  backgroundColor: '#fcf8e3',
  borderColor: '#faebcc',
});

export const alertInfo = style({
  color: '#31708f',
  backgroundColor: '#d9edf7',
  borderColor: '#bce8f1',
});

export const alertSuccess = style({
  color: '#3c763d',
  backgroundColor: '#dff0d8',
  borderColor: '#d6e9c6',
});
