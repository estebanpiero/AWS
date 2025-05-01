import json
import boto3
import os
import uuid
from datetime import datetime
from typing import Dict, Any
from botocore.exceptions import ClientError
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Environment variables
TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def validate_event_data(event_data: Dict[str, Any]) -> bool:
    """Validate the required fields in event data"""
    required_fields = ['title', 'date', 'description']
    return all(field in event_data for field in required_fields)

def store_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Store event in DynamoDB"""
    if not TABLE_NAME:
        raise ValueError("DYNAMODB_TABLE environment variable is not set")

    table = dynamodb.Table(TABLE_NAME)
    
    # Add additional fields
    event_data['event_id'] = str(uuid.uuid4())
    event_data['created_at'] = datetime.utcnow().isoformat()
    
    try:
        table.put_item(Item=event_data)
        logger.info(f"Successfully stored event: {event_data['event_id']}")
        return event_data
    except ClientError as e:
        logger.error(f"Failed to store event in DynamoDB: {str(e)}")
        raise

def send_sns_notification(event_data: Dict[str, Any]) -> None:
    """Send formatted SNS notification about new event"""
    if not TOPIC_ARN:
        raise ValueError("SNS_TOPIC_ARN environment variable is not set")
    
    try:
        # Format the date to be more readable
        event_date = datetime.fromisoformat(event_data['date']).strftime('%B %d, %Y')
        created_at = datetime.fromisoformat(event_data['created_at']).strftime('%B %d, %Y at %I:%M %p UTC')
    except ValueError:
        event_date = event_data['date']
        created_at = event_data['created_at']
    
    # Create a formatted message using Unicode characters for borders and bullets
    message = f"""
╔══════════════════════════════════════╗
             EVENT DETAILS
╚══════════════════════════════════════╝

📌 Title: {event_data['title']}
📅 Date: {event_date}

📝 Description:
{event_data['description']}

ℹ️ Additional Information:
• Event ID: {event_data['event_id']}
• Created: {created_at}

═══════════════════════════════════════
"""
    
    try:
        response = sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=f"New Event: {event_data['title']}",
            Message=message
        )
        logger.info(f"Successfully published message to SNS. MessageId: {response['MessageId']}")
    except ClientError as e:
        logger.error(f"Failed to publish to SNS. Error: {str(e)}")
        raise


def lambda_handler(event, context):
    """Main Lambda handler function"""
    try:
        # Parse the incoming event body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No body found in request'})
            }

        event_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Validate event data
        if not validate_event_data(event_data):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        # Store event in DynamoDB
        stored_event = store_event(event_data)
        
        # Send SNS notification
        send_sns_notification(stored_event)
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Event created successfully',
                'event_id': stored_event['event_id']
            })
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except ClientError as e:
        logger.error(f"AWS service error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
