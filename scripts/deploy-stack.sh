#!/bin/bash
# Deploy all CloudFormation templates in order
# PREREQUISITE: Configure AWS CLI with 'aws configure'
# PREREQUISITE: Generate a GitHub OAuth Token (classic) with 'repo' and 'admin:repo_hook' scope

REGION="eu-south-1"  # CHANGE THIS IF NEEDED
STACK_PREFIX="devsecops"
GITHUB_TOKEN="CHANGE_ME_TO_YOUR_TOKEN" # Recommend passing this as env var or argument safely

echo "Deploying Stacks to region $REGION..."

# 1. Network
echo "Deploying Network Stack..."
aws cloudformation create-stack \
  --stack-name ${STACK_PREFIX}-network \
  --template-body file://iac/01-network.yml \
  --region $REGION
echo "Network stack creation initiated. Waiting..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_PREFIX}-network --region $REGION
echo "Network Stack Deployed."

# 2. Storage & Notifications (Dependencies for Pipeline)
# Moved to step 2 because Pipeline stack references the Bucket and Topic
echo "Deploying Storage & Notifications Stack..."
aws cloudformation create-stack \
  --stack-name ${STACK_PREFIX}-storage \
  --template-body file://iac/05-storage-notifications.yml \
  --region $REGION
echo "Storage stack creation initiated. Waiting..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_PREFIX}-storage --region $REGION
echo "Storage Stack Deployed."

# 3. Cognito
echo "Deploying Cognito Stack..."
aws cloudformation create-stack \
  --stack-name ${STACK_PREFIX}-cognito \
  --template-body file://iac/02-cognito.yml \
  --region $REGION
echo "Cognito stack creation initiated. Waiting..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_PREFIX}-cognito --region $REGION
echo "Cognito Stack Deployed."

# 4. ECS (Depends on Network. Pipeline deploys to it, but it can exist empty first or we create it here)
# This stack creates Cluster, ALB, TaskDef, Service
echo "Deploying ECS Stack..."
aws cloudformation create-stack \
  --stack-name ${STACK_PREFIX}-ecs \
  --template-body file://iac/03-ecs.yml \
  --region $REGION \
  --capabilities CAPABILITY_NAMED_IAM
echo "ECS stack creation initiated. Waiting..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_PREFIX}-ecs --region $REGION
echo "ECS Stack Deployed."

# 5. Pipeline
echo "Deploying Pipeline Stack..."
aws cloudformation create-stack \
  --stack-name ${STACK_PREFIX}-pipeline \
  --template-body file://iac/04-pipeline.yml \
  --parameters ParameterKey=GitHubToken,ParameterValue=$GITHUB_TOKEN \
  --region $REGION \
  --capabilities CAPABILITY_NAMED_IAM
echo "Pipeline stack creation initiated. Waiting..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_PREFIX}-pipeline --region $REGION
echo "Pipeline Stack Deployed."

echo "All Stacks Deployed Successfully!"
echo "Next Steps:"
echo "1. Run './scripts/create-cognito-user.sh' to create a test user."
echo "2. Push code to your GitHub repo to trigger the pipeline."
