#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."

python -c "
import os
import socket
import time

host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', '5432'))

for attempt in range(30):
    try:
        with socket.create_connection((host, port), timeout=2):
            print('PostgreSQL is available')
            break
    except OSError:
        print(f'Attempt {attempt + 1}/30: PostgreSQL is not ready yet')
        time.sleep(2)
else:
    raise SystemExit('Could not connect to PostgreSQL in time')
"

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
