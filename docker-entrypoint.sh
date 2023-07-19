#!/bin/sh

# Container will run migrations before app starts.
flask db upgrade

# Start the server with a timeout of 120 seconds
exec gunicorn --bind 0.0.0.0:80 --timeout 120 "app:create_app()"