#!/bin/bash
if [ $# -eq 0 ]
then
  echo "Usage: upload_lambda.sh [s3 prefix]"
  exit 1
fi

zip ext_checker.zip ext_checker.py
aws s3 cp ext_checker.zip $1/ext_checker.zip
aws s3 cp ext_checker_cnf.yaml $1/ext_checker_cnf.template
