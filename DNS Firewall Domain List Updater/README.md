# DNS Firewall Domain List Updater

This repository contains an AWS Lambda function written in Python that updates an AWS Route 53 Resolver DNS Firewall Domain List using a list of domains stored in an S3 bucket. As an AWS Community Builder, I created this project to demonstrate how to integrate multiple AWS services using boto3.

## Overview

The Lambda function performs the following tasks:
- **Triggered by S3:**  
  It is invoked when a new object is created in a designated S3 bucket.
- **Fetches Domain List:**  
  It reads the file content from the S3 object and extracts domain names.
- **Updates DNS Firewall:**  
  It updates the specified DNS Firewall Domain List in Route 53 Resolver with the new set of domains using the 'REPLACE' operation.
- **Error Handling:**  
  Logs detailed error messages and returns appropriate HTTP responses based on success or failure.

## Function Code

The core functionality is defined in two functions within the `DNS_List_Updater.py` file:

### 1. `get_firewall_domain_list_id`
This helper function retrieves the ID of a DNS Firewall Domain List by its name using a paginator to list all domain lists.
  
### 2. `lambda_handler`
This is the entry point for the Lambda function. It:
- Validates the S3 bucket.
- Retrieves the object key from the event.
- Reads the file content and parses the domain names.
- Updates the firewall domain list via Route 53 Resolver.

## Deployment

### 1. `Create or Update the Lambda Function:`

- In the AWS Lambda console, create a new function or update an existing one.
- Upload the `DNS_List_Updater.py` file (or the packaged ZIP) as your Lambda code.

### 2. `Configure S3 Trigger:`

- Set up an S3 bucket event notification to trigger the Lambda function when a new object is created.
- Update the BUCKET_NAME and DOMAIN_LIST_NAME variables in the code with your actual S3 bucket name and Route 53 Resolver Domain List name.


### 3. `Set Up IAM Permissions:`

- Ensure that the Lambda execution role has permissions to:
        - Read objects from the specified S3 bucket.
        - Access and update Route 53 Resolver domain lists.

```json

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-threat-intel-bucket",
                "arn:aws:s3:::my-threat-intel-bucket/*"
            ]
        }
    ]
}

