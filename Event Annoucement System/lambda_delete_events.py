import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('events-table')  # Replace with your table name

def lambda_handler(event, context):
    try:
        # Debug: log the full incoming event
        print("DEBUG: EVENT RECEIVED")
        print(json.dumps(event))

        # Safely access pathParameters
        event_id = event.get('pathParameters', {}).get('event_id')
        if not event_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing event_id in pathParameters'})
            }

        # Delete the item from DynamoDB
        response = table.delete_item(
            Key={'event_id': event_id}
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': f'Event {event_id} deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
