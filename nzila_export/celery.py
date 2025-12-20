"""
Celery configuration for asynchronous task processing
Required for scalable production deployment
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')

app = Celery('nzila_export')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-exchange-rates-daily': {
        'task': 'payments.tasks.update_exchange_rates',
        'schedule': crontab(hour=0, minute=30),  # Run daily at 12:30 AM
    },
    'check-stalled-deals-daily': {
        'task': 'deals.tasks.check_stalled_deals',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    'send-shipment-updates': {
        'task': 'shipments.tasks.send_shipment_updates',
        'schedule': crontab(hour='*/6'),  # Run every 6 hours
    },
    'process-pending-commissions': {
        'task': 'commissions.tasks.process_pending_commissions',
        'schedule': crontab(hour=10, minute=0, day_of_week='monday'),  # Weekly on Monday
    },
    'cleanup-old-audit-logs': {
        'task': 'nzila_export.tasks.cleanup_old_audit_logs',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),  # Monthly cleanup
    },
    'send-payment-reminders-daily': {
        'task': 'payments.tasks.send_payment_reminders',
        'schedule': crontab(hour=10, minute=0),  # Run daily at 10 AM
    },
    'check-delayed-shipments': {
        'task': 'shipments.tasks.check_delayed_shipments',
        'schedule': crontab(hour=8, minute=0),  # Run daily at 8 AM
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Toronto',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
