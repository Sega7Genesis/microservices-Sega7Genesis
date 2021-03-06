#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations warranty --no-input
python manage.py migrate warranty --no-input

echo "Collect static files"
python manage.py collectstatic --no-input


echo "Loading items"
python manage.py loaddata warranty.json --ignorenonexistent



# Start server
echo "Starting server"
gunicorn \
  --bind 0.0.0.0:$PORT \
  service.wsgi:application
