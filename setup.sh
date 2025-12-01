#!/bin/bash
# ySEal Setup Script
# This script helps set up the development environment for ySEal

set -e

echo "=================================="
echo "ySEal Development Setup"
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
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3.10+ is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

# Check if PostgreSQL is installed
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL found${NC}"
else
    echo -e "${RED}✗ PostgreSQL not found. Please install PostgreSQL 12+${NC}"
    exit 1
fi

# Check if Redis is installed
echo -e "${YELLOW}Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓ Redis found${NC}"
else
    echo -e "${RED}✗ Redis not found. Please install Redis 6+${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✓ .env file created with generated SECRET_KEY${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create logs directory
echo -e "${YELLOW}Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

# Create static and media directories
echo -e "${YELLOW}Creating static and media directories...${NC}"
mkdir -p static media staticfiles
echo -e "${GREEN}✓ Static and media directories created${NC}"

# Database setup
echo ""
echo -e "${YELLOW}Would you like to set up the PostgreSQL database? (y/n)${NC}"
read -r setup_db

if [ "$setup_db" = "y" ]; then
    echo -e "${YELLOW}Setting up PostgreSQL database...${NC}"
    
    # Check if database exists
    DB_EXISTS=$(psql -lqt | cut -d \| -f 1 | grep -w yseal | wc -l)
    
    if [ "$DB_EXISTS" -eq 0 ]; then
        echo -e "${YELLOW}Creating database 'yseal'...${NC}"
        createdb yseal || echo -e "${YELLOW}Note: Database might already exist${NC}"
        
        echo -e "${YELLOW}Creating user 'yseal'...${NC}"
        psql -c "CREATE USER yseal WITH PASSWORD 'yseal';" || echo -e "${YELLOW}Note: User might already exist${NC}"
        
        echo -e "${YELLOW}Granting privileges...${NC}"
        psql -c "GRANT ALL PRIVILEGES ON DATABASE yseal TO yseal;"
        psql -d yseal -c "GRANT ALL ON SCHEMA public TO yseal;"
        
        echo -e "${GREEN}✓ Database setup complete${NC}"
    else
        echo -e "${GREEN}✓ Database 'yseal' already exists${NC}"
    fi
fi

# Run migrations
echo ""
echo -e "${YELLOW}Would you like to run Django migrations? (y/n)${NC}"
read -r run_migrations

if [ "$run_migrations" = "y" ]; then
    echo -e "${YELLOW}Running migrations...${NC}"
    python manage.py makemigrations
    python manage.py migrate
    echo -e "${GREEN}✓ Migrations complete${NC}"
fi

# Create superuser
echo ""
echo -e "${YELLOW}Would you like to create a superuser? (y/n)${NC}"
read -r create_superuser

if [ "$create_superuser" = "y" ]; then
    echo -e "${YELLOW}Creating superuser...${NC}"
    python manage.py createsuperuser
    echo -e "${GREEN}✓ Superuser created${NC}"
fi

# Collect static files
echo ""
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

echo ""
echo -e "${GREEN}=================================="
echo "Setup Complete!"
echo "==================================${NC}"
echo ""
echo "To start the development server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start Django: python manage.py runserver"
echo "  3. Start Celery worker (new terminal): celery -A yseal worker -l info"
echo "  4. Start Celery beat (new terminal): celery -A yseal beat -l info"
echo ""
echo "Access points:"
echo "  - Web UI: http://localhost:8000/"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - API Docs: http://localhost:8000/api/docs/"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
