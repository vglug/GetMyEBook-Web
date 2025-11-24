#!/bin/bash

# Discussion Forum Cleanup Script
# Removes old discussion files after reorganization

echo "🧹 Discussion Forum Cleanup Script"
echo "=================================="
echo ""
echo "This script will remove the OLD discussion files that have been"
echo "reorganized into the new module structure."
echo ""
echo "Files to be removed:"
echo "  - cps/discussion_models.py"
echo "  - cps/discussion_api.py"
echo "  - cps/discussion_routes.py"
echo ""
echo "⚠️  WARNING: Make sure the new module is working before running this!"
echo ""
read -p "Continue with cleanup? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 1
fi

echo "🗑️  Removing old files..."

# Remove old Python files
if [ -f "cps/discussion_models.py" ]; then
    rm "cps/discussion_models.py"
    echo "✓ Removed cps/discussion_models.py"
fi

if [ -f "cps/discussion_api.py" ]; then
    rm "cps/discussion_api.py"
    echo "✓ Removed cps/discussion_api.py"
fi

if [ -f "cps/discussion_routes.py" ]; then
    rm "cps/discussion_routes.py"
    echo "✓ Removed cps/discussion_routes.py"
fi

# Remove compiled Python files
if [ -f "cps/__pycache__/discussion_models.cpython-312.pyc" ]; then
    rm "cps/__pycache__/discussion_models.cpython-312.pyc"
    echo "✓ Removed cached discussion_models"
fi

if [ -f "cps/__pycache__/discussion_api.cpython-312.pyc" ]; then
    rm "cps/__pycache__/discussion_api.cpython-312.pyc"
    echo "✓ Removed cached discussion_api"
fi

if [ -f "cps/__pycache__/discussion_routes.cpython-312.pyc" ]; then
    rm "cps/__pycache__/discussion_routes.cpython-312.pyc"
    echo "✓ Removed cached discussion_routes"
fi

echo ""
echo "✅ Cleanup completed successfully!"
echo ""
echo "New structure:"
echo "  ✓ cps/discussion/ (module with all discussion code)"
echo "  ✓ docs/discussion/ (all documentation)"
echo "  ✓ scripts/ (setup scripts)"
echo ""
echo "You can now use: from cps.discussion import discussion_api, discussion_routes"
echo ""
