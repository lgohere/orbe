"""
Celery configuration for ORBE Platform
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orbe_platform.settings')

app = Celery('orbe_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    # D-0 Reminders: Send at 9:00 AM daily for fees due today
    'send-membership-reminders-daily': {
        'task': 'finance.send_membership_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    # D+3 Overdue Reminders: Send at 9:00 AM daily for fees 3 days overdue
    'send-overdue-reminders-daily': {
        'task': 'finance.send_overdue_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    # Update Overdue Status: Run at midnight daily
    'update-overdue-status-daily': {
        'task': 'finance.update_overdue_status',
        'schedule': crontab(hour=0, minute=0),
    },
    # Generate Monthly Fees: Run on 1st of each month at 1:00 AM
    'generate-monthly-fees': {
        'task': 'finance.generate_monthly_fees',
        'schedule': crontab(day_of_month=1, hour=1, minute=0),
    },
}

app.conf.timezone = 'America/Sao_Paulo'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')