#!/bin/sh

# Container will run migrations before app starts.
flask db upgrade

exec gunicorn --bind 0.0.0.0:80 "app:create_app()"