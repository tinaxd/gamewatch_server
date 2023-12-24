#!/bin/bash

# read from env
processes=$PROCESS_NUM

python manage.py collectstatic --noinput && \
python manage.py migrate && \
uwsgi --socket=:49152 --http=:49153 --processes=$processes --module=gamewatch.wsgi:application
