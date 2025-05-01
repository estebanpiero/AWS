# Serverless Event Announcement System

A serverless web application built on AWS for managing and displaying event announcements. The solution leverages AWS Lambda, API Gateway, DynamoDB, and S3 for a scalable, maintenance-free architecture.

## ?? Architecture Overview

![Architecture Diagram]

### AWS Services Used
- **Amazon S3**: Hosts the static website (HTML, CSS, JavaScript)
- **Amazon API Gateway**: RESTful API endpoints
- **AWS Lambda**: Serverless compute for business logic
- **Amazon DynamoDB**: NoSQL database for event storage
- **AWS IAM**: Identity and access management
- **Amazon CloudWatch**: Monitoring and logging

## ?? Technical Architecture

### Frontend (S3 Static Website)
- HTML5, CSS3, and JavaScript
- Responsive design
- Hosted in S3 bucket configured for static website hosting
- CloudFront distribution for content delivery (optional)

### Backend (Serverless)
- API Gateway REST API endpoints
- Lambda functions for CRUD operations
- DynamoDB for event data persistence

### API Endpoints
GET /events - List all events
POST /events - Create new event
DELETE /events/{id} - Delete an event
GET /events/{id} - Get single event
PUT /events/{id} - Update an event


## ?? Implementation Details

### DynamoDB Schema
```json
{
  "eventId": "string (UUID)",
  "title": "string",
  "description": "string",
  "date": "string (ISO 8601)",
  "createdAt": "string (timestamp)",
  "updatedAt": "string (timestamp)"
}
```

### Lambda Functions

#### createEvent

- Creates new event in DynamoDB
- Validates input
- Generates UUID

#### listEvents

- Retrieves events from DynamoDB
- Supports pagination
- Implements filtering

#### deleteEvent

- Removes event by ID
- Validates existence

#### updateEvent

- Updates existing event
- Handles partial updates


