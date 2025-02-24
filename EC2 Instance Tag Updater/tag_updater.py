import json
import sys
import os
import os
import boto3
import base64
from botocore.exceptions import ClientError
import logging

# Set up logging using Python's logging module
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Log the incoming event
    logger.info(event)
    
    # Use STS to get the current AWS account ID
    client = boto3.client('sts')
    response_account = client.get_caller_identity()['Account']
    
    # Assume the event payload is the instance ID
    instance = event
    resourse_ARN = f"arn:aws:ec2:us-east-1:{response_account}:instance/{instance}"
    logger.info(resourse_ARN)
    
    # Initialize the resourcegroupstaggingapi client for tagging
    tag_client = boto3.client('resourcegroupstaggingapi')
    try:
        response_tag = tag_client.tag_resources(
            ResourceARNList=[resourse_ARN],
            Tags={'Environment': 'Prod'}
        )
        print(response_tag)
    except Exception as exp:
        logger.exception(exp)
        
    return {
        "compliance_type": "COMPLIANT",
        "annotation": "This resource is compliant with the rule."
    }
