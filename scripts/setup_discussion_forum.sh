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
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: PostgreSQL client (psql) not found${NC}"
    echo "Please install PostgreSQL first"
    exit 1
fi

# Load environment variables from .env if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${BLUE}Loading database credentials from .env file...${NC}"
    source "$PROJECT_ROOT/.env"
    
    # Use environment variables if set
    DB_NAME=${DATABASENAME_APP:-}
    DB_USER=${DB_USERNAME:-}
    DB_PASSWORD=${DB_PASSWORD:-}
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
fi

# Prompt for missing credentials
if [ -z "$DB_NAME" ]; then
    read -p "Database name: " DB_NAME
fi

if [ -z "$DB_USER" ]; then
    read -p "Database user: " DB_USER
fi

if [ -z "$DB_PASSWORD" ]; then
    read -sp "Database password: " DB_PASSWORD
    echo ""
fi

# Display connection info
echo ""
echo -e "${BLUE}Connection Details:${NC}"
echo "  Host: ${DB_HOST:-localhost}"
echo "  Port: ${DB_PORT:-5432}"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Test database connection
echo "Testing database connection..."
export PGPASSWORD=$DB_PASSWORD
if psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME -c "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    echo "Please check your credentials and try again"
    exit 1
fi

# Check if schema file exists
SCHEMA_FILE="$PROJECT_ROOT/docs/discussion/schema.sql"
if [ ! -f "$SCHEMA_FILE" ]; then
    echo -e "${RED}✗ Schema file not found: $SCHEMA_FILE${NC}"
    echo "Please ensure the schema file exists"
    exit 1
fi

# Check if tables already exist
echo ""
echo "Checking for existing discussion tables..."
TABLE_CHECK=$(psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'discussion_threads';" 2>/dev/null | tr -d ' ')

if [ "$TABLE_CHECK" = "1" ]; then
    echo -e "${YELLOW}⚠ Discussion tables already exist${NC}"
    read -p "Do you want to recreate them? This will DELETE all existing data! (yes/no): " RECREATE
    if [ "$RECREATE" != "yes" ]; then
        echo "Skipping table creation"
    else
        echo "Dropping existing tables..."
        psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS discussion_user_reputation, discussion_reports, discussion_thread_followers, discussion_comment_likes, discussion_comments, discussion_threads CASCADE;" > /dev/null 2>&1
        echo -e "${GREEN}✓ Existing tables dropped${NC}"
    fi
fi

# Create database tables
echo ""
echo "Creating discussion forum tables..."
if psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME -f "$SCHEMA_FILE" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database tables created successfully${NC}"
else
    echo -e "${RED}✗ Failed to create database tables${NC}"
    echo "Running with verbose output for debugging:"
    psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME -f "$SCHEMA_FILE"
    exit 1
fi

# Verify tables were created
echo ""
echo "Verifying table creation..."
TABLES=("discussion_threads" "discussion_comments" "discussion_comment_likes" "discussion_thread_followers" "discussion_reports" "discussion_user_reputation")

ALL_CREATED=true
for table in "${TABLES[@]}"; do
    TABLE_EXISTS=$(psql -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '$table';" 2>/dev/null | tr -d ' ')
    if [ "$TABLE_EXISTS" = "1" ]; then
        echo -e "${GREEN}✓${NC} $table"
    else
        echo -e "${RED}✗${NC} $table (not created)"
        ALL_CREATED=false
    fi
done

if [ "$ALL_CREATED" = false ]; then
    echo ""
    echo -e "${RED}Some tables were not created. Please check the error messages above.${NC}"
    exit 1
fi

# Verify Flask app structure
echo ""
echo "Verifying application structure..."

FILES=(
    "cps/discussion/__init__.py"
    "cps/discussion/models.py"
    "cps/discussion/api.py"
    "cps/discussion/routes.py"
    "cps/templates/discussion_forum.html"
    "cps/templates/discussion_thread.html"
)

ALL_EXIST=true
for file in "${FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
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
if grep -q "from .discussion import" "$PROJECT_ROOT/cps/main.py" 2>/dev/null; then
    echo -e "${GREEN}✓ Blueprints are registered${NC}"
else
    echo -e "${YELLOW}⚠ Blueprints may not be registered${NC}"
    echo "Please add the following to cps/main.py:"
    echo ""
    echo "from .discussion import discussion_api, discussion_routes"
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
echo -e "${GREEN}✓ Database tables created${NC}"
echo -e "${GREEN}✓ Application files verified${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure blueprints are registered in cps/main.py"
echo "2. Discussion button is already added to book detail pages"
echo "3. Restart your Flask application:"
echo "   ${BLUE}.venv/bin/python3 cps.py${NC}"
echo "4. Navigate to any book and click 'Discussion Forum' button"
echo ""
echo "For detailed instructions, see docs/discussion/README.md"
echo ""
echo -e "${GREEN}Happy discussing! 🎉${NC}"
