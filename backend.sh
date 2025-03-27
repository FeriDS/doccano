#!/bin/bash
cd backend || exit
export DATABASE_URL="postgres://doccano_admin:doccano_pass@localhost:5432/doccano?sslmode=disable"
poetry run python manage.py runserver

