import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skybooker.settings')

app = Celery('skybooker')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

