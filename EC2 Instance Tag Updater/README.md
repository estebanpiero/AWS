# EC2 Instance Tag Updater

This repository contains an AWS Lambda function written in Python that reviews and updates the tags on an EC2 instance. 

As an AWS Community Builder, I developed this function to assign a TAG to a non compliance EC2 intance.

ReadMore: https://medium.com/aws-in-plain-english/achieving-tag-compliance-with-aws-config-systems-manager-and-lambda-7840ec3f1c3b

## Overview

The Lambda function performs the following tasks:
- **Logging:**  
  Utilizes Python’s logging module to capture and report events and errors.
- **AWS Account Identification:**  
  Retrieves the AWS account ID using the STS service.
- **ARN Construction:**  
  Constructs the ARN for an EC2 instance based on the instance ID provided in the event.
- **Tagging:**  
  Uses the AWS Resource Groups Tagging API to apply the tag `"Environment": "Prod"` to the target instance.
- **Compliance Reporting:**  
  Returns a JSON response indicating that the resource complies with the specified tagging rule.
