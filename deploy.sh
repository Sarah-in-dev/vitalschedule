#!/bin/bash
# Script to build and deploy the Streamlit dashboard to AWS App Runner

# Set variables
ECR_REPOSITORY_NAME="vbc-dashboard"
IMAGE_TAG="latest"
AWS_REGION="us-east-1"  # Change to your preferred region

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print step messages
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Function to print error messages and exit
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null
then
    print_error "AWS CLI is not installed. Please install it first."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    print_error "Docker is not installed. Please install it first."
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null
then
    print_error "AWS credentials not configured. Please run 'aws configure'."
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_info "AWS Account ID: $AWS_ACCOUNT_ID"

# Get ECR repository URI
ECR_REPOSITORY_URI=$(aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --query 'repositories[0].repositoryUri' --output text)

if [ -z "$ECR_REPOSITORY_URI" ]; then
    print_error "ECR repository not found. Please run setup_aws.sh first."
fi

print_info "ECR Repository URI: $ECR_REPOSITORY_URI"

# Login to ECR
print_step "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

if [ $? -ne 0 ]; then
    print_error "Failed to log in to ECR."
fi

# Create a directory structure if it doesn't exist
print_step "Creating directory structure..."
mkdir -p value_based/dashboard

# Prepare dashboard files
print_step "Checking dashboard files..."

# Check if file exists in the expected location 
if [ ! -f "value_based/dashboards/vbc_dashboard.py" ]; then
    print_info "Dashboard file not found at value_based/dashboards/vbc/vbc_dashboard.py. Please copy your dashboard.py"
    exit 1
fi

# Build Docker image
print_step "Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

if [ $? -ne 0 ]; then
    print_error "Docker build failed."
fi

# Tag Docker image
print_step "Tagging Docker image..."
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $ECR_REPOSITORY_URI:$IMAGE_TAG

# Push Docker image to ECR
print_step "Pushing Docker image to ECR..."
docker push $ECR_REPOSITORY_URI:$IMAGE_TAG

if [ $? -ne 0 ]; then
    print_error "Failed to push image to ECR."
fi

print_info "Image pushed successfully: $ECR_REPOSITORY_URI:$IMAGE_TAG"

# Check if App Runner service exists and needs to be updated
APP_RUNNER_SERVICE_NAME="vbc-dashboard-service"
if aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$APP_RUNNER_SERVICE_NAME']" --output text | grep -q $APP_RUNNER_SERVICE_NAME; then
    print_step "App Runner service already exists. A new deployment will be triggered automatically."
    print_info "You can check the deployment status in the AWS App Runner console."
else
    print_info "App Runner service not found. To create it, run:"
    echo "aws apprunner create-service \\"
    echo "  --service-name $APP_RUNNER_SERVICE_NAME \\"
    echo "  --source-configuration '{\"AuthenticationConfiguration\":{\"AccessRoleArn\":\"ROLE_ARN\"},\"AutoDeploymentsEnabled\":true,\"ImageRepository\":{\"ImageIdentifier\":\"$ECR_REPOSITORY_URI:latest\",\"ImageConfiguration\":{\"Port\":\"8501\"},\"ImageRepositoryType\":\"ECR\"}}'"
    echo ""
    echo "Replace ROLE_ARN with the ARN of your AppRunnerECRAccessRole"
fi

print_step "Deployment complete!"
