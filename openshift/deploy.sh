#!/bin/bash
# Quick deployment script for ySEal on OpenShift
#
# Usage: ./deploy.sh [PROJECT_NAME] [GIT_REPO] [GIT_BRANCH] [STORAGE_CLASS]
#
# Examples:
#   ./deploy.sh
#   ./deploy.sh yseal-prod
#   ./deploy.sh yseal https://github.com/MrMEEE/yseal.git main nfs-backup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configuration
PROJECT_NAME="${1:-yseal}"
GIT_REPO="${2:-https://github.com/MrMEEE/yseal.git}"
GIT_BRANCH="${3:-main}"
STORAGE_CLASS="${4}"

echo -e "${GREEN}=== ySEal OpenShift Deployment ===${NC}"
echo ""
echo "Project Name: $PROJECT_NAME"
echo "Git Repository: $GIT_REPO"
echo "Git Branch: $GIT_BRANCH"
if [ -n "$STORAGE_CLASS" ]; then
    echo "Storage Class: $STORAGE_CLASS"
else
    echo "Storage Class: (using cluster default)"
fi
echo ""

# Check if oc is installed
if ! command -v oc &> /dev/null; then
    echo -e "${RED}Error: oc CLI is not installed${NC}"
    echo "Please install the OpenShift CLI: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html"
    exit 1
fi

# Check if logged in
if ! oc whoami &> /dev/null; then
    echo -e "${RED}Error: Not logged in to OpenShift${NC}"
    echo "Please login first: oc login <cluster-url>"
    exit 1
fi

echo -e "${YELLOW}Current user:${NC} $(oc whoami)"
echo -e "${YELLOW}Current server:${NC} $(oc whoami --show-server)"
echo ""

# Create project
echo -e "${GREEN}Creating project...${NC}"
if oc get project $PROJECT_NAME &> /dev/null; then
    echo -e "${YELLOW}Project $PROJECT_NAME already exists, using existing project${NC}"
    oc project $PROJECT_NAME
else
    oc new-project $PROJECT_NAME --display-name="ySEal - Security Enhanced Architecture Library"
fi

echo ""
echo -e "${GREEN}Deploying application from template...${NC}"

# Generate random passwords
DJANGO_SECRET=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
DB_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/")
REDIS_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/")

# Determine template path
TEMPLATE_PATH="$SCRIPT_DIR/template.yaml"

# Build the oc process command
PROCESS_CMD="oc process -f \"$TEMPLATE_PATH\" \
    -p APP_NAME=$PROJECT_NAME \
    -p GIT_REPOSITORY=$GIT_REPO \
    -p GIT_BRANCH=$GIT_BRANCH \
    -p PYTHON_VERSION=3.12-ubi9 \
    -p DJANGO_SECRET_KEY=\"$DJANGO_SECRET\" \
    -p DATABASE_PASSWORD=\"$DB_PASSWORD\" \
    -p REDIS_PASSWORD=\"$REDIS_PASSWORD\""

# Add storage class if provided
if [ -n "$STORAGE_CLASS" ]; then
    PROCESS_CMD="$PROCESS_CMD -p STORAGE_CLASS=$STORAGE_CLASS"
fi

# Execute the command
eval "$PROCESS_CMD" | oc apply -f -

echo ""
echo -e "${GREEN}Starting build...${NC}"
oc start-build $PROJECT_NAME

echo ""
echo -e "${YELLOW}Build started. Monitor progress with:${NC}"
echo "  oc logs -f bc/$PROJECT_NAME"
echo ""
echo -e "${YELLOW}Check deployment status with:${NC}"
echo "  oc get pods"
echo ""
echo -e "${YELLOW}Once deployment is complete, get the application URL with:${NC}"
echo "  oc get route $PROJECT_NAME"
echo ""
echo -e "${GREEN}Deployment initiated successfully!${NC}"
echo ""
echo -e "${YELLOW}Important credentials (save these):${NC}"
echo "  Database Password: $DB_PASSWORD"
echo "  Redis Password: $REDIS_PASSWORD"
echo ""
echo -e "${YELLOW}After deployment completes, create a superuser:${NC}"
echo "  POD=\$(oc get pods -l name=$PROJECT_NAME -o jsonpath='{.items[0].metadata.name}')"
echo "  oc rsh \$POD python manage.py createsuperuser"
echo ""
