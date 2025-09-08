import json
import boto3
import uuid
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('events-table')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Generate unique ID
        event_id = str(uuid.uuid4())

        # Prepare event data
        event_data = {
            'id': event_id,
            'event_id': event_id,  # For compatibility
            'title': body['title'],
            'date': body['date'],
            'address': body['address'],
            'description': body['description'],
            'creator_name': body['creator_name'],
            'created_at': datetime.utcnow().isoformat()
        }

        # Save to DynamoDB
        table.put_item(Item=event_data)

        # Send SNS notification (optional - configure SNS_TOPIC_ARN environment variable)
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        if sns_topic_arn:
            message = f"New Event Created: {body['title']} on {body['date']}"
            sns.publish(
                TopicArn=sns_topic_arn,  # Set this in Lambda environment variables
                Message=message,
                Subject='New Event Announcement'
            )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': 'Event created successfully', 'id': event_id})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
