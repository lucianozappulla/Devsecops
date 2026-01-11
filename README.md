# DevSecOps Pipeline Demo on AWS

This project demonstrates a complete DevSecOps pipeline using AWS native services.

## Overview

The pipeline automates the delivery of a secure Python Flask application to Amazon ECS Fargate.
It includes:
- **Source**: GitHub
- **Build & Scan**: AWS CodeBuild (Semgrep, Checkov, Trivy)
- **Deploy**: AWS CodePipeline -> ECS Fargate
- **Auth**: Amazon Cognito
- **Infrastructure**: CloudFormation (YAML)

## Prerequisities

1. **AWS Account** with permissions to create resources (VPC, ECS, IAM, etc).
2. **AWS CLI v2** installed and configured (`aws configure`).
3. **GitHub Repository** containing this code.
4. **GitHub Personal Access Token** (Classic) with `repo` and `admin:repo_hook` scopes.

## Setup Instructions

### 1. Clone & Push
Push this repository to your own GitHub account:
```bash
git remote set-url origin https://github.com/<YOUR_USER>/devsecops-pipeline-demo.git
git push -u origin main
```

### 2. Deploy Infrastructure
Open `scripts/deploy-stack.sh` and update:
- `REGION` (default: eu-south-1)
- `GITHUB_TOKEN` (replace with your token)

Run the deployment script:
```bash
cd scripts
bash deploy-stack.sh
```
*This will take approximately 10-15 minutes.*

### 3. Create Test User
Create a user in Cognito to log in:
```bash
bash create-cognito-user.sh
```
This creates user `testuser` with password `TempPassword123!`.

### 4. Verify Pipeline
Modify `README.md` or any file and push to GitHub:
```bash
bash invoke-pipeline.sh
```
Go to the AWS Console -> **CodePipeline** and watch the `devsecops-pipeline` run.

### 5. Access Application
Get the ALB DNS Name from CloudFormation outputs (Stack: `devsecops-ecs`) or via console.
Open `https://<ALB-DNS-NAME>` (or http if no cert configured).
1. You will be redirected to Cognito.
2. Login with `testuser`.
3. You will be redirected back to the app.

### API Endpoints
- `GET /health` (Public)
- `GET /profile` (Protected)
- `POST /orders` (Protected) - JSON Body: `{"item": "X", "quantity": 1}`

## Cleanup
To remove all resources and avoid costs:
1. Delete the files in the S3 Artifact Bucket.
2. Delete the ECR images.
3. Delete stacks in reverse order (Pipeline -> ECS -> Cognito -> Storage -> Network).
