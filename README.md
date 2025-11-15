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

#### Option 1: Run via Python

```bash
python src/main.py
```

#### Option 2: Run via Docker (Window WSL or Linux)

1. Build the Docker image:

```bash
docker build -t student-management-app .
```

2. Run the container:

```bash
docker run -d -p 5000:5000 student-management-app
```

3. Run the container with environment variables and GUI support:

```bash
sudo docker run -it --rm \
    --network="host" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    --env-file .env \
    student-management-app
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
 ┣ 📂models
 ┣ 📂utils
 ┣ 📂views
 ┗ 📜main.py
```