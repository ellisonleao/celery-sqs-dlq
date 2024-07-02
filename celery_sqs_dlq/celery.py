import os

from celery import Celery

from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery_sqs_dlq.settings")

app = Celery()
app.config_from_object(settings.CELERY)
app.autodiscover_tasks()
