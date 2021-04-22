# SageMaker Studio Auto Shutdown Extension Checker

This lambda function checks periodically if all the user profiles under each SageMaker Studio Domain has installed the [extension for auto-shutdown idle notebooks](https://github.com/aws-samples/sagemaker-studio-auto-shutdown-extension/tree/main/sagemaker_studio_autoshutdown). The lambda function will run once a day and send the list of all the user profiles which has no installed auto-shutdown extension to an SNS topic. Studio admins can subscribe to this SNS topic to get notifications daily if any of the user profiles has no extension installed.

## Resources to be provisioned

![architecture](assets/arch.jpg?raw=true "Arch")

## Steps to install

1. Run the **upload_lambda.sh** function which packages and uploads the lambda function to S3. You need to specify the S3 prefix as an input argument of the script. The script also uploads the CloudFormation template to S3 which deploys the lambda function and creates the corresponding SNS topic.
```bash
./upload_lambda.sh s3://ext-checker/
```

2. Push the **Launch** button below. Switch to the proper region.

[![Launch in us-west-2](assets/launch-stack.png?raw=true)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=auto-shutdown-ext-checker&templateURL=https://bucket-name.s3.us-west-2.amazonaws.com/ext_checker_cnf.template)

3. Update the S3 URL of the CNF template file (uploaded by the *upload_lambda.sh* script):

![Alt Step 1](assets/step1.jpg?raw=true "Step 1")

4. Provide your S3 object url for your lambda function package uploaded by the *upload_lambda.sh* script. Click on the *Next* button.

![Alt Step 2](assets/step2.jpg?raw=true "Step 2")

5. As we are provisioning a role for the lambda function, you have to allow the IAM provisioning capability for the template as well. Hit on the *Create stack* button.

![Alt Step 3](assets/step3.jpg?raw=true "Step 3")

6. *(Optional)* Subscribe to the SNS topic to get notification via email

Tha lambda function publish the list of SageMaker Studio User Profiles not having the auto-shutdown extension installed into an SNS topic. It is up to you how you would handle these notification. For example, you can subscribe into this SNS topic with your email address and you can get a notification in email every time when the lambda function runs and there are User Profiles without the extension installed.

To subscribe to the SNS topic with your email address, please go to the **SNS Console / Topics** and find the provisioned SNS topic (**studio-ext-checker-alarms**). Click on the **Create subscription** button. For *Protocol*, please seled Email and you can specify your Email in the *Endpoint* text box. Once you have created the subscription, you will get an email from the SNS service to confirm your subscription. After the confirmation you will get an email each time when there is a new notification pushed into this topic.

7. Test your lambda function

To test your lambda function, please go to the **Lambda** console and find the provisionged **auto-shutdown-ext-checker** function. To add a new test even, click on the **Test** button and select the **Create test event** menu item.

When you call the Lambda function, you have to pass the **Region** and the **SNS topic name** where to the alarms will be published. These parameters needs to be passed as a JSON document, please see the image below. For SNS topic, you have to provide the fully qualifies ARN.

![Alt Step 5](assets/step55.jpg?raw=true "Step 3")

8. Schedule to run the Extension Checker daily

Go to the **CloudWatch** console, click on the **Events/Rules** on the left navigation plane. Click on **Create rule**. Set the Event Source to Schedule and provide the desired cadence to run the function *(e.g. daily)*. Click on the Add target button, select the Lambda function and provide the following JSON document as input:

```json
{ "region": "us-west-2", "sns-topic": "arn:aws:sns:us-west-2:<account id>:studio-ext-checker-alarms" }
```



