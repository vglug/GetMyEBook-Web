#!/bin/bash

# Discussion Forum Setup Script
# This script helps you set up the discussion forum for GetMyEBook-Web

echo "========================================="
echo "Discussion Forum Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: PostgreSQL client (psql) not found${NC}"
    echo "Please install PostgreSQL first"
    exit 1
fi

# Get database credentials
echo ""
echo "Please enter your database credentials:"
read -p "Database name: " DB_NAME
read -p "Database user: " DB_USER
read -sp "Database password: " DB_PASSWORD
echo ""

# Test database connection
echo ""
echo "Testing database connection..."
export PGPASSWORD=$DB_PASSWORD
if psql -U $DB_USER -d $DB_NAME -c "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    echo "Please check your credentials and try again"
    exit 1
fi

# Create database tables
echo ""
echo "Creating discussion forum tables..."
if psql -U $DB_USER -d $DB_NAME -f discussion_forum_schema.sql; then
    echo -e "${GREEN}✓ Database tables created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create database tables${NC}"
    echo "Please check the SQL file and try again"
    exit 1
fi

# Check if Python virtual environment exists
echo ""
echo "Checking Python environment..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
fi

# Verify Flask app structure
echo ""
echo "Verifying application structure..."

FILES=(
    "cps/discussion_models.py"
    "cps/discussion_api.py"
    "cps/discussion_routes.py"
    "cps/templates/discussion_forum.html"
    "cps/templates/discussion_thread.html"
)

ALL_EXIST=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (missing)"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo ""
    echo -e "${RED}Some files are missing. Please ensure all files are in place.${NC}"
    exit 1
fi

# Check if blueprints are registered
echo ""
echo "Checking blueprint registration..."
if grep -q "discussion_api" cps/__init__.py || grep -q "discussion_api" cps.py; then
    echo -e "${GREEN}✓ Blueprints appear to be registered${NC}"
else
    echo -e "${YELLOW}⚠ Blueprints may not be registered${NC}"
    echo "Please add the following to your main app file:"
    echo ""
    echo "from cps.discussion_api import discussion_api"
    echo "from cps.discussion_routes import discussion_routes"
    echo ""
    echo "app.register_blueprint(discussion_api)"
    echo "app.register_blueprint(discussion_routes)"
    echo ""
fi

# Summary
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Register the blueprints in your main app file (if not done)"
echo "2. Add discussion links to your book detail pages"
echo "3. Restart your Flask application"
echo "4. Navigate to /discussion/book/{book_id} to test"
echo ""
echo "For detailed instructions, see DISCUSSION_FORUM_GUIDE.md"
echo ""
echo -e "${GREEN}Happy discussing! 🎉${NC}"
