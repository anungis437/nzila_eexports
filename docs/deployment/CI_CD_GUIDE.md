# CI/CD Pipeline Documentation

## Overview

The Nzila Export platform uses GitHub Actions for continuous integration and deployment. The pipeline consists of three workflows:

1. **CI (Continuous Integration)** - Automated testing and quality checks
2. **CD (Continuous Deployment)** - Automated deployment to staging and production
3. **Security** - Automated security scanning and vulnerability detection

## CI Pipeline (`.github/workflows/ci.yml`)

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Jobs

#### Backend Jobs
1. **backend-tests**
   - Runs Django test suite
   - Generates coverage report
   - Uploads to Codecov
   - Required for PR merge

2. **backend-lint**
   - Flake8 (syntax and style)
   - Black (code formatting)
   - isort (import sorting)
   - Blocks PR if linting fails

3. **backend-security**
   - Bandit (security issues)
   - Safety (dependency vulnerabilities)
   - Creates security report

#### Frontend Jobs
1. **frontend-tests**
   - TypeScript type checking
   - Build verification
   - Unit tests (when implemented)

2. **frontend-lint**
   - ESLint (code quality)
   - Type checking
   - Blocks PR if linting fails

3. **frontend-security**
   - npm audit (dependency vulnerabilities)
   - Generates security report

### Setup Requirements

#### GitHub Secrets
```bash
# Add these secrets in GitHub: Settings → Secrets and variables → Actions
CODECOV_TOKEN=<your-codecov-token>
```

#### Repository Settings
1. Enable "Require status checks to pass before merging"
2. Add required checks:
   - `Backend Tests`
   - `Backend Lint`
   - `Frontend Tests`
   - `Frontend Lint`

## CD Pipeline (`.github/workflows/deploy.yml`)

### Deployment Environments

#### Staging
- **URL**: https://staging.nzila-export.com
- **Trigger**: Automatic on push to `main`
- **Purpose**: Pre-production testing
- **Database**: Separate staging database
- **Data**: Test data only

#### Production
- **URL**: https://nzila-export.com
- **Trigger**: Git tags matching `v*.*.*` (e.g., v1.0.0)
- **Purpose**: Live customer environment
- **Database**: Production PostgreSQL
- **Monitoring**: Sentry enabled

### Deployment Process

#### 1. Build Docker Images
```bash
# Backend image
ghcr.io/your-org/nzila-export/backend:latest
ghcr.io/your-org/nzila-export/backend:v1.0.0
ghcr.io/your-org/nzila-export/backend:sha-abc123

# Frontend image
ghcr.io/your-org/nzila-export/frontend:latest
ghcr.io/your-org/nzila-export/frontend:v1.0.0
```

#### 2. Deploy to Staging
```bash
# Automated steps:
1. Pull latest images
2. Run database migrations
3. Restart services
4. Health checks
5. Smoke tests
```

#### 3. Integration Tests
- API endpoint tests
- Authentication flow tests
- Critical user journeys
- Database connectivity

#### 4. Deploy to Production
```bash
# Automated steps:
1. Create database backup
2. Pull production images
3. Run migrations (zero-downtime)
4. Rolling deployment
5. Cache warming
6. Health verification
7. Create Sentry release
```

### Rollback Procedure

#### Automatic Rollback
- Triggered on failed health checks
- Reverts to previous container version
- Restores database from backup if needed

#### Manual Rollback
```bash
# Option 1: Via GitHub Actions
1. Go to Actions → Deploy workflow
2. Click "Run workflow"
3. Select "Rollback" option

# Option 2: Via SSH
ssh deploy@prod.server
cd /app
./rollback.sh
```

## Security Pipeline (`.github/workflows/security.yml`)

### Automated Security Scans

#### 1. CodeQL (Code Analysis)
- **Languages**: Python, JavaScript/TypeScript
- **Queries**: Security-extended, quality
- **Schedule**: Daily at 2 AM UTC
- **Reports**: GitHub Security tab

#### 2. Dependency Scanning
- **Tools**:
  - GitHub Dependency Review (PR only)
  - OWASP Dependency Check (all deps)
  - npm audit (frontend)
  - Safety (backend)
- **Fail On**: Critical/High vulnerabilities
- **License Check**: Blocks GPL-3.0, AGPL-3.0

#### 3. Container Scanning
- **Tool**: Trivy
- **Scans**: Base images, dependencies
- **Severity**: Critical, High
- **Output**: SARIF format → Security tab

#### 4. Secrets Detection
- **Tool**: TruffleHog
- **Scans**: Full git history
- **Detects**: API keys, passwords, tokens
- **Action**: Blocks PR, alerts security team

#### 5. SAST (Static Analysis)
- **Tool**: Semgrep
- **Rulesets**:
  - OWASP Top 10
  - Django security
  - React best practices
- **Output**: SARIF → Security tab

### Security Reports

#### Viewing Results
```bash
# GitHub UI
1. Repository → Security tab
2. View "Code scanning alerts"
3. Filter by severity/tool

# Download reports
1. Actions → Security workflow
2. Download artifacts:
   - owasp-dependency-check-report
   - license-reports
```

## Setup Instructions

### 1. GitHub Repository Setup

#### Enable GitHub Actions
```bash
# In repository settings:
Settings → Actions → General
- Allow all actions and reusable workflows
- Enable "Allow GitHub Actions to create pull requests"
```

#### Configure Environments
```bash
# Create staging environment:
Settings → Environments → New environment
Name: staging
Protection rules:
- ✅ Required reviewers: 1
- ✅ Wait timer: 0 minutes

# Create production environment:
Name: production
Protection rules:
- ✅ Required reviewers: 2
- ✅ Wait timer: 5 minutes
- ✅ Deployment branches: main + tags
```

### 2. Secrets Configuration

#### GitHub Container Registry
```bash
# Automatic - GITHUB_TOKEN has push permissions
# Verify: Settings → Actions → General → Workflow permissions
- ✅ Read and write permissions
```

#### Deployment Secrets (Staging)
```bash
# Settings → Environments → staging → Add secret

DB_PASSWORD=<staging-db-password>
REDIS_PASSWORD=<staging-redis-password>
SECRET_KEY=<django-secret-key-staging>
STRIPE_SECRET_KEY=<stripe-test-key>
SENTRY_DSN=<sentry-staging-dsn>
EMAIL_HOST_PASSWORD=<email-password>
```

#### Deployment Secrets (Production)
```bash
# Settings → Environments → production → Add secret

DB_PASSWORD=<prod-db-password>
REDIS_PASSWORD=<prod-redis-password>
SECRET_KEY=<django-secret-key-prod>
STRIPE_SECRET_KEY=<stripe-live-key>
STRIPE_WEBHOOK_SECRET=<stripe-webhook-secret>
SENTRY_DSN=<sentry-prod-dsn>
SENTRY_AUTH_TOKEN=<sentry-auth-token>
SENTRY_ORG=<your-sentry-org>
SENTRY_PROJECT=nzila-export
EMAIL_HOST_PASSWORD=<email-password>
ALLOWED_HOSTS=nzila-export.com,www.nzila-export.com
VITE_API_URL=https://nzila-export.com/api
VITE_SENTRY_DSN=<sentry-frontend-dsn>
```

### 3. Server Preparation

#### Staging Server Setup
```bash
# SSH into staging server
ssh deploy@staging.server

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /app
sudo chown deploy:deploy /app
cd /app

# Set up GitHub Container Registry authentication
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

#### Production Server Setup
```bash
# Same as staging, plus:

# Set up SSL certificates
sudo apt install certbot
sudo certbot certonly --standalone -d nzila-export.com -d www.nzila-export.com

# Configure firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Set up automated backups
sudo crontab -e
# Add: 0 2 * * * /app/backup.sh
```

### 4. Deploy Script Setup

#### Create deployment script (`/app/deploy.sh`)
```bash
#!/bin/bash
set -e

IMAGE_TAG=${1:-latest}

echo "🚀 Deploying version: $IMAGE_TAG"

# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Stop services gracefully
docker-compose -f docker-compose.prod.yml down

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
sleep 10

# Run migrations
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Health check
curl -f http://localhost/health || exit 1

echo "✅ Deployment successful"
```

#### Create rollback script (`/app/rollback.sh`)
```bash
#!/bin/bash
set -e

echo "⏪ Rolling back to previous version"

# Restore from backup
docker-compose -f docker-compose.prod.yml down
pg_restore -d nzila_export < /backups/latest.dump

# Deploy previous image
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback complete"
```

### 5. Testing the Pipeline

#### Test CI Pipeline
```bash
# Create feature branch
git checkout -b test/ci-pipeline

# Make a small change
echo "# Test" >> README.md
git add README.md
git commit -m "test: CI pipeline"

# Push and create PR
git push origin test/ci-pipeline
# Go to GitHub and create pull request

# Verify:
✅ All 6 CI jobs pass
✅ Codecov comment appears
✅ Security scans complete
```

#### Test Staging Deployment
```bash
# Merge PR to main
# Verify in GitHub Actions:
✅ Build images job completes
✅ Deploy to staging succeeds
✅ Integration tests pass

# Manual verification:
curl https://staging.nzila-export.com/health
curl https://staging.nzila-export.com/api/vehicles/
```

#### Test Production Deployment
```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Verify in GitHub Actions:
✅ Build images
✅ Deploy to staging
✅ Integration tests
⏸️  Awaiting production approval (2 reviewers)
✅ Deploy to production
✅ Sentry release created

# Manual verification:
curl https://nzila-export.com/health
```

## Monitoring and Alerts

### GitHub Actions Notifications

#### Slack Integration
```yaml
# Add to workflow files:
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "❌ Pipeline failed: ${{ github.workflow }}",
        "workflow": "${{ github.workflow }}",
        "status": "failure"
      }
```

#### Email Notifications
```bash
# GitHub Settings → Notifications
✅ Actions: Notify me on workflow failures
```

### Sentry Integration

#### Release Tracking
```bash
# Automatically creates Sentry releases with:
- Release version (git tag)
- Commit history
- Deploy timestamp
- Environment (staging/production)
```

#### Error Tracking
```bash
# View in Sentry dashboard:
- Errors by release
- Performance metrics
- User impact
```

## Troubleshooting

### Common Issues

#### 1. Docker Build Fails
```bash
# Check:
- Dockerfile syntax
- Base image availability
- Build context size (add to .dockerignore)

# Debug locally:
docker build -f Dockerfile.backend -t test .
```

#### 2. Deployment Hangs
```bash
# Check server logs:
ssh deploy@server
docker-compose -f docker-compose.prod.yml logs -f

# Common causes:
- Database migration stuck
- Health check failing
- Port already in use
```

#### 3. Tests Fail in CI but Pass Locally
```bash
# Check:
- Environment variables
- Database state (migrations)
- Test isolation (use --keepdb cautiously)

# Run in CI environment:
docker run -it python:3.12 bash
# ... replicate CI steps
```

#### 4. Security Scan False Positives
```bash
# Suppress in .semgrep.yml:
rules:
  - id: django-raw-sql
    paths:
      exclude:
        - tests/

# Document in security-exceptions.md
```

## Performance Optimization

### Build Caching
```yaml
# Already implemented:
- Docker layer caching (GitHub Actions cache)
- npm ci cache
- pip cache
```

### Parallel Execution
```yaml
# CI jobs run in parallel:
- backend-tests, backend-lint, backend-security
- frontend-tests, frontend-lint, frontend-security

# Total CI time: ~5-8 minutes (was 15+ sequential)
```

## Maintenance

### Regular Tasks

#### Weekly
- Review security scan results
- Update dependencies with vulnerabilities
- Check deployment logs

#### Monthly
- Audit secrets rotation
- Review and clean old Docker images
- Update base images (Python, Node, nginx)

#### Quarterly
- Update GitHub Actions versions
- Review and optimize workflow performance
- Update security scanning tools

## Best Practices

### Commits and PRs
```bash
# Conventional commits for changelog generation:
git commit -m "feat: Add vehicle export feature"
git commit -m "fix: Resolve payment processing bug"
git commit -m "docs: Update deployment guide"
git commit -m "chore: Update dependencies"

# PR requirements:
- All CI checks pass
- Code review approved (1+ reviewer)
- Up-to-date with main branch
```

### Release Process
```bash
# Semantic versioning:
v1.0.0 - Major: Breaking changes
v1.1.0 - Minor: New features (backward compatible)
v1.1.1 - Patch: Bug fixes

# Release checklist:
1. Update CHANGELOG.md
2. Update version in package.json
3. Create git tag
4. Monitor deployment
5. Verify in production
6. Announce to team
```

### Security
```bash
# Never commit secrets
- Use environment variables
- Use GitHub Secrets
- Rotate secrets quarterly

# Keep dependencies updated
- Review Dependabot PRs weekly
- Update within 7 days of security alerts
- Test thoroughly after updates
```

## Support

### Getting Help
- **CI/CD Issues**: Check GitHub Actions logs
- **Deployment Issues**: Check server logs via SSH
- **Security Issues**: Review GitHub Security tab
- **General Questions**: Contact DevOps team

### Useful Commands
```bash
# View CI logs
gh run list
gh run view <run-id>
gh run watch <run-id>

# Rerun failed jobs
gh run rerun <run-id>

# View deployments
gh api repos/:owner/:repo/deployments

# Trigger manual deployment
gh workflow run deploy.yml
```
