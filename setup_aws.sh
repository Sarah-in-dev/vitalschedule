#!/bin/bash
# Script to set up AWS infrastructure for Streamlit dashboard

# Set variables
ECR_REPOSITORY_NAME="vbc-dashboard"
APP_RUNNER_SERVICE_NAME="vbc-dashboard-service"
AWS_REGION="us-east-1"  # Change to your preferred region

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null
then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null
then
    echo "AWS credentials not configured. Please run 'aws configure'."
    exit 1
fi

# Create ECR repository if it doesn't exist
if ! aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME &> /dev/null
then
    echo "Creating ECR repository: $ECR_REPOSITORY_NAME"
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME
else
    echo "ECR repository already exists: $ECR_REPOSITORY_NAME"
fi

# Get ECR repository URI
ECR_REPOSITORY_URI=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --query 'repositories[0].repositoryUri' --output text)
echo "ECR Repository URI: $ECR_REPOSITORY_URI"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME .

# Tag Docker image
echo "Tagging Docker image..."
docker tag $ECR_REPOSITORY_NAME:latest $ECR_REPOSITORY_URI:latest

# Push Docker image to ECR
echo "Pushing Docker image to ECR..."
docker push $ECR_REPOSITORY_URI:latest

# Create IAM role for App Runner
ROLE_NAME="AppRunnerECRAccessRole"
POLICY_ARN="arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"

# Check if the role already exists
if ! aws iam get-role --role-name $ROLE_NAME &> /dev/null
then
    echo "Creating IAM role for App Runner..."
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "build.apprunner.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

    # Attach ECR access policy to the role
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn $POLICY_ARN
else
    echo "IAM role already exists: $ROLE_NAME"
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "App Runner role ARN: $ROLE_ARN"

echo "Setup complete! You can now deploy the app to App Runner."
echo ""
echo "To deploy to App Runner, use the AWS console or run the following command:"
echo "aws apprunner create-service \\"
echo "  --service-name $APP_RUNNER_SERVICE_NAME \\"
echo "  --source-configuration '{\"AuthenticationConfiguration\":{\"AccessRoleArn\":\"$ROLE_ARN\"},\"AutoDeploymentsEnabled\":true,\"ImageRepository\":{\"ImageIdentifier\":\"$ECR_REPOSITORY_URI:latest\",\"ImageConfiguration\":{\"Port\":\"8501\"},\"ImageRepositoryType\":\"ECR\"}}'"
echo ""
echo "Note: The App Runner service creation might take a few minutes."
