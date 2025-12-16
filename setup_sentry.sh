#!/bin/bash

# Sentry Quick Setup Script
# This script helps configure Sentry for both backend and frontend

set -e

echo "🔧 Sentry Configuration Setup"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env files exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Backend .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env${NC}"
fi

if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}⚠️  Frontend .env file not found. Creating from .env.example...${NC}"
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
fi

echo ""
echo -e "${BLUE}📋 Sentry Setup Instructions${NC}"
echo "================================"
echo ""
echo "1. Sign up for Sentry at: https://sentry.io/signup/"
echo "2. Create an organization (e.g., 'Nzila Exports')"
echo "3. Create TWO projects:"
echo "   - Backend: Select 'Django' platform"
echo "   - Frontend: Select 'React' platform"
echo ""
echo "4. Copy the DSN from each project"
echo ""

# Prompt for backend DSN
echo -e "${BLUE}Backend Configuration${NC}"
echo "---------------------"
read -p "Enter Backend Sentry DSN (leave empty to skip): " BACKEND_DSN

if [ ! -z "$BACKEND_DSN" ]; then
    # Check if SENTRY_DSN already exists in .env
    if grep -q "^SENTRY_DSN=" .env; then
        # Update existing line
        sed -i "s|^SENTRY_DSN=.*|SENTRY_DSN=${BACKEND_DSN}|" .env
    else
        # Append new line
        echo "SENTRY_DSN=${BACKEND_DSN}" >> .env
    fi
    
    # Update environment
    if grep -q "^SENTRY_ENVIRONMENT=" .env; then
        sed -i "s|^SENTRY_ENVIRONMENT=.*|SENTRY_ENVIRONMENT=development|" .env
    else
        echo "SENTRY_ENVIRONMENT=development" >> .env
    fi
    
    # Update version
    if grep -q "^APP_VERSION=" .env; then
        sed -i "s|^APP_VERSION=.*|APP_VERSION=1.0.0|" .env
    else
        echo "APP_VERSION=1.0.0" >> .env
    fi
    
    echo -e "${GREEN}✓ Backend Sentry configured${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping backend Sentry configuration${NC}"
fi

echo ""

# Prompt for frontend DSN
echo -e "${BLUE}Frontend Configuration${NC}"
echo "----------------------"
read -p "Enter Frontend Sentry DSN (leave empty to skip): " FRONTEND_DSN

if [ ! -z "$FRONTEND_DSN" ]; then
    # Check if VITE_SENTRY_DSN already exists in frontend/.env
    if grep -q "^VITE_SENTRY_DSN=" frontend/.env; then
        # Update existing line
        sed -i "s|^VITE_SENTRY_DSN=.*|VITE_SENTRY_DSN=${FRONTEND_DSN}|" frontend/.env
    else
        # Append new line
        echo "VITE_SENTRY_DSN=${FRONTEND_DSN}" >> frontend/.env
    fi
    
    # Update environment
    if grep -q "^VITE_ENVIRONMENT=" frontend/.env; then
        sed -i "s|^VITE_ENVIRONMENT=.*|VITE_ENVIRONMENT=development|" frontend/.env
    else
        echo "VITE_ENVIRONMENT=development" >> frontend/.env
    fi
    
    echo -e "${GREEN}✓ Frontend Sentry configured${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping frontend Sentry configuration${NC}"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Sentry setup complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "1. Restart your backend server: python manage.py runserver"
echo "2. Restart your frontend dev server: cd frontend && npm run dev"
echo "3. Test Sentry integration:"
echo "   - Backend: python manage.py shell"
echo "     >>> from sentry_sdk import capture_message"
echo "     >>> capture_message('Test from Django', level='error')"
echo "   - Frontend: Open browser console"
echo "     >>> Sentry.captureMessage('Test from React', 'error')"
echo ""
echo "4. Check your Sentry dashboard to confirm events are received"
echo ""
echo "For detailed documentation, see: docs/monitoring/SENTRY_SETUP.md"
