#!binbash

# Event Announcement System Deployment Script
# Replace all placeholder values before running this script

# Configuration - REPLACE THESE VALUES
REGION=us-east-1  # Replace with your preferred region
ACCOUNT_ID=YOUR_ACCOUNT_ID  # Replace with your AWS Account ID
BUCKET_NAME=your-event-system-bucket  # Replace with your unique bucket name

echo 🚀 Starting Event Announcement System deployment...

# Step 1 Create Cognito User Pool
echo 📝 Creating Cognito User Pool...
USER_POOL_ID=$(aws cognito-idp create-user-pool 
    --pool-name EventAnnouncementUserPool 
    --policies '{
        PasswordPolicy {
            MinimumLength 8,
            RequireUppercase true,
            RequireLowercase true,
            RequireNumbers true,
            RequireSymbols false
        }
    }' 
    --auto-verified-attributes email 
    --region $REGION 
    --query 'UserPool.Id' --output text)

echo ✅ User Pool created $USER_POOL_ID

# Step 2 Create User Pool Client
echo 📝 Creating User Pool Client...
CLIENT_ID=$(aws cognito-idp create-user-pool-client 
    --user-pool-id $USER_POOL_ID 
    --client-name EventAnnouncementWebClient 
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH 
    --region $REGION 
    --query 'UserPoolClient.ClientId' --output text)

echo ✅ Client created $CLIENT_ID

# Step 3 Create DynamoDB Tables
echo 📝 Creating DynamoDB tables...
aws dynamodb create-table 
    --table-name events-table 
    --attribute-definitions AttributeName=id,AttributeType=S 
    --key-schema AttributeName=id,KeyType=HASH 
    --billing-mode PAY_PER_REQUEST 
    --region $REGION

aws dynamodb create-table 
    --table-name invitations-table 
    --attribute-definitions AttributeName=token,AttributeType=S 
    --key-schema AttributeName=token,KeyType=HASH 
    --billing-mode PAY_PER_REQUEST 
    --region $REGION

echo ✅ DynamoDB tables created

# Step 4 Create SNS Topic
echo 📝 Creating SNS topic...
SNS_TOPIC_ARN=$(aws sns create-topic 
    --name EventAnnouncementTopic 
    --region $REGION 
    --query 'TopicArn' --output text)

echo ✅ SNS topic created $SNS_TOPIC_ARN

# Step 5 Create S3 Bucket
echo 📝 Creating S3 bucket...
aws s3 mb s3$BUCKET_NAME --region $REGION

aws s3api put-bucket-website 
    --bucket $BUCKET_NAME 
    --website-configuration '{
        IndexDocument {Suffix index.html},
        ErrorDocument {Key error.html}
    }'

aws s3api put-bucket-policy 
    --bucket $BUCKET_NAME 
    --policy {
        Version 2012-10-17,
        Statement [{
            Sid PublicReadGetObject,
            Effect Allow,
            Principal ,
            Action s3GetObject,
            Resource arnawss3$BUCKET_NAME
        }]
    }

echo ✅ S3 bucket created and configured

# Display configuration values
echo 
echo 🎉 Deployment completed! Update your configuration files with these values
echo 
echo USER_POOL_ID $USER_POOL_ID
echo CLIENT_ID $CLIENT_ID
echo SNS_TOPIC_ARN $SNS_TOPIC_ARN
echo BUCKET_NAME $BUCKET_NAME
echo WEBSITE_URL http$BUCKET_NAME.s3-website-$REGION.amazonaws.com
echo 
echo 📋 Next steps
echo 1. Update frontendscript.js with your API Gateway URL
echo 2. Update frontendlogin.html with Cognito configuration
echo 3. Deploy Lambda functions with environment variables
echo 4. Create and configure API Gateway
echo 5. Upload frontend files to S3
