import json
import boto3
import os
from typing import Dict, Any, List
from botocore.exceptions import ClientError

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')

# Get environment variables with default values
TABLE_NAME = os.environ.get('TABLE_NAME', 'events-table')
MAX_ITEMS = int(os.environ.get('MAX_ITEMS', '100'))

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to create standardized response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps(body)
    }

def get_events_from_dynamodb(table, last_evaluated_key: Dict = None) -> List[Dict]:
    """Helper function to get events from DynamoDB with pagination"""
    scan_params = {
        'Limit': MAX_ITEMS
    }
    if last_evaluated_key:
        scan_params['ExclusiveStartKey'] = last_evaluated_key

    return table.scan(**scan_params)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler to get all events from DynamoDB"""
    print(f"Received event: {json.dumps(event)}")
    print(f"Using table name: {TABLE_NAME}")

    try:
        table = dynamodb.Table(TABLE_NAME)
        items = []
        last_evaluated_key = None

        try:
            # Get items with pagination
            while True:
                response = get_events_from_dynamodb(table, last_evaluated_key)
                items.extend(response.get('Items', []))

                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key or len(items) >= MAX_ITEMS:
                    break

            # Sort events by date
            items.sort(key=lambda x: x.get('date', ''))

            print(f"Retrieved {len(items)} items from DynamoDB")

            return create_response(200, items)

        except ClientError as e:
            print(f"DynamoDB error: {str(e)}")
            error_code = e.response['Error']['Code']
            status_code = 400 if error_code in ['ValidationException', 'ConditionalCheckFailedException'] else 500

            return create_response(status_code, {
                'error': 'DynamoDB error',
                'message': str(e),
                'code': error_code
            })

    except Exception as e:
        print(f"Error getting events: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })
