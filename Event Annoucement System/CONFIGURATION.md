# Configuration Guide

This document lists all the placeholders you need to replace with your actual AWS values.

## 🔧 Required Replacements

### 1. AWS Account Information
- **YOUR_ACCOUNT_ID**: Replace with your 12-digit AWS Account ID
- **YOUR_REGION**: Replace with your preferred AWS region (e.g., us-east-1, eu-west-1)

### 2. Cognito Configuration
- **YOUR_USER_POOL_ID**: Replace with your Cognito User Pool ID (format: us-east-1_XXXXXXXXX)
- **YOUR_CLIENT_ID**: Replace with your Cognito App Client ID

### 3. API Gateway
- **YOUR_API_GATEWAY_URL**: Replace with your API Gateway URL
  - Format: `https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod`
- **YOUR_API_ID**: Replace with your API Gateway ID (10-character string)

### 4. S3 Configuration
- **your-bucket-name**: Replace with your S3 bucket name (must be globally unique)
- **your-event-system-bucket**: Replace with your chosen bucket name

### 5. Lambda Environment Variables
Set these in your Lambda function environment variables:
- **SNS_TOPIC_ARN**: Your SNS topic ARN (optional for notifications)
- **INVITATIONS_TABLE**: Your DynamoDB invitations table name
- **FRONTEND_URL**: Your S3 website URL

## 📁 Files to Update

### Frontend Files
1. **frontend/script.js**
   - Line 47: Replace `YOUR_API_GATEWAY_URL` with your API Gateway URL
   - Line 207: Replace `YOUR_API_GATEWAY_URL` with your API Gateway URL

2. **frontend/login.html**
   - Line 15: Replace `YOUR_USER_POOL_ID` with your User Pool ID
   - Line 16: Replace `YOUR_CLIENT_ID` with your Client ID
   - Line 17: Replace `us-east-1` with your region

3. **frontend/register.html**
   - Update Cognito configuration (same as login.html)

4. **frontend/invite.html**
   - Update API Gateway URL for invitation generation

### Lambda Functions
1. **All Lambda functions**
   - Set environment variables in AWS Lambda console
   - Update region-specific configurations

2. **generateInvitation/lambda_function.py**
   - Line 25: Replace `your-bucket-name` and `YOUR_REGION` with actual values

### Deployment Scripts
1. **All AWS CLI commands**
   - Replace region references
   - Replace account ID references
   - Replace resource names

## 🚀 Quick Setup Checklist

- [ ] Replace all `YOUR_ACCOUNT_ID` with your AWS Account ID
- [ ] Replace all `YOUR_REGION` with your AWS region
- [ ] Replace all `YOUR_USER_POOL_ID` with your Cognito User Pool ID
- [ ] Replace all `YOUR_CLIENT_ID` with your Cognito Client ID
- [ ] Replace all `YOUR_API_GATEWAY_URL` with your API Gateway URL
- [ ] Replace all `your-bucket-name` with your S3 bucket name
- [ ] Set Lambda environment variables
- [ ] Update S3 bucket policy with correct bucket name
- [ ] Test all endpoints after deployment

## 🔍 How to Find Your Values

### AWS Account ID
```bash
aws sts get-caller-identity --query Account --output text
```

### Cognito User Pool ID
```bash
aws cognito-idp list-user-pools --max-items 10
```

### API Gateway ID
```bash
aws apigateway get-rest-apis --query 'items[?name==`EventAnnouncementAPI`].id' --output text
```

### S3 Bucket URL Format
`http://your-bucket-name.s3-website-YOUR_REGION.amazonaws.com`
