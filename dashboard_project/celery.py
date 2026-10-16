import os
from celery import Celery

# Django settings module set karo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')

app = Celery('dashboard_project')

# Django settings se Celery config load karo (CELERY_ prefix ke saath)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Saare installed apps se tasks auto-discover karo
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')