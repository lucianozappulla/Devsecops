#!/bin/bash
# Create test user in Cognito
# Must be run AFTER stacks are deployed

REGION="eu-south-1" # Match your region
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name devsecops-cognito --region $REGION --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text)
CLIENT_ID=$(aws cloudformation describe-stacks --stack-name devsecops-cognito --region $REGION --query "Stacks[0].Outputs[?OutputKey=='UserPoolClientId'].OutputValue" --output text)

USERNAME="testuser"
EMAIL="testuser@example.com"
PASSWORD="TempPassword123!"

echo "Creating user $USERNAME in Pool $USER_POOL_ID..."

aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username $USERNAME \
  --user-attributes Name=email,Value=$EMAIL Name=name,Value="Test User" \
  --message-action SUPPRESS \
  --region $REGION

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username $USERNAME \
  --password $PASSWORD \
  --permanent \
  --region $REGION

echo "User $USERNAME created with password $PASSWORD"
echo "You can now login via the ALB Domain."
