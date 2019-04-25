import os
try:
    from celery import Celery
except ImportError:
    import celery



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashtarg.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('cashtarg')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

'''
app.conf.beat_schedule = {
    'send-reminder-every-day' : {
        'task': 'invoice.tasks.send_automated_reminder',
        'schedule': ''
    }

}

'''