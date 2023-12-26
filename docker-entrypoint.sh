#!/bin/sh

# Running database migrations in production

# Container will run migrations before app starts.
flask db upgrade

# Start the server
exec gunicorn --bind 0.0.0.0:80 "app:create_app()" --timeout 120