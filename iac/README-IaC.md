# Infrastructure as Code (CloudFormation)

This directory contains the CloudFormation templates to provision the AWS infrastructure.

## Application Architecture
- **VPC & Netorking**: Public/Private subnets across 2 AZs, NAT Gateway, Internet Gateway.
- **Compute**: ECS Fargate Cluster.
- **Load Balancing**: Application Load Balancer (ALB) public facing.
- **Security**: Security Groups, IAM Roles (Least Privilege).
- **Authentication**: Amazon Cognito User Pool integrated with ALB.
- **CI/CD**: CodePipeline (GitHub Source) -> CodeBuild (Scan & Build) -> ECS Deploy.

## Templates

| File | Description | Dependencies |
|------|-------------|--------------|
| `00-parameters.yml` | Shared configuration values | None |
| `01-network.yml` | VPC, Subnets, Security Groups | None |
| `02-cognito.yml` | User Pool, Client, Domain | 00-parameters |
| `03-ecs.yml` | ECS Cluster, Service, Task Def, ALB | 01-network, 00-parameters |
| `04-pipeline.yml` | CodePipeline, CodeBuild, ECR | 05-storage, 03-ecs (Cluster name) |
| `05-storage-notifications.yml` | S3 Artifact Bucket, SNS Topic | None |

## Deployment Order

The `scripts/deploy-stack.sh` automates this, but logically:

1. **Network** (`01-network.yml`): Sets up the base VPC.
2. **Storage** (`05-storage-notifications.yml`): Sets up Bucket for Pipeline artifacts.
3. **Cognito** (`02-cognito.yml`): Sets up Auth.
4. **ECS** (`03-ecs.yml`): Sets up runtime environment (Cluster, ALB).
5. **Pipeline** (`04-pipeline.yml`): Connects GitHub to ECS.

## Important Notes
- **HTTPS**: The ALB listener is set to 80 (HTTP) redirect or 443 (HTTPS) depending on configuration. For Cognito Auth to work on ALB, HTTPS is required. You must provide a valid Certificate ARN in `03-ecs.yml` or manually attach one after creation if you want full Cognito integration on the ALB level. The provided template assumes HTTP for simplicity unless a Certificate is available.
- **Parameters**: `00-parameters.yml` exports values used by others using `Fn::ImportValue`.
