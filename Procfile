web: gunicorn cashtarg.wsgi --pythonpath cashtarg
worker: celery worker -A cashtarg -l info
beat: celery -A cashtarg beat --loglevel=info