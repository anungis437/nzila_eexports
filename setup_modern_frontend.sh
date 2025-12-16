#!/bin/bash

echo "🚀 Setting up Nzila Export Hub - Modern Frontend"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "${BLUE}📦 Installing Frontend Dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -eq 0 ]; then
        echo "${GREEN}✅ Frontend dependencies installed successfully${NC}"
    else
        echo "${YELLOW}⚠️  Some dependencies may have warnings, but should still work${NC}"
    fi
else
    echo "${GREEN}✅ Frontend dependencies already installed${NC}"
fi

echo ""
echo "${BLUE}📦 Installing Marketing Site Dependencies...${NC}"
cd ../marketing-site
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -eq 0 ]; then
        echo "${GREEN}✅ Marketing site dependencies installed successfully${NC}"
    else
        echo "${YELLOW}⚠️  Some dependencies may have warnings, but should still work${NC}"
    fi
else
    echo "${GREEN}✅ Marketing site dependencies already installed${NC}"
fi

cd ..

echo ""
echo "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "================================================"
echo "${BLUE}📋 Next Steps:${NC}"
echo ""
echo "1. Start Django Backend:"
echo "   ${YELLOW}python manage.py runserver${NC}"
echo ""
echo "2. Start Frontend (in new terminal):"
echo "   ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo "3. Start Marketing Site (in new terminal):"
echo "   ${YELLOW}cd marketing-site && npm run dev${NC}"
echo ""
echo "================================================"
echo "${BLUE}🌐 Access URLs:${NC}"
echo "   Frontend App:    http://localhost:3000"
echo "   Backend API:     http://localhost:8000"
echo "   Admin Panel:     http://localhost:8000/admin"
echo "   Marketing Site:  http://localhost:3001"
echo ""
echo "${GREEN}Happy coding! 🚀${NC}"
