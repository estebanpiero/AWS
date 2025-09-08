import json
import boto3
import uuid
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('INVITATIONS_TABLE', 'invitations-table'))  # Set in environment variables

def lambda_handler(event, context):
    try:
        # Generate invitation token
        invitation_token = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(days=5)).isoformat()

        # Get inviter info from request
        body = json.loads(event['body'])
        inviter_email = body.get('inviter_email', 'unknown')

        # Store invitation
        table.put_item(Item={
            'token': invitation_token,
            'inviter_email': inviter_email,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at,
            'used': False
        })

        # Generate invitation URL
        # REPLACE 'your-bucket-name' with your actual S3 bucket name
        # REPLACE 'YOUR_REGION' with your AWS region
        base_url = os.environ.get('FRONTEND_URL', 'http://your-bucket-name.s3-website-YOUR_REGION.amazonaws.com')
        invitation_url = f"{base_url}/register.html?token={invitation_token}"

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'invitation_url': invitation_url,
                'expires_at': expires_at
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
