import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Redis is both the broker and the result backend, on separate databases so
# queued messages and stored results never share keyspace. Both come from the
# CELERY_* keys of the single settings module, which reads them from `.env`.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, name='core.debug_task')
def debug_task(self):
    """Minimal task used to validate the worker and the result backend."""
    return f'ok from {self.request.hostname}'
