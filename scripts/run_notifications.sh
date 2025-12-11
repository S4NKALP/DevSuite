#!/bin/bash
# Script to run daily notifications
# Add this to crontab: 0 9 * * * /path/to/devsuite/scripts/run_notifications.sh

cd "$(dirname "$0")/.." || exit
source .venv/bin/activate
python manage.py send_notifications
