#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations warehouse --no-input
python manage.py migrate warehouse --no-input

echo "Collect static files"
python manage.py collectstatic --no-input


echo "Loading items"
python manage.py loaddata items.json --ignorenonexistent


# Start server
echo "Starting server"
gunicorn \
  --bind 0.0.0.0:$PORT \
  service.wsgi:application
