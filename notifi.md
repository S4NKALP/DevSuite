# Notification System Workflow

This document outlines how the notification system works in DevSuite.

## Overview
The system automatically checks for upcoming deadlines, due dates, and other time-sensitive events and sends email notifications to Clients and Admins.

## Triggers & Recipients

The system checks for the following events daily:

| Module | Event | Condition | Recipient |
| :--- | :--- | :--- | :--- |
| **Projects** | Project Deadline | Deadline is **tomorrow** | Client & Admin |
| **Projects** | Milestone Due | Due date is **tomorrow** | Client & Admin |
| **Projects** | Task Due | Due date is **tomorrow** | Admin |
| **Services** | Service Expiry | Expiry date is **tomorrow** | Client |
| **Finance** | Invoice Due | Due date is **tomorrow** | Client |
| **Productivity** | Time Entry Logged | Completed in last **24 hours** | Admin |

## How It Works

1.  **Command**: The logic is encapsulated in a Django management command:
    ```bash
    python manage.py send_notifications
    ```
2.  **Logic**:
    -   It queries the database for objects matching the conditions above.
    -   It generates an email with relevant details.
    -   It records the notification in the `Notification` model to prevent duplicates (for the same day).
    -   It sends the email using the configured `EMAIL_BACKEND`.

## Automation

To ensure notifications are sent daily, a cron job is used.

**Script**: `scripts/run_notifications.sh`

**Setup**:
Add this to your crontab (`crontab -e`) to run daily at 9:00 AM:
```bash
0 9 * * * /path/to/devsuite/scripts/run_notifications.sh >> /path/to/devsuite/logs/cron.log 2>&1
```

## Configuration

-   **Admin Emails**: Configured in `src/settings/base.py` under `ADMINS`.
-   **Email Backend**: Configured in `src/settings/base.py` (default is console for dev, SMTP for prod).
