#!/bin/bash
# ySEal SQLite Setup Script
# Quick setup for development/testing with SQLite

set -e

echo "=================================="
echo "ySEal SQLite Development Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3.10+ is installed
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Error: Python 3.10 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    
    # Generate a random SECRET_KEY
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$SECRET_KEY|g" .env
        sed -i '' "s|USE_POSTGRES=.*|USE_POSTGRES=False|g" .env
    else
        # Linux
        sed -i "s|DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$SECRET_KEY|g" .env
        sed -i "s|USE_POSTGRES=.*|USE_POSTGRES=False|g" .env
    fi
    
    echo -e "${GREEN}✓ .env file created with SQLite configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ Database migrations complete${NC}"

# Create superuser
echo ""
echo -e "${YELLOW}Creating superuser...${NC}"
echo -e "${YELLOW}Please enter superuser credentials:${NC}"
python manage.py createsuperuser

# Collect static files
echo ""
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

# Success message
echo ""
echo -e "${GREEN}=================================="
echo -e "Setup Complete! 🎉"
echo -e "==================================${NC}"
echo ""
echo "Your ySEal development environment is ready with SQLite!"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Access the application:"
echo "   - Admin interface: http://127.0.0.1:8000/admin/"
echo "   - API documentation: http://127.0.0.1:8000/api/docs/"
echo "   - API schema: http://127.0.0.1:8000/api/schema/"
echo ""
echo -e "${YELLOW}Note:${NC} You're using SQLite for testing/development."
echo "For production, set USE_POSTGRES=True in .env and run ./setup.sh"
echo ""
