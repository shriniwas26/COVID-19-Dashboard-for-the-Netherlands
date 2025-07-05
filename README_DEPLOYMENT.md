# COVID-19 Dashboard - ECS Deployment Guide

This guide will help you deploy the COVID-19 Dashboard for the Netherlands on AWS ECS with a public-facing URL in the eu-north-1 region.

## 🏗️ Architecture Overview

- **ECS Fargate**: Serverless container orchestration
- **Application Load Balancer**: Public-facing load balancer
- **ECR**: Container registry for Docker images
- **VPC**: Isolated network with public/private subnets
- **CloudWatch**: Logging and monitoring

## 📋 Prerequisites

1. **AWS CLI** installed and configured
2. **Docker** installed
3. **Terraform** installed (version >= 1.0)
4. **AWS Account** with appropriate permissions

## 🚀 Quick Deployment

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd COVID-19-Dashboard-for-the-Netherlands

# Make the deployment script executable
chmod +x deploy.sh
```

### 2. Deploy Infrastructure

```bash
# Run the automated deployment script
./deploy.sh
```

This script will:

- Initialize Terraform
- Deploy all AWS infrastructure
- Build and push Docker image to ECR
- Deploy the application to ECS
- Provide you with the public URL

## 🔧 Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### Step 1: Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -out=tfplan

# Apply the infrastructure
terraform apply tfplan
```

### Step 2: Build and Push Docker Image

```bash
# Get ECR repository URL
ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="eu-north-1"

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build Docker image
docker build -t covid-dashboard .

# Tag and push to ECR
docker tag covid-dashboard:latest ${ECR_REPO_URL}:latest
docker push ${ECR_REPO_URL}:latest
```

### Step 3: Deploy Application

```bash
# Update ECS service to use new image
aws ecs update-service --cluster covid-dashboard-cluster --service covid-dashboard-service --force-new-deployment --region ${AWS_REGION}

# Wait for deployment to complete
aws ecs wait services-stable --cluster covid-dashboard-cluster --services covid-dashboard-service --region ${AWS_REGION}
```

### Step 4: Access Your Application

```bash
# Get the public URL
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "Your application is available at: http://${ALB_DNS}"
```

## 📊 Monitoring and Logs

### View Application Logs

```bash
# Get log group name
aws logs describe-log-groups --log-group-name-prefix "/ecs/covid-dashboard" --region ${AWS_REGION}

# View recent logs
aws logs tail /ecs/covid-dashboard --follow --region ${AWS_REGION}
```

### Monitor ECS Service

```bash
# Check service status
aws ecs describe-services --cluster covid-dashboard-cluster --services covid-dashboard-service --region ${AWS_REGION}

# Check task status
aws ecs list-tasks --cluster covid-dashboard-cluster --service-name covid-dashboard-service --region ${AWS_REGION}
```

## 🔄 Updating the Application

To update your application with new code:

1. **Build new Docker image**:

   ```bash
   docker build -t covid-dashboard .
   docker tag covid-dashboard:latest ${ECR_REPO_URL}:latest
   docker push ${ECR_REPO_URL}:latest
   ```

2. **Update ECS service**:
   ```bash
   aws ecs update-service --cluster covid-dashboard-cluster --service covid-dashboard-service --force-new-deployment --region ${AWS_REGION}
   ```

## 🧹 Cleanup

To remove all resources:

```bash
cd terraform
terraform destroy
```

## 🔒 Security Features

- **Non-root user**: Application runs as non-root user
- **Private subnets**: ECS tasks run in private subnets
- **Security groups**: Restrictive firewall rules
- **IAM roles**: Least privilege access

## 💰 Cost Optimization

- **Fargate Spot**: Use spot instances for cost savings
- **Auto Scaling**: Scale based on demand
- **CloudWatch**: Monitor resource usage

## 🐛 Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile and requirements.txt
2. **Service won't start**: Check ECS task logs
3. **Health check fails**: Verify application responds on port 8080
4. **Image pull fails**: Ensure ECR login and permissions

### Useful Commands

```bash
# Check ECS task logs
aws logs describe-log-streams --log-group-name /ecs/covid-dashboard --region ${AWS_REGION}

# Describe ECS service
aws ecs describe-services --cluster covid-dashboard-cluster --services covid-dashboard-service --region ${AWS_REGION}

# Check ALB health
aws elbv2 describe-target-health --target-group-arn $(terraform output -raw target_group_arn) --region ${AWS_REGION}
```

## 📈 Scaling

The application is configured with:

- **2 desired tasks** for high availability
- **Auto scaling** based on CPU/memory usage
- **Load balancer** for traffic distribution

To scale manually:

```bash
aws ecs update-service --cluster covid-dashboard-cluster --service covid-dashboard-service --desired-count 4 --region ${AWS_REGION}
```

## 🎯 Next Steps

1. **Set up monitoring**: Configure CloudWatch alarms
2. **Add HTTPS**: Configure SSL certificate
3. **Custom domain**: Set up Route 53
4. **CI/CD**: Automate deployments with GitHub Actions

Your COVID-19 Dashboard is now running on AWS ECS with a public URL! 🎉
