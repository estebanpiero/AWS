import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('INVITATIONS_TABLE', 'invitations-table'))  # Set in environment variables

def lambda_handler(event, context):
    try:
        token = event['pathParameters']['token']

        # Get invitation from database
        response = table.get_item(Key={'token': token})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid invitation token'})
            }

        invitation = response['Item']

        # Check if already used
        if invitation.get('used', False):
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invitation already used'})
            }

        # Check if expired
        expires_at = datetime.fromisoformat(invitation['expires_at'])
        if datetime.utcnow() > expires_at:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invitation expired'})
            }

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'valid': True,
                'inviter_email': invitation['inviter_email'],
                'expires_at': invitation['expires_at']
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
