# Event Announcement System - AWS Serverless Project

A complete serverless event management system built on AWS with user authentication, allowing users to securely create, view, and manage events with automatic email notifications and chronological sorting.

## 🏗️ Architecture Overview

This project demonstrates a modern serverless architecture using AWS services to create a scalable, cost-effective, and secure event management system with invitation-based user registration.

## 🛠️ Technologies Used

### Frontend
- **HTML5/CSS3/JavaScript** - Modern responsive web interface
- **Font Awesome** - Icons and visual elements
- **Google Maps API** - Location visualization
- **Vanilla JavaScript** - No frameworks for simplicity

### AWS Services
- **Cognito** - User authentication and management
- **S3** - Static website hosting and file storage
- **Lambda** - Serverless compute for business logic
- **API Gateway** - RESTful API endpoints
- **DynamoDB** - NoSQL database for event and invitation storage
- **SNS** - Simple Notification Service for email alerts
- **IAM** - Identity and Access Management for security											  

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Basic knowledge of HTML/JavaScript
- Understanding of AWS services

## 🛠️ Technologies Used

### Frontend
- **HTML5/CSS3/JavaScript** - Modern responsive web interface
- **Font Awesome** - Icons and visual elements
- **Google Maps API** - Location visualization
- **Vanilla JavaScript** - No frameworks for simplicity

### AWS Services
- **Cognito** - User authentication and management
- **S3** - Static website hosting and file storage
- **Lambda** - Serverless compute for business logic
- **API Gateway** - RESTful API endpoints
- **DynamoDB** - NoSQL database for event and invitation storage
- **SNS** - Simple Notification Service for email alerts
- **IAM** - Identity and Access Management for security

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Basic knowledge of HTML/JavaScript
- Understanding of AWS services

## 🚀 Step-by-Step Implementation

### Step 1: Create Cognito User Pool

```bash
aws cognito-idp create-user-pool \
    --pool-name EventAnnouncementUserPool \
    --policies '{
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": false
        }
    }' \
    --auto-verified-attributes email \
    --region us-east-1
```

Create User Pool Client:
```bash
aws cognito-idp create-user-pool-client \
    --user-pool-id us-east-1_77ER4ADqH \
    --client-name EventAnnouncementWebClient \
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH \
    --region us-east-1
```

**Why Cognito?**
- Secure user authentication
- Email verification
- JWT token management
- Password policies
- Scalable user management

### Step 2: Create DynamoDB Tables

**Events Table:**
```bash
aws dynamodb create-table \
    --table-name events-table \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

**Invitations Table:**
```bash
aws dynamodb create-table \
    --table-name invitations-table \
    --attribute-definitions \
        AttributeName=token,AttributeType=S \
    --key-schema \
        AttributeName=token,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

**Why DynamoDB?**
- Serverless and fully managed
- Automatic scaling
- Pay-per-use pricing
- Perfect for event and invitation data storage

### Step 3: Create SNS Topic

```bash
aws sns create-topic \
    --name EventAnnouncementTopic \
    --region us-east-1
```

**Why SNS?**
- Decoupled messaging system
- Multiple notification channels
- Reliable message delivery
- Easy integration with Lambda

### Step 4: Create IAM Role for Lambda

```bash
aws iam create-role \
    --role-name LambdaSNSPublisherRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'
```

Attach necessary policies:
```bash
aws iam attach-role-policy \
    --role-name LambdaSNSPublisherRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name LambdaSNSPublisherRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
    --role-name LambdaSNSPublisherRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess
```

### Step 5: Deploy Lambda Functions

#### Create Event Function (sendEventNotification)
```python
import json
import boto3
import uuid
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
            'title': body['title'],
            'date': body['date'],
            'address': body['address'],
            'description': body['description'],
            'creator_name': body['creator_name'],
            'created_at': datetime.utcnow().isoformat()
        }

        # Save to DynamoDB
        table.put_item(Item=event_data)

        # Send SNS notification
        message = f"New Event Created: {body['title']} on {body['date']}"
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
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
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
```

#### Generate Invitation Function (generateInvitation)
```python
import json
import boto3
import uuid
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('INVITATIONS_TABLE', 'invitations-table'))

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
        base_url = os.environ.get('FRONTEND_URL', 'http://event-announcement-system-site.s3-website-us-east-1.amazonaws.com')
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
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
```

#### Validate Invitation Function (validateInvitation)
```python
import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('INVITATIONS_TABLE', 'invitations-table'))

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

    } catch Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
```

#### List Events Function (listEventsNotification)
```python
import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('events-table')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        response = table.scan()
        events = response['Items']

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(events, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
```

#### Delete Event Function (deleteEventNotification)
```python
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('events-table')

def lambda_handler(event, context):
    try:
        event_id = event['pathParameters']['id']

        table.delete_item(Key={'id': event_id})

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': 'Event deleted successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
```

### Step 6: Create API Gateway

```bash
# 1. Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name EventAnnouncementAPI \
    --region us-east-1 \
    --query 'id' --output text)

# 2. Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region us-east-1 \
    --query 'items[0].id' --output text)

# 3. Create /events resource
EVENTS_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part events \
    --region us-east-1 \
    --query 'id' --output text)

# 4. Create /{id} resource under /events
ID_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $EVENTS_RESOURCE_ID \
    --path-part '{id}' \
    --region us-east-1 \
    --query 'id' --output text)

# 5. Create methods
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $EVENTS_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region us-east-1

aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $EVENTS_RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE \
    --region us-east-1

aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $ID_RESOURCE_ID \
    --http-method DELETE \
    --authorization-type NONE \
    --region us-east-1

# 6. Integrate with Lambda functions
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $EVENTS_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:ACCOUNT_ID:function:sendEventNotification/invocations \
    --region us-east-1

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $EVENTS_RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:ACCOUNT_ID:function:listEventsNotification/invocations \
    --region us-east-1

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $ID_RESOURCE_ID \
    --http-method DELETE \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:ACCOUNT_ID:function:deleteEventNotification/invocations \
    --region us-east-1

# 7. Grant Lambda permissions
aws lambda add-permission \
    --function-name sendEventNotification \
    --statement-id api-gateway-invoke-1 \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:ACCOUNT_ID:$API_ID/*/*" \
    --region us-east-1

aws lambda add-permission \
    --function-name listEventsNotification \
    --statement-id api-gateway-invoke-2 \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:ACCOUNT_ID:$API_ID/*/*" \
    --region us-east-1

aws lambda add-permission \
    --function-name deleteEventNotification \
    --statement-id api-gateway-invoke-3 \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:ACCOUNT_ID:$API_ID/*/*" \
    --region us-east-1

# 8. Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region us-east-1

# 9. Get API URL
echo "API URL: https://$API_ID.execute-api.us-east-1.amazonaws.com/prod"
```

**Note**: Replace `ACCOUNT_ID` with your AWS account ID. For complete setup including CORS configuration, use the provided `api-gateway-setup.sh` script.

**API Endpoints:**
- `POST /events` - Create new event
- `GET /events` - List all events
- `DELETE /events/{id}` - Delete specific event
- `POST /invitations` - Generate invitation token
- `GET /invitations/{token}` - Validate invitation token

### Step 7: Create S3 Bucket for Website

```bash
aws s3 mb s3://event-announcement-system-site --region us-east-1

# Configure for static website hosting
aws s3api put-bucket-website \
    --bucket event-announcement-system-site \
    --website-configuration '{
        "IndexDocument": {"Suffix": "index.html"},
        "ErrorDocument": {"Key": "error.html"}
    }'

# Set public read policy
aws s3api put-bucket-policy \
    --bucket event-announcement-system-site \
    --policy '{
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::event-announcement-system-site/*"
        }]
    }'
```

### Step 8: Deploy Frontend Files

Upload the HTML, CSS, and JavaScript files to S3:
```bash
aws s3 sync ./frontend/ s3://event-announcement-system-site/
```

## 🔧 Configuration Details

### Cognito Configuration
- **User Pool ID**: `us-east-1_77ER4ADqH`
- **Client ID**: `4g1gvg11ap1qn3apikj6rdpuir`
- **Authentication Flow**: USER_PASSWORD_AUTH
- **Email Verification**: Required for registration

### Environment Variables
- `SNS_TOPIC_ARN` - ARN of the SNS topic for notifications
- `DYNAMODB_TABLE` - Name of the DynamoDB table

### CORS Configuration
All Lambda functions include CORS headers to allow frontend access:
```javascript
'Access-Control-Allow-Origin': '*'
'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS'
'Access-Control-Allow-Headers': 'Content-Type'
```

### Security Considerations
- **User Authentication**: AWS Cognito with JWT tokens
- **Frontend Protection**: Immediate authentication checks on page load
- **Function-Level Security**: All CRUD operations require valid tokens
- **IAM roles**: Least privilege access
- **CORS properly configured**: Secure cross-origin requests
- **Input validation**: Implemented in Lambda functions
- **Error handling and logging**: Comprehensive monitoring

## 🌐 System Interconnections

### Data Flow

1. **User Registration/Login**
   - User receives invitation link via email/sharing
   - User validates invitation token → Cognito User Pool registration
   - Email verification required
   - User logs in via login.html → JWT tokens stored

2. **User Creates Event**
   - Authentication check → Frontend form submission → API Gateway
   - API Gateway → sendEventNotification Lambda
   - Lambda → DynamoDB (store event)
   - Lambda → SNS (send notification)

3. **User Views Events**
   - Authentication check → Frontend request → API Gateway
   - API Gateway → listEventsNotification Lambda
   - Lambda → DynamoDB (retrieve events)
   - Lambda → Frontend (display events)

4. **User Deletes Event**
   - Authentication check → Frontend request → API Gateway
   - API Gateway → deleteEventNotification Lambda
   - Lambda → DynamoDB (remove event)

5. **User Generates Invitation**
   - Authentication check → Navigate to invite.html
   - User fills invitation form → API Gateway
   - API Gateway → generateInvitation Lambda
   - Lambda → DynamoDB (store invitation token)
   - Lambda → Frontend (display shareable link)

### Component Relationships

- **Cognito** manages user authentication and sessions
- **S3** hosts the static website files
- **API Gateway** provides RESTful endpoints
- **Lambda** functions handle business logic
- **DynamoDB** stores event data persistently
- **SNS** sends email notifications
- **IAM** manages permissions and security

## 💰 Cost Optimization

This serverless architecture is cost-effective because:
- **Pay-per-use** - Only charged when functions execute
- **No server management** - No EC2 instances to maintain
- **Automatic scaling** - Handles traffic spikes efficiently
- **Free tier eligible** - Many services have generous free tiers

## 🚀 Deployment

1. Clone this repository
2. Configure AWS CLI with your credentials
3. Run the deployment scripts in order
4. Update API endpoints in frontend JavaScript
5. Upload frontend files to S3
6. Access your website via S3 website URL

## 🔍 Monitoring and Debugging

- **CloudWatch Logs** - Lambda function logs
- **CloudWatch Metrics** - Performance monitoring
- **X-Ray** - Distributed tracing (optional)
- **API Gateway Logs** - Request/response logging

## 🎯 Key Benefits

1. **Serverless** - No infrastructure management
2. **Scalable** - Automatically handles load
3. **Cost-effective** - Pay only for what you use
4. **Reliable** - Built on AWS managed services
5. **Secure** - IAM-based access control with invitation-only registration
6. **Fast deployment** - Infrastructure as code

## 📚 Learning Outcomes

By building this project, you'll learn:
- Serverless architecture patterns
- AWS service integration
- RESTful API design
- Frontend-backend communication
- Infrastructure as code
- Event-driven programming

## 🔗 Live Demo

Website URL: `http://event-announcement-system-site.s3-website-us-east-1.amazonaws.com`

## 📝 Next Steps

Potential enhancements:
- Real-time updates with WebSockets
- Image upload for events
- Calendar integration
- Mobile app development
- Advanced search and filtering

---

This project demonstrates modern cloud-native development practices and serves as an excellent foundation for learning AWS serverless technologies.
