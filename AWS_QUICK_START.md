# AWS Quick Start Guide

Simple steps to deploy your COVID-19 Dashboard to AWS Elastic Beanstalk.

## 🚀 Prerequisites

### 1. Install Required Tools

**macOS:**

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Install Terraform
brew install terraform

# Install EB CLI
pip install awsebcli
```

**Linux:**

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# Install EB CLI
pip install awsebcli
```

### 2. Configure AWS Credentials

```bash
aws configure
```

You'll need to enter:

- **AWS Access Key ID**: From your AWS account
- **AWS Secret Access Key**: From your AWS account
- **Default region**: `us-east-1` (recommended)
- **Default output format**: `json`

## 🎯 Deploy to AWS

### Step 1: Run the Deployment Script

```bash
# Make the script executable
chmod +x aws-deploy.sh

# Deploy everything
./aws-deploy.sh deploy
```

This will:

1. ✅ Check prerequisites
2. ✅ Deploy AWS infrastructure with Terraform
3. ✅ Create Elastic Beanstalk application
4. ✅ Deploy your dashboard
5. ✅ Provide you with the URL

### Step 2: Access Your Dashboard

After deployment completes, you'll see a URL like:

```
http://covid-dashboard-nl-env.region.elasticbeanstalk.com
```

Open this URL in your browser to see your live dashboard!

## 🔧 Useful Commands

```bash
# Check deployment status
./aws-deploy.sh status

# View application logs
./aws-deploy.sh logs

# Destroy infrastructure (when done)
./aws-deploy.sh destroy
```

## 💰 Cost Information

**Free Tier (12 months):**

- ✅ **EC2 t2.micro**: 750 hours/month (free)
- ✅ **Elastic Beanstalk**: Free
- ✅ **S3**: 5GB storage (free)
- ✅ **CloudWatch**: 5GB data (free)

**After Free Tier:**

- **Monthly cost**: ~$9.32
- **Includes**: EC2, S3, CloudWatch, data transfer

## 🐛 Troubleshooting

### Common Issues:

**1. AWS Credentials Error**

```bash
# Reconfigure AWS credentials
aws configure
```

**2. Terraform Error**

```bash
# Reinitialize Terraform
cd terraform
terraform init
cd ..
```

**3. EB CLI Error**

```bash
# Reinstall EB CLI
pip install --upgrade awsebcli
```

**4. Application Won't Start**

```bash
# Check logs
./aws-deploy.sh logs

# SSH into instance (if needed)
eb ssh
```

## 📞 Need Help?

- **AWS Documentation**: [docs.aws.amazon.com](https://docs.aws.amazon.com)
- **Elastic Beanstalk**: [docs.aws.amazon.com/elasticbeanstalk](https://docs.aws.amazon.com/elasticbeanstalk)
- **GitHub Issues**: Open an issue in your repository

---

**Your COVID-19 Dashboard will be live on AWS in about 15 minutes! 🎉**
