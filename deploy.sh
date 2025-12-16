#!/bin/bash
# Production Deployment Script for Nzila Export Platform
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   Nzila Export Platform - Deployment Script     ${NC}"
echo -e "${GREEN}   Environment: $ENVIRONMENT                      ${NC}"
echo -e "${GREEN}==================================================${NC}"

# Function to print step
print_step() {
    echo -e "\n${YELLOW}>>> $1${NC}"
}

# Function to check if command succeeded
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1 failed!${NC}"
        exit 1
    fi
}

# Validate environment
if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    echo -e "${RED}Error: Environment must be 'production' or 'staging'${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found. Copy .env.example and configure it first.${NC}"
    exit 1
fi

# 1. Backup current database
print_step "Creating database backup..."
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
    check_success "Database backup created"
fi

# 2. Update code from git
print_step "Pulling latest code from repository..."
git fetch origin
git pull origin main
check_success "Code updated"

# 3. Install/Update Python dependencies
print_step "Installing Python dependencies..."
pip install -r requirements.txt --upgrade
check_success "Python dependencies installed"

# 4. Run database migrations
print_step "Running database migrations..."
python manage.py migrate --no-input
check_success "Database migrations completed"

# 5. Collect static files
print_step "Collecting static files..."
python manage.py collectstatic --no-input --clear
check_success "Static files collected"

# 6. Build frontend
print_step "Building frontend application..."
cd frontend
npm install
npm run build
check_success "Frontend built successfully"
cd ..

# 7. Build marketing site
print_step "Building marketing site..."
cd marketing-site
npm install
npm run build
check_success "Marketing site built"
cd ..

# 8. Run tests
print_step "Running test suite..."
python manage.py test --verbosity=0
check_success "All tests passed"

# 9. Check for security issues
print_step "Running security checks..."
python manage.py check --deploy
check_success "Security checks completed"

# 10. Update exchange rates
print_step "Updating exchange rates..."
python manage.py shell << EOF
from payments.stripe_service import StripePaymentService
result = StripePaymentService.update_exchange_rates()
print(f"Exchange rates updated: {result}")
EOF
check_success "Exchange rates updated"

# 11. Restart services
print_step "Restarting services..."
if command -v systemctl &> /dev/null; then
    # Systemd service management
    if systemctl list-units --type=service --all | grep -q "gunicorn-nzila"; then
        sudo systemctl restart gunicorn-nzila
        check_success "Gunicorn restarted"
    fi
    
    if systemctl list-units --type=service --all | grep -q "celery-nzila"; then
        sudo systemctl restart celery-nzila
        check_success "Celery worker restarted"
    fi
    
    if systemctl list-units --type=service --all | grep -q "celery-beat-nzila"; then
        sudo systemctl restart celery-beat-nzila
        check_success "Celery beat restarted"
    fi
    
    if systemctl list-units --type=service --all | grep -q "nginx"; then
        sudo systemctl reload nginx
        check_success "Nginx reloaded"
    fi
else
    echo -e "${YELLOW}Note: systemctl not found. Please restart services manually.${NC}"
fi

# 12. Clear cache
print_step "Clearing application cache..."
python manage.py shell << EOF
from django.core.cache import cache
cache.clear()
print("Cache cleared")
EOF
check_success "Cache cleared"

# 13. Verify deployment
print_step "Verifying deployment..."
python manage.py check
check_success "Deployment verification passed"

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}   Deployment completed successfully!             ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "\n${YELLOW}Post-deployment checklist:${NC}"
echo "  1. Check application logs for errors"
echo "  2. Test critical user flows"
echo "  3. Verify payment processing"
echo "  4. Monitor server resources"
echo "  5. Check Celery tasks are running"
echo ""
echo -e "${GREEN}Backup location: $BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3${NC}"
echo ""
