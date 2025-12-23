#!/usr/bin/env python
"""
Automated Database Backup Script
================================

Backs up PostgreSQL database to AWS S3 with:
- Compression (gzip)
- Encryption
- Rotation policy (7 daily, 4 weekly, 12 monthly)
- Integrity validation
- Email notifications

Usage:
    python scripts/backup_database.py [--type daily|weekly|monthly]

Environment Variables Required:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_S3_BACKUP_BUCKET
    DATABASE_URL (or DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    BACKUP_NOTIFICATION_EMAIL (optional)
"""

import os
import sys
import subprocess
import gzip
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
import django
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Handles PostgreSQL database backups to AWS S3"""
    
    RETENTION_POLICY = {
        'daily': 7,      # Keep 7 daily backups
        'weekly': 4,     # Keep 4 weekly backups
        'monthly': 12,   # Keep 12 monthly backups
    }
    
    def __init__(self, backup_type='daily'):
        """
        Initialize backup configuration
        
        Args:
            backup_type: Type of backup (daily, weekly, monthly)
        """
        self.backup_type = backup_type
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Database configuration
        self.db_config = self._get_db_config()
        
        # AWS configuration
        self.s3_bucket = os.getenv('AWS_S3_BACKUP_BUCKET', 'nzila-export-backups')
        self.s3_prefix = f"database/{backup_type}"
        
        # Local temp directory
        self.temp_dir = Path(project_root) / 'backups' / 'temp'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup filename
        self.backup_filename = f"nzila_db_{backup_type}_{self.timestamp}.sql.gz"
        self.backup_path = self.temp_dir / self.backup_filename
        
        # Metadata filename
        self.metadata_filename = f"nzila_db_{backup_type}_{self.timestamp}.json"
        
        logger.info(f"Initialized {backup_type} backup: {self.backup_filename}")
    
    def _get_db_config(self):
        """Extract database configuration from Django settings"""
        db_settings = settings.DATABASES['default']
        
        # Support both direct config and DATABASE_URL
        if 'DATABASE_URL' in os.environ:
            # Parse DATABASE_URL (postgres://user:pass@host:port/dbname)
            import urllib.parse
            url = urllib.parse.urlparse(os.environ['DATABASE_URL'])
            return {
                'name': url.path[1:],
                'user': url.username,
                'password': url.password,
                'host': url.hostname,
                'port': url.port or 5432,
            }
        else:
            return {
                'name': db_settings.get('NAME'),
                'user': db_settings.get('USER'),
                'password': db_settings.get('PASSWORD'),
                'host': db_settings.get('HOST', 'localhost'),
                'port': db_settings.get('PORT', 5432),
            }
    
    def create_backup(self):
        """Create PostgreSQL backup using pg_dump"""
        logger.info(f"Starting database backup: {self.db_config['name']}")
        
        # Build pg_dump command
        pg_dump_cmd = [
            'pg_dump',
            '--host', self.db_config['host'],
            '--port', str(self.db_config['port']),
            '--username', self.db_config['user'],
            '--dbname', self.db_config['name'],
            '--format', 'custom',  # Custom format for better compression
            '--verbose',
            '--no-owner',  # Don't dump ownership commands
            '--no-acl',    # Don't dump access privileges
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']
        
        try:
            # Run pg_dump and compress on the fly
            logger.info(f"Running pg_dump to {self.backup_path}")
            
            with open(self.backup_path, 'wb') as f_out:
                # Run pg_dump
                process = subprocess.Popen(
                    pg_dump_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                
                # Compress output
                with gzip.GzipFile(fileobj=f_out, mode='wb', compresslevel=9) as gz:
                    for chunk in iter(lambda: process.stdout.read(8192), b''):
                        gz.write(chunk)
                
                # Wait for completion
                process.wait()
                
                if process.returncode != 0:
                    error = process.stderr.read().decode()
                    raise Exception(f"pg_dump failed: {error}")
            
            # Validate backup
            backup_size = self.backup_path.stat().st_size
            logger.info(f"Backup created successfully: {backup_size / (1024*1024):.2f} MB")
            
            # Calculate checksum
            checksum = self._calculate_checksum(self.backup_path)
            logger.info(f"Backup checksum (SHA256): {checksum}")
            
            return {
                'filename': self.backup_filename,
                'size_bytes': backup_size,
                'checksum': checksum,
                'timestamp': self.timestamp,
                'database': self.db_config['name'],
                'backup_type': self.backup_type,
            }
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            raise
    
    def _calculate_checksum(self, file_path):
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def upload_to_s3(self, metadata):
        """Upload backup to AWS S3"""
        logger.info(f"Uploading backup to S3: s3://{self.s3_bucket}/{self.s3_prefix}/")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Upload backup file
            s3_key = f"{self.s3_prefix}/{self.backup_filename}"
            logger.info(f"Uploading {self.backup_filename} to s3://{self.s3_bucket}/{s3_key}")
            
            with open(self.backup_path, 'rb') as f:
                s3_client.upload_fileobj(
                    f,
                    self.s3_bucket,
                    s3_key,
                    ExtraArgs={
                        'ServerSideEncryption': 'AES256',  # Encrypt at rest
                        'StorageClass': 'STANDARD_IA',     # Infrequent access
                        'Metadata': {
                            'backup-type': self.backup_type,
                            'database': self.db_config['name'],
                            'checksum': metadata['checksum'],
                        }
                    }
                )
            
            logger.info("Backup uploaded successfully")
            
            # Upload metadata
            metadata_key = f"{self.s3_prefix}/{self.metadata_filename}"
            s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=metadata_key,
                Body=json.dumps(metadata, indent=2),
                ServerSideEncryption='AES256',
                ContentType='application/json'
            )
            
            logger.info("Metadata uploaded successfully")
            
            # Return S3 location
            return {
                's3_bucket': self.s3_bucket,
                's3_key': s3_key,
                's3_url': f"s3://{self.s3_bucket}/{s3_key}"
            }
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise
    
    def cleanup_local(self):
        """Remove local backup file"""
        try:
            if self.backup_path.exists():
                self.backup_path.unlink()
                logger.info(f"Local backup file removed: {self.backup_path}")
        except Exception as e:
            logger.warning(f"Failed to remove local backup: {str(e)}")
    
    def rotate_old_backups(self):
        """Delete old backups based on retention policy"""
        logger.info(f"Rotating old {self.backup_type} backups (keep {self.RETENTION_POLICY[self.backup_type]})")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # List all backups of this type
            response = s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=f"{self.s3_prefix}/nzila_db_{self.backup_type}_"
            )
            
            if 'Contents' not in response:
                logger.info("No existing backups found")
                return
            
            # Sort by last modified date (oldest first)
            backups = sorted(
                response['Contents'],
                key=lambda x: x['LastModified']
            )
            
            # Filter only .sql.gz files (not metadata)
            backup_files = [b for b in backups if b['Key'].endswith('.sql.gz')]
            
            # Calculate how many to delete
            retention_count = self.RETENTION_POLICY[self.backup_type]
            if len(backup_files) <= retention_count:
                logger.info(f"Only {len(backup_files)} backups exist (keeping {retention_count}), no rotation needed")
                return
            
            # Delete old backups
            backups_to_delete = backup_files[:-retention_count]  # Keep most recent N
            deleted_count = 0
            
            for backup in backups_to_delete:
                key = backup['Key']
                logger.info(f"Deleting old backup: {key}")
                
                # Delete backup file
                s3_client.delete_object(Bucket=self.s3_bucket, Key=key)
                
                # Delete corresponding metadata file
                metadata_key = key.replace('.sql.gz', '.json')
                try:
                    s3_client.delete_object(Bucket=self.s3_bucket, Key=metadata_key)
                except:
                    pass  # Metadata might not exist
                
                deleted_count += 1
            
            logger.info(f"Rotation complete: deleted {deleted_count} old backups")
            
        except ImportError:
            logger.error("boto3 not installed")
        except ClientError as e:
            logger.error(f"S3 rotation failed: {str(e)}")
    
    def send_notification(self, success, metadata=None, error=None):
        """Send email notification about backup status"""
        notification_email = os.getenv('BACKUP_NOTIFICATION_EMAIL')
        
        if not notification_email:
            logger.info("No notification email configured (BACKUP_NOTIFICATION_EMAIL)")
            return
        
        if success:
            subject = f"✅ Database Backup Successful - {self.backup_type} - {self.timestamp}"
            message = f"""
Database backup completed successfully!

Backup Details:
- Type: {self.backup_type}
- Timestamp: {self.timestamp}
- Database: {metadata['database']}
- Size: {metadata['size_bytes'] / (1024*1024):.2f} MB
- Checksum: {metadata['checksum']}
- S3 Location: {metadata.get('s3_url', 'N/A')}

Retention Policy:
- Daily backups: 7 days
- Weekly backups: 4 weeks
- Monthly backups: 12 months

Next Steps:
- Backups are automatically rotated
- Test restore procedure quarterly
- Monitor S3 storage costs

-- Nzila Export Hub Backup System
            """
        else:
            subject = f"❌ Database Backup Failed - {self.backup_type} - {self.timestamp}"
            message = f"""
ALERT: Database backup FAILED!

Backup Details:
- Type: {self.backup_type}
- Timestamp: {self.timestamp}
- Database: {self.db_config['name']}

Error:
{error}

Action Required:
1. Check database connectivity
2. Verify AWS S3 credentials
3. Check disk space
4. Review logs for details
5. Retry backup manually if needed

-- Nzila Export Hub Backup System
            """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification_email],
                fail_silently=False,
            )
            logger.info(f"Notification sent to {notification_email}")
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    def run(self):
        """Execute full backup workflow"""
        logger.info(f"Starting {self.backup_type} backup workflow")
        start_time = timezone.now()
        
        try:
            # Step 1: Create backup
            metadata = self.create_backup()
            
            # Step 2: Upload to S3
            s3_info = self.upload_to_s3(metadata)
            metadata.update(s3_info)
            
            # Step 3: Cleanup local file
            self.cleanup_local()
            
            # Step 4: Rotate old backups
            self.rotate_old_backups()
            
            # Step 5: Send success notification
            duration = (timezone.now() - start_time).total_seconds()
            metadata['duration_seconds'] = duration
            self.send_notification(success=True, metadata=metadata)
            
            logger.info(f"Backup workflow completed successfully in {duration:.2f}s")
            return metadata
            
        except Exception as e:
            logger.error(f"Backup workflow failed: {str(e)}")
            
            # Cleanup on failure
            self.cleanup_local()
            
            # Send failure notification
            self.send_notification(success=False, error=str(e))
            
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Automated database backup to S3')
    parser.add_argument(
        '--type',
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='Backup type (determines retention policy)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test backup without uploading to S3'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BACKUP_BUCKET']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars and not args.dry_run:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Set them in .env file or environment")
        sys.exit(1)
    
    # Run backup
    try:
        backup = DatabaseBackup(backup_type=args.type)
        
        if args.dry_run:
            logger.info("DRY RUN MODE - Creating backup but not uploading to S3")
            metadata = backup.create_backup()
            backup.cleanup_local()
            logger.info(f"Dry run successful: {json.dumps(metadata, indent=2)}")
        else:
            metadata = backup.run()
            logger.info(f"Backup completed: {json.dumps(metadata, indent=2)}")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
