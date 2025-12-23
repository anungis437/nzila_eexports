#!/usr/bin/env python
"""
Database Restore Script
======================

Restores PostgreSQL database from S3 backup with:
- Download from S3
- Integrity validation (checksum)
- Database restore
- Verification tests

Usage:
    # List available backups
    python scripts/restore_database.py --list
    
    # Restore specific backup
    python scripts/restore_database.py --backup nzila_db_daily_20241220_120000.sql.gz
    
    # Restore latest backup
    python scripts/restore_database.py --latest
    
    # Dry run (test without restoring)
    python scripts/restore_database.py --latest --dry-run

Environment Variables Required:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_S3_BACKUP_BUCKET
    DATABASE_URL (or DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
"""

import os
import sys
import subprocess
import gzip
import hashlib
import json
from datetime import datetime
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
from django.db import connection

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseRestore:
    """Handles PostgreSQL database restoration from S3 backups"""
    
    def __init__(self, backup_filename=None):
        """
        Initialize restore configuration
        
        Args:
            backup_filename: Name of backup file to restore
        """
        self.backup_filename = backup_filename
        
        # Database configuration
        self.db_config = self._get_db_config()
        
        # AWS configuration
        self.s3_bucket = os.getenv('AWS_S3_BACKUP_BUCKET', 'nzila-export-backups')
        
        # Local temp directory
        self.temp_dir = Path(project_root) / 'backups' / 'restore'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        if backup_filename:
            self.backup_path = self.temp_dir / backup_filename
            self.metadata_filename = backup_filename.replace('.sql.gz', '.json')
            logger.info(f"Initialized restore for: {backup_filename}")
    
    def _get_db_config(self):
        """Extract database configuration from Django settings"""
        db_settings = settings.DATABASES['default']
        
        # Support both direct config and DATABASE_URL
        if 'DATABASE_URL' in os.environ:
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
    
    def list_available_backups(self):
        """List all available backups in S3"""
        logger.info(f"Listing backups in s3://{self.s3_bucket}/")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # List all backup files
            all_backups = []
            
            for backup_type in ['daily', 'weekly', 'monthly']:
                prefix = f"database/{backup_type}/"
                
                try:
                    response = s3_client.list_objects_v2(
                        Bucket=self.s3_bucket,
                        Prefix=prefix
                    )
                    
                    if 'Contents' in response:
                        # Filter .sql.gz files only
                        backups = [
                            obj for obj in response['Contents']
                            if obj['Key'].endswith('.sql.gz')
                        ]
                        all_backups.extend(backups)
                except ClientError as e:
                    logger.warning(f"Could not list {backup_type} backups: {str(e)}")
            
            if not all_backups:
                logger.warning("No backups found in S3")
                return []
            
            # Sort by last modified (newest first)
            all_backups.sort(key=lambda x: x['LastModified'], reverse=True)
            
            # Display backups
            print("\n" + "="*80)
            print(f"Available Backups in s3://{self.s3_bucket}/")
            print("="*80)
            print(f"{'Filename':<50} {'Size':<12} {'Date':<20}")
            print("-"*80)
            
            for backup in all_backups:
                filename = backup['Key'].split('/')[-1]
                size_mb = backup['Size'] / (1024 * 1024)
                date = backup['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{filename:<50} {size_mb:>8.2f} MB  {date}")
            
            print("="*80)
            print(f"Total: {len(all_backups)} backups\n")
            
            return all_backups
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            return []
        except ClientError as e:
            logger.error(f"Failed to list S3 backups: {str(e)}")
            return []
    
    def get_latest_backup(self, backup_type='daily'):
        """Get filename of the most recent backup"""
        logger.info(f"Finding latest {backup_type} backup")
        
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            prefix = f"database/{backup_type}/"
            response = s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                logger.error(f"No {backup_type} backups found")
                return None
            
            # Filter .sql.gz files and sort by date
            backups = [
                obj for obj in response['Contents']
                if obj['Key'].endswith('.sql.gz')
            ]
            
            if not backups:
                logger.error(f"No {backup_type} backups found")
                return None
            
            # Get most recent
            latest = max(backups, key=lambda x: x['LastModified'])
            filename = latest['Key'].split('/')[-1]
            
            logger.info(f"Latest backup: {filename} ({latest['LastModified']})")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to find latest backup: {str(e)}")
            return None
    
    def download_from_s3(self):
        """Download backup from S3"""
        logger.info(f"Downloading backup from S3: {self.backup_filename}")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Find S3 key (try all backup types)
            s3_key = None
            for backup_type in ['daily', 'weekly', 'monthly']:
                possible_key = f"database/{backup_type}/{self.backup_filename}"
                try:
                    s3_client.head_object(Bucket=self.s3_bucket, Key=possible_key)
                    s3_key = possible_key
                    break
                except ClientError:
                    continue
            
            if not s3_key:
                raise Exception(f"Backup not found in S3: {self.backup_filename}")
            
            logger.info(f"Downloading from s3://{self.s3_bucket}/{s3_key}")
            
            # Download backup file
            with open(self.backup_path, 'wb') as f:
                s3_client.download_fileobj(self.s3_bucket, s3_key, f)
            
            backup_size = self.backup_path.stat().st_size
            logger.info(f"Download complete: {backup_size / (1024*1024):.2f} MB")
            
            # Download metadata
            try:
                metadata_key = s3_key.replace('.sql.gz', '.json')
                metadata_path = self.temp_dir / self.metadata_filename
                
                with open(metadata_path, 'wb') as f:
                    s3_client.download_fileobj(self.s3_bucket, metadata_key, f)
                
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                logger.info(f"Metadata downloaded: {metadata}")
                return metadata
                
            except ClientError:
                logger.warning("Metadata file not found, skipping validation")
                return None
            
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            raise
        except ClientError as e:
            logger.error(f"S3 download failed: {str(e)}")
            raise
    
    def validate_backup(self, expected_checksum=None):
        """Validate backup file integrity"""
        logger.info("Validating backup file integrity")
        
        if not self.backup_path.exists():
            raise Exception(f"Backup file not found: {self.backup_path}")
        
        # Calculate checksum
        logger.info("Calculating checksum...")
        sha256 = hashlib.sha256()
        with open(self.backup_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        checksum = sha256.hexdigest()
        logger.info(f"Calculated checksum: {checksum}")
        
        # Compare with expected checksum
        if expected_checksum:
            if checksum == expected_checksum:
                logger.info("✅ Checksum validation passed")
                return True
            else:
                logger.error("❌ Checksum validation FAILED")
                logger.error(f"Expected: {expected_checksum}")
                logger.error(f"Actual:   {checksum}")
                raise Exception("Backup file corrupted - checksum mismatch")
        else:
            logger.warning("No expected checksum provided, skipping validation")
            return True
    
    def restore_database(self):
        """Restore database from backup file"""
        logger.info(f"Starting database restore to: {self.db_config['name']}")
        
        # Warning prompt
        print("\n" + "="*80)
        print("⚠️  WARNING: DATABASE RESTORE")
        print("="*80)
        print(f"This will REPLACE the current database: {self.db_config['name']}")
        print(f"Host: {self.db_config['host']}:{self.db_config['port']}")
        print(f"Backup: {self.backup_filename}")
        print("\nAll current data will be LOST!")
        print("="*80)
        
        response = input("\nType 'RESTORE' to continue: ")
        if response != 'RESTORE':
            logger.info("Restore cancelled by user")
            return False
        
        try:
            # Close all Django connections
            connection.close()
            
            # Build pg_restore command
            pg_restore_cmd = [
                'pg_restore',
                '--host', self.db_config['host'],
                '--port', str(self.db_config['port']),
                '--username', self.db_config['user'],
                '--dbname', self.db_config['name'],
                '--clean',      # Drop existing objects
                '--if-exists',  # Don't error if objects don't exist
                '--no-owner',   # Don't restore ownership
                '--no-acl',     # Don't restore access privileges
                '--verbose',
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # Decompress and restore
            logger.info("Decompressing and restoring database...")
            
            with gzip.open(self.backup_path, 'rb') as f_in:
                process = subprocess.Popen(
                    pg_restore_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                
                # Stream decompressed data to pg_restore
                for chunk in iter(lambda: f_in.read(8192), b''):
                    process.stdin.write(chunk)
                
                process.stdin.close()
                process.wait()
                
                # Note: pg_restore may return non-zero for warnings
                stderr_output = process.stderr.read().decode()
                
                if process.returncode != 0:
                    # Check if it's just warnings
                    if 'ERROR' in stderr_output:
                        raise Exception(f"pg_restore failed:\n{stderr_output}")
                    else:
                        logger.warning(f"pg_restore warnings:\n{stderr_output}")
            
            logger.info("✅ Database restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            raise
    
    def verify_restore(self):
        """Verify database restoration was successful"""
        logger.info("Verifying database restoration...")
        
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Check table count
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                logger.info(f"✅ Tables found: {table_count}")
                
                # Check key tables exist
                key_tables = [
                    'accounts_customuser',
                    'vehicles_vehicle',
                    'deals_deal',
                    'payments_payment',
                    'shipments_shipment'
                ]
                
                for table in key_tables:
                    cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_name = %s
                    """, [table])
                    
                    if cursor.fetchone()[0] == 1:
                        # Count rows
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        row_count = cursor.fetchone()[0]
                        logger.info(f"✅ {table}: {row_count} rows")
                    else:
                        logger.error(f"❌ Table missing: {table}")
                
                logger.info("✅ Database verification completed")
                return True
                
        except Exception as e:
            logger.error(f"Database verification failed: {str(e)}")
            return False
    
    def cleanup_local(self):
        """Remove local backup file"""
        try:
            if self.backup_path.exists():
                self.backup_path.unlink()
                logger.info(f"Local backup file removed: {self.backup_path}")
            
            metadata_path = self.temp_dir / self.metadata_filename
            if metadata_path.exists():
                metadata_path.unlink()
                logger.info(f"Metadata file removed: {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup local files: {str(e)}")
    
    def run(self, dry_run=False):
        """Execute full restore workflow"""
        logger.info("Starting restore workflow")
        
        try:
            # Step 1: Download from S3
            metadata = self.download_from_s3()
            
            # Step 2: Validate backup
            expected_checksum = metadata.get('checksum') if metadata else None
            self.validate_backup(expected_checksum)
            
            if dry_run:
                logger.info("DRY RUN MODE - Stopping before restore")
                self.cleanup_local()
                return True
            
            # Step 3: Restore database
            success = self.restore_database()
            
            if not success:
                return False
            
            # Step 4: Verify restore
            self.verify_restore()
            
            # Step 5: Cleanup
            self.cleanup_local()
            
            logger.info("✅ Restore workflow completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Restore workflow failed: {str(e)}")
            self.cleanup_local()
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Restore database from S3 backup')
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available backups'
    )
    parser.add_argument(
        '--backup',
        type=str,
        help='Specific backup filename to restore'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Restore the latest daily backup'
    )
    parser.add_argument(
        '--type',
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='Backup type for --latest option'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test restore without actually restoring database'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BACKUP_BUCKET']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Set them in .env file or environment")
        sys.exit(1)
    
    # Handle list command
    if args.list:
        restore = DatabaseRestore()
        restore.list_available_backups()
        sys.exit(0)
    
    # Determine backup filename
    backup_filename = None
    
    if args.latest:
        restore = DatabaseRestore()
        backup_filename = restore.get_latest_backup(args.type)
        if not backup_filename:
            logger.error("No backups found")
            sys.exit(1)
    elif args.backup:
        backup_filename = args.backup
    else:
        logger.error("Must specify --backup, --latest, or --list")
        parser.print_help()
        sys.exit(1)
    
    # Run restore
    try:
        restore = DatabaseRestore(backup_filename)
        success = restore.run(dry_run=args.dry_run)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
