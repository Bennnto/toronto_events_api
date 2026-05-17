web: gunicorn events.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
worker: celery -A events worker --beat --schedule=/tmp/celerybeat-schedule --loglevel=info --concurrency=2
