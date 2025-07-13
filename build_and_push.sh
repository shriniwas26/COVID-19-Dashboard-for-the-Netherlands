#!/bin/bash
set -e

# Get AWS account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${1:-eu-north-1}
REPO_NAME=${2:-covid-dashboard}

echo "Building and pushing Docker image..."
echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo "Repository: $REPO_NAME"

# Build Docker image with correct architecture
docker build --no-cache --platform linux/amd64 -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest ..

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest

echo "Docker image built and pushed successfully!"

# Force ECS service redeployment
echo "Forcing ECS service redeployment..."
aws ecs update-service --cluster covid-dashboard-cluster --service covid-dashboard-service --force-new-deployment --region $REGION

echo "ECS service redeployment triggered!"
