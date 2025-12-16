# Deployment Guide

This guide covers deploying the Nzila E-Exports platform to production.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Database Configuration](#database-configuration)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Security Configuration](#security-configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Requirements
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ and npm installed
- [ ] PostgreSQL 14+ database server
- [ ] Redis 6+ for Celery
- [ ] SSL certificate for HTTPS
- [ ] Domain name configured
- [ ] Stripe account (production keys)
- [ ] SMS provider account (Twilio recommended)
- [ ] Email service (SendGrid, AWS SES, or SMTP)

### Security
- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Configure CORS allowed origins
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure SSL/TLS certificates
- [ ] Set up rate limiting
- [ ] Configure security headers

### Services
- [ ] Stripe production keys configured
- [ ] SMS provider credentials set
- [ ] Email service configured
- [ ] Storage service (AWS S3, Azure, or local)
- [ ] Monitoring tools (Sentry, DataDog, etc.)

## Environment Setup

### 1. Create Production Environment File

Create `.env.production` in the project root:

```bash
# Django Core Settings
SECRET_KEY=your-production-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=nzila_export.settings_production

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/nzila_exports
DB_NAME=nzila_exports
DB_USER=nzila_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Two-Factor Authentication
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_api_key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Static & Media Files
STATIC_ROOT=/var/www/nzila_exports/static
MEDIA_ROOT=/var/www/nzila_exports/media
STATIC_URL=/static/
MEDIA_URL=/media/

# AWS S3 (Optional - for production file storage)
USE_S3=False
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=nzila-exports-media
AWS_S3_REGION_NAME=us-east-1

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=True

# Logging & Monitoring
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# Application URLs
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

### 2. Generate Secure Secret Key

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Database Configuration

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Create Production Database

```bash
sudo -u postgres psql

-- In PostgreSQL shell:
CREATE DATABASE nzila_exports;
CREATE USER nzila_user WITH PASSWORD 'your-secure-password';
ALTER ROLE nzila_user SET client_encoding TO 'utf8';
ALTER ROLE nzila_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nzila_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nzila_exports TO nzila_user;

-- Exit
\q
```

### 3. Configure PostgreSQL for Production

Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
# Performance tuning (adjust based on server RAM)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
max_connections = 100
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:

```conf
# Local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 4. Enable Automated Backups

Create backup script `/usr/local/bin/backup-nzila-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR=/var/backups/nzila_exports
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U nzila_user -h localhost nzila_exports | gzip > $BACKUP_DIR/nzila_exports_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "nzila_exports_*.sql.gz" -mtime +30 -delete
```

Make executable and add to cron:

```bash
chmod +x /usr/local/bin/backup-nzila-db.sh
sudo crontab -e

# Add line for daily backup at 2 AM:
0 2 * * * /usr/local/bin/backup-nzila-db.sh
```

## Backend Deployment

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip nginx redis-server supervisor

# macOS
brew install python@3.10 nginx redis supervisor
```

### 2. Create Application Directory

```bash
sudo mkdir -p /var/www/nzila_exports
sudo chown $USER:$USER /var/www/nzila_exports
cd /var/www/nzila_exports
```

### 3. Clone Repository

```bash
git clone https://github.com/yourusername/nzila_eexports.git .
```

### 4. Set Up Python Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 5. Configure Environment

```bash
cp .env.production .env
# Edit .env with your production values
nano .env
```

### 6. Run Database Migrations

```bash
python manage.py migrate --settings=nzila_export.settings_production
```

### 7. Create Superuser

```bash
python manage.py createsuperuser --settings=nzila_export.settings_production
```

### 8. Load Currency Data

```bash
python manage.py shell --settings=nzila_export.settings_production

# In Django shell:
from payments.models import Currency
Currency.seed_currencies()
exit()
```

### 9. Collect Static Files

```bash
python manage.py collectstatic --no-input --settings=nzila_export.settings_production
```

### 10. Configure Gunicorn

Create `/var/www/nzila_exports/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/nzila_exports/gunicorn_access.log"
errorlog = "/var/log/nzila_exports/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "nzila_exports"

# Server mechanics
daemon = False
pidfile = "/var/run/nzila_exports/gunicorn.pid"
user = "www-data"
group = "www-data"
```

Create log directory:

```bash
sudo mkdir -p /var/log/nzila_exports
sudo chown www-data:www-data /var/log/nzila_exports
sudo mkdir -p /var/run/nzila_exports
sudo chown www-data:www-data /var/run/nzila_exports
```

### 11. Configure Supervisor for Gunicorn

Create `/etc/supervisor/conf.d/nzila_exports.conf`:

```ini
[program:nzila_exports]
command=/var/www/nzila_exports/venv/bin/gunicorn nzila_export.wsgi:application -c /var/www/nzila_exports/gunicorn_config.py
directory=/var/www/nzila_exports
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/nzila_exports/gunicorn_supervisor.log
stderr_logfile=/var/log/nzila_exports/gunicorn_supervisor_error.log
environment=PATH="/var/www/nzila_exports/venv/bin"
```

Start Gunicorn:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nzila_exports
sudo supervisorctl status
```

### 12. Configure Celery Workers

Create `/etc/supervisor/conf.d/nzila_celery.conf`:

```ini
[program:nzila_celery]
command=/var/www/nzila_exports/venv/bin/celery -A nzila_export worker -l info
directory=/var/www/nzila_exports
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/nzila_exports/celery.log
stderr_logfile=/var/log/nzila_exports/celery_error.log
environment=PATH="/var/www/nzila_exports/venv/bin"

[program:nzila_celery_beat]
command=/var/www/nzila_exports/venv/bin/celery -A nzila_export beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/var/www/nzila_exports
user=www-data
numprocs=1
autostart=true
autorestart=true
startsecs=10
redirect_stderr=true
stdout_logfile=/var/log/nzila_exports/celery_beat.log
stderr_logfile=/var/log/nzila_exports/celery_beat_error.log
environment=PATH="/var/www/nzila_exports/venv/bin"
```

Start Celery:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start nzila_celery
sudo supervisorctl start nzila_celery_beat
sudo supervisorctl status
```

### 13. Configure Nginx

Create `/etc/nginx/sites-available/nzila_exports`:

```nginx
upstream nzila_backend {
    server 127.0.0.1:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # File Upload Limit
    client_max_body_size 20M;

    # Static Files
    location /static/ {
        alias /var/www/nzila_exports/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/nzila_exports/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Backend API
    location / {
        proxy_pass http://nzila_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health Check Endpoint
    location /health/ {
        access_log off;
        proxy_pass http://nzila_backend/health/;
    }
}
```

Enable site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/nzila_exports /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 14. Configure SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Set up auto-renewal:

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Frontend Deployment

### 1. Build Frontend Application

Navigate to marketing site:

```bash
cd /var/www/nzila_exports/marketing-site
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

Create `.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_key
```

### 4. Build for Production

```bash
npm run build
```

### 5. Configure Nginx for Next.js

Update `/etc/nginx/sites-available/nzila_exports` to add frontend:

```nginx
# Frontend (Next.js)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (same as above)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 6. Configure PM2 for Next.js

Install PM2:

```bash
sudo npm install -g pm2
```

Create ecosystem file `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'nzila-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/var/www/nzila_exports/marketing-site',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
```

Start frontend:

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Security Configuration

### 1. Firewall Setup

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban for Brute Force Protection

```bash
sudo apt install fail2ban

# Create config
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Add Django section:
[django-auth]
enabled = true
filter = django-auth
logpath = /var/log/nzila_exports/gunicorn_error.log
maxretry = 5
bantime = 3600
```

Create filter `/etc/fail2ban/filter.d/django-auth.conf`:

```ini
[Definition]
failregex = ^.*Login failed for.*from <HOST>.*$
ignoreregex =
```

Start Fail2Ban:

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Security Updates

Set up unattended upgrades:

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Monitoring & Maintenance

### 1. Application Monitoring (Sentry)

Install Sentry SDK (already in requirements.txt):

```bash
pip install sentry-sdk
```

Add to `settings_production.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment='production'
)
```

### 2. Server Monitoring

Set up server monitoring with Prometheus and Grafana or DataDog.

### 3. Log Rotation

Create `/etc/logrotate.d/nzila_exports`:

```
/var/log/nzila_exports/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart nzila_exports
        supervisorctl restart nzila_celery
    endscript
}
```

### 4. Health Checks

Create health check endpoint in `nzila_export/views.py`:

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

Add to `urls.py`:

```python
path('health/', views.health_check, name='health_check'),
```

Set up monitoring to ping `/health/` endpoint regularly.

### 5. Periodic Tasks

Schedule periodic maintenance tasks:

```bash
# In Django shell
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# Daily database cleanup
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.DAYS,
)

PeriodicTask.objects.get_or_create(
    interval=schedule,
    name='Database Cleanup',
    task='deals.tasks.cleanup_old_data',
)
```

## Troubleshooting

### Application Not Starting

```bash
# Check Gunicorn logs
sudo tail -f /var/log/nzila_exports/gunicorn_error.log

# Check supervisor status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart nzila_exports
```

### Database Connection Issues

```bash
# Test database connection
psql -U nzila_user -h localhost -d nzila_exports

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Celery Not Processing Tasks

```bash
# Check Celery logs
sudo tail -f /var/log/nzila_exports/celery.log

# Restart Celery
sudo supervisorctl restart nzila_celery
sudo supervisorctl restart nzila_celery_beat

# Check Redis
redis-cli ping
```

### High Memory Usage

```bash
# Check memory usage
free -h
htop

# Restart services
sudo supervisorctl restart all
```

### SSL Certificate Issues

```bash
# Test certificate renewal
sudo certbot renew --dry-run

# Force renew
sudo certbot renew --force-renewal
```

### Static Files Not Loading

```bash
# Re-collect static files
cd /var/www/nzila_exports
source venv/bin/activate
python manage.py collectstatic --clear --no-input

# Check permissions
sudo chown -R www-data:www-data /var/www/nzila_exports/staticfiles/
```

### Performance Issues

```bash
# Check slow queries
sudo -u postgres psql nzila_exports

-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- View slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

## Deployment Checklist

Before going live:

- [ ] All tests passing (`python manage.py test`)
- [ ] Database migrations applied
- [ ] Currency data seeded
- [ ] Static files collected
- [ ] SSL certificate installed and auto-renewal configured
- [ ] All environment variables set correctly
- [ ] Stripe production keys configured
- [ ] SMS provider configured
- [ ] Email service configured
- [ ] Backups configured and tested
- [ ] Monitoring and logging set up
- [ ] Security headers configured
- [ ] Firewall rules in place
- [ ] Health check endpoint working
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on deployment process

## Post-Deployment

After successful deployment:

1. **Monitor Logs**: Watch application logs for first 24-48 hours
2. **Test Critical Flows**: Verify payment processing, 2FA, PDF generation
3. **Performance Monitoring**: Check response times and resource usage
4. **Security Audit**: Run security scanners (OWASP ZAP, etc.)
5. **Backup Verification**: Ensure backups are running and restorable
6. **User Feedback**: Gather initial user feedback
7. **Documentation**: Update runbooks with any deployment-specific notes

## Support & Maintenance

- **Daily**: Review error logs and monitoring alerts
- **Weekly**: Check database performance and disk space
- **Monthly**: Security patches and dependency updates
- **Quarterly**: Full security audit and penetration testing

For issues, check logs first, then consult this guide's troubleshooting section.
