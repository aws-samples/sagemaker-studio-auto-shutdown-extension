# Lambda Function for checking if auto shutdown extension was installed for every 
# user profiles in each domain

import json
import boto3
import requests

DEFAULT_REGION = 'us-west-2'

def lambda_handler(event, context):
    
    region = event.get('region', DEFAULT_REGION)
    topic_arn = event.get('sns-topic')
    
    sagemaker = boto3.client('sagemaker', region)
    sns = boto3.client('sns', region)
    
    try:
        
        user_profiles = sagemaker.list_user_profiles()
        no_ext_list = []
        
        for user in user_profiles['UserProfiles']:
            domain_id = user['DomainId']
            user_profile = user['UserProfileName']

            presigned_url = sagemaker.create_presigned_domain_url(
              DomainId=domain_id, UserProfileName=user_profile)
        
            session = requests.Session()
            session.get(presigned_url['AuthorizedUrl'])
            try:
                response = session.get('https://{}.studio.{}.sagemaker.aws/jupyter/default/sagemaker-studio-autoshutdown/idle_checker'.format(domain_id, region))
                ext_installed = True if response.status_code == 200 else False
            except requests.exceptions.Timeout:
                ext_installed = False
            
            if not ext_installed:
                no_ext_list.append({'domain-id': domain_id, 'user-profile': user_profile})
        
        if len(no_ext_list) > 1:
            payload = { 'profiles_with_no_auto_shutdown_ext': no_ext_list }
            sns.publish(TargetArn=topic_arn, Message=json.dumps(payload))
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Auto-shutdown extension check complete')
    }
