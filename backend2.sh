#!/bin/bash

source .venv/bin/activate
cd backend
celery --app=config worker --loglevel=INFO --concurrency=1
