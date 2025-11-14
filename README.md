# Student_Management_System

## Testing report

[![Pytest report](https://img.shields.io/badge/pytest-report--latest-blue?logo=pytest&logoColor=white)](https://zombieTDV.github.io/Student-Management-System/latest-report/)

## Installation / Running Guide

### Prerequisites

- Python **3.9 or higher** (3.12 recommended)
- Git installed

---

### Step 1: Create Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

- On Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

- On macOS/Linux:

```bash
source .venv/bin/activate
```

---

### Step 2: Install the Project

Development (recommended):

```bash
pip install -e .[dev]
```
---

### Step 3: Create a .env files, in that you need to have the following Variables

```bash
MONGO_URL=????
MONGO_DB=Student_Management_System
EMAIL_USER="huh37394@gmail.com"
EMAIL_PASSWORD="emwq wlmg soke zlyh"
```

**MONGO_URL** *is the url that contain the account and password to access the DataBase, it will be given by the DataBase Manager, it not, please contact with him*

**EMAIL_USER** *and* **EMAIL_PASSWORD** *are the email service account (not the student or admin account's email)*

---

### Step 4: Run the Application

- Run the shim launcher at project root:

```bash
python src/main.py
```

---

## Contributing

We use pre-commit hooks to enforce style and quality checks (black, flake8, etc.).

### Setup pre-commit

```bash
pip install pre-commit
```

```bash
pre-commit install
```

Now, checks will run automatically before each commit.
To run them manually on all files:

```bash
pre-commit run --all-files
```

Our configuration lints all .py files in src/, tests/, and the project root (e.g. main.py).

---

## Development Notes

-Use pip==25.2.3 to ensure compatibility with pip-tools 7.5.1

## Project structure

```
📦src
 ┣ 📂controllers
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜admin_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜auth_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜fee_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜financial_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜notifications_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜payment_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜re.cpython-312.pyc
 ┃ ┃ ┣ 📜signup.cpython-312.pyc
 ┃ ┃ ┣ 📜student_controller.cpython-312.pyc
 ┃ ┃ ┣ 📜transaction_controller.cpython-312.pyc
 ┃ ┃ ┗ 📜__init__.cpython-312.pyc
 ┃ ┣ 📜admin_controller.py
 ┃ ┣ 📜auth_controller.py
 ┃ ┣ 📜fee_controller.py
 ┃ ┣ 📜financial_controller.py
 ┃ ┣ 📜notifications_controller.py
 ┃ ┣ 📜payment_controller.py
 ┃ ┣ 📜student_controller.py
 ┃ ┣ 📜transaction_controller.py
 ┃ ┗ 📜__init__.py
 ┣ 📂models
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜account.cpython-312.pyc
 ┃ ┃ ┣ 📜admin.cpython-312.pyc
 ┃ ┃ ┣ 📜announcement.cpython-312.pyc
 ┃ ┃ ┣ 📜database.cpython-312.pyc
 ┃ ┃ ┣ 📜fee.cpython-312.pyc
 ┃ ┃ ┣ 📜student.cpython-312.pyc
 ┃ ┃ ┣ 📜transaction.cpython-312.pyc
 ┃ ┃ ┗ 📜__init__.cpython-312.pyc
 ┃ ┣ 📜account.py
 ┃ ┣ 📜admin.py
 ┃ ┣ 📜announcement.py
 ┃ ┣ 📜database.py
 ┃ ┣ 📜fee.py
 ┃ ┣ 📜student.py
 ┃ ┣ 📜test.py
 ┃ ┣ 📜transaction.py
 ┃ ┗ 📜__init__.py
 ┣ 📂Student_Management_System.egg-info
 ┃ ┣ 📜dependency_links.txt
 ┃ ┣ 📜PKG-INFO
 ┃ ┣ 📜requires.txt
 ┃ ┣ 📜SOURCES.txt
 ┃ ┗ 📜top_level.txt
 ┣ 📂utils
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜email_service.cpython-312.pyc
 ┃ ┃ ┗ 📜__init__.cpython-312.pyc
 ┃ ┣ 📜config.py
 ┃ ┣ 📜email_service.py
 ┃ ┗ 📜__init__.py
 ┣ 📂views
 ┃ ┣ 📂admin
 ┃ ┃ ┣ 📂__pycache__
 ┃ ┃ ┃ ┣ 📜admin_dashboard.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜admin_management.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜fee_management.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜make_anoucements.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜notification_management.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜student_management.cpython-312.pyc
 ┃ ┃ ┃ ┗ 📜transaction_management.cpython-312.pyc
 ┃ ┃ ┣ 📜admin_dashboard.py
 ┃ ┃ ┣ 📜admin_management.py
 ┃ ┃ ┣ 📜fee_management.py
 ┃ ┃ ┣ 📜make_anoucements.py
 ┃ ┃ ┣ 📜notification_management.py
 ┃ ┃ ┣ 📜student_management.py
 ┃ ┃ ┗ 📜transaction_management.py
 ┃ ┣ 📂student
 ┃ ┃ ┣ 📂__pycache__
 ┃ ┃ ┃ ┣ 📜financial_summary.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜payment.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜student_dashboard.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜student_dashboard_view_notifications.cpython-312.pyc
 ┃ ┃ ┃ ┣ 📜student_profile.cpython-312.pyc
 ┃ ┃ ┃ ┗ 📜update_student_profile.cpython-312.pyc
 ┃ ┃ ┣ 📜financial_summary.py
 ┃ ┃ ┣ 📜payment.py
 ┃ ┃ ┣ 📜student_dashboard.py
 ┃ ┃ ┣ 📜student_dashboard_view_notifications.py
 ┃ ┃ ┣ 📜student_profile.py
 ┃ ┃ ┗ 📜update_student_profile.py
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜admin_dashboard.cpython-312.pyc
 ┃ ┃ ┣ 📜email_sent.cpython-312.pyc
 ┃ ┃ ┣ 📜financial_summary.cpython-312.pyc
 ┃ ┃ ┣ 📜forgot_password.cpython-312.pyc
 ┃ ┃ ┣ 📜login.cpython-312.pyc
 ┃ ┃ ┣ 📜make_anoucements.cpython-312.pyc
 ┃ ┃ ┣ 📜notification_detail.cpython-312.pyc
 ┃ ┃ ┣ 📜payment.cpython-312.pyc
 ┃ ┃ ┣ 📜student_dashboard.cpython-312.pyc
 ┃ ┃ ┣ 📜student_dashboard_view_notifications.cpython-312.pyc
 ┃ ┃ ┣ 📜student_management.cpython-312.pyc
 ┃ ┃ ┣ 📜student_profile.cpython-312.pyc
 ┃ ┃ ┣ 📜update_student_profile.cpython-312.pyc
 ┃ ┃ ┗ 📜__init__.cpython-312.pyc
 ┃ ┣ 📜forgot_password.py
 ┃ ┣ 📜login.py
 ┃ ┣ 📜notification_detail.py
 ┃ ┗ 📜__init__.py
 ┗ 📜main.py
```