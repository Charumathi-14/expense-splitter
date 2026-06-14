#!/bin/sh
set -e

# Run migrations then start Gunicorn
python manage.py migrate --noinput
exec gunicorn expense_manager.wsgi:application --bind 0.0.0.0:8000