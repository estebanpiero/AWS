# Video Transcription Starter

This repository contains an AWS Lambda function written in Python that automatically starts an Amazon Transcribe job when a video file is uploaded to a designated S3 folder. As an AWS Community Builder, I created this project to demonstrate how to integrate S3 events with Amazon Transcribe to automate video transcription workflows.

## Overview

The Lambda function performs the following steps:
- **Triggered by S3:**  
  The function is invoked when an object is created in an S3 bucket.
- **Folder Verification:**  
  It checks if the uploaded object is located in the `videos_to_transcript/` folder.
- **Starting a Transcription Job:**  
  If the file is in the correct folder, the function initializes an Amazon Transcribe job:
  - Generates a unique job name.
  - Constructs the media URI from the S3 bucket and object key.
  - Determines the media format from the file extension.
  - Specifies the language (`en-US`) and output bucket for the transcription.
- **Response:**  
  Returns a success message indicating that the transcription job was started.

## Deployment

### 1. `Create/Update the Lambda Function:`

- Open the AWS Lambda console and create a new function or update an existing one.
- Upload the lambda_function.py file (or a packaged ZIP file) containing your code.

### 2. `Configure the S3 Trigger:`

- Set up an S3 bucket event notification to trigger the Lambda function on object creation.
- Ensure that only objects in the videos_to_transcript/ folder trigger the function.

### 3. `Set Up IAM Permissions:`

- The Lambda execution role must have the necessary permissions to:
- Read from the source S3 bucket.
- Start transcription jobs via Amazon Transcribe.
- Write outputs to the designated transcription output S3 bucket.


## Testing

### Local Testing:

- Use tools like the AWS SAM CLI to simulate Lambda invocation locally.

```bash

sam local invoke "YourLambdaFunctionName" -e event.json

```

Ensure the event.json file mirrors the S3 event structure.

### AWS Console Testing:

- Use the Test feature within the AWS Lambda console with a sample event payload.