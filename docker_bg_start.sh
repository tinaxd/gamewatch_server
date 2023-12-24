#!/bin/bash

celery -A gamewatch.background worker -E --loglevel=INFO
