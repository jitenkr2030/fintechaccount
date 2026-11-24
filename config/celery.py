"""Celery configuration for fintechaccountant.

Background tasks: email notifications, certificate generation, video transcoding
notifications, payment verification, scheduled job alerts.
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('fintechaccountant')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
