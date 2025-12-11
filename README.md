# DevSuite

DevSuite is a comprehensive management system designed for developers and agencies to streamline client management, project tracking, finance, and productivity.

## Features

-   **Client Management**: Track clients, contact details, and unique short codes.
-   **Project Management**: Manage projects, milestones, and tasks with deadlines.
-   **Service Management**: Track recurring services (domains, hosting) and their expiry dates.
-   **Finance**: Generate invoices, track payments, and manage expenses.
-   **Productivity**: Log time entries and track duration for projects.
-   **Automated Notifications**: Email alerts for deadlines, due dates, and service expirations.

## Modules

The project is organized into the following core modules in `src/models/`:

-   **Clients** (`clients.py`): `Client` model.
-   **Projects** (`projects.py`): `Project`, `Milestone`, `Task` models.
-   **Services** (`services.py`): `Service`, `Credential` models.
-   **Finance** (`finance.py`): `Invoice`, `Payment`, `Expense` models.
-   **Productivity** (`productivity.py`): `TimeEntry`, `Note` models.
-   **Notifications** (`notifications.py`): `Notification` model and sending logic.

## Setup

### Prerequisites
-   Python 3.10+
-   `just` (optional, for command shortcuts)

### Installation

#### Using Just (Recommended)

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/S4NKALP/DevSuite.git
    cd DevSuite
    ```

2.  **Configure Environment**:
    Copy `.env.sample` to `.env` and update the values:
    ```bash
    cp .env.sample .env
    ```

3.  **Run Setup**:
    This installs dependencies, runs migrations, and creates a superuser.
    ```bash
    just setup
    ```

4.  **Run Server**:
    ```bash
    just dev
    ```

#### Traditional Method

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Copy `.env.sample` to `.env` and update the values:
    ```bash
    cp .env.sample .env
    ```

3.  **Initialize Database**:
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

4.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

## Notifications

DevSuite includes an automated email notification system.

-   **Triggers**: Project deadlines, Milestone due dates, Service expiry, Invoice due dates.
-   **Command**: `python manage.py send_notifications`
-   **Automation**: Use `scripts/run_notifications.sh` in a cron job.

For detailed documentation, see [notifi.md](notifi.md).

## Testing

Run the full test suite with:

```bash
python manage.py test
```

For detailed testing documentation, see [testing.md](testing.md).

## Management Commands

-   `send_notifications`: Checks for upcoming events and sends emails.
    ```bash
    python manage.py send_notifications
    ```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage all records.
