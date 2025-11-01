# Student_Management_System

## Installation Guide

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

Development mode (recommended):

```bash
pip install -e .[dev]
```

Runtime only (minimal install):

```bash
pip install -e .
```

---

### Step 3: Run the Application

- Run the shim launcher at project root:

```bash
  python main.py
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

src/  
├─ models/        # data layer classes (e.g. User, Payment, Announcement)  
├─ views/         # GUI code (Tkinter windows and dialogs)  
├─ controllers/   # application logic linking views and models  
├─ main.py        # application entry point (initializes MVC and starts app)  
