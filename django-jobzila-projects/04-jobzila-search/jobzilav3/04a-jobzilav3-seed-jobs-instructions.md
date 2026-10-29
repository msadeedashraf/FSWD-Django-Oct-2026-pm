# JobZila v3 — Load Dummy Jobs into SQLite

**Short practical exercise | Prerequisite:** The JobZila v3 project from Module 03, with the `jobs` app and `Job` model already created.

## Step 1 — Open the Django project

Open the project in VS Code and open its terminal. Navigate to the folder containing `manage.py`.

If you already created a virtual environment, activate it (from the folder containing `.venv`):

```powershell
.\.venv\Scripts\Activate.ps1
```

> Your `.venv` folder may be one directory above `manage.py`. Activate the existing environment rather than creating a new one.

## Step 2 — Add the management command

Inside the existing `jobs` app, create the following folders and files:

```text
jobs/
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── seed_jobs.py
├── models.py
└── views.py
```

Copy the supplied **`seed_jobs.py`** into `jobs/management/commands/seed_jobs.py`. The two `__init__.py` files can be empty.

## Step 3 — Make sure the database is ready

From the directory containing `manage.py`, run:

```powershell
python manage.py migrate
python manage.py check
```

The `jobs` app must already be listed in `INSTALLED_APPS` and its model migration must have been created in Module 03. If you changed the model since then, run `python manage.py makemigrations jobs` followed by `python manage.py migrate`.

## Step 4 — Insert 100 sample jobs

```powershell
python manage.py seed_jobs --count 100
```

Example output on a database with one existing job:

```text
Created 100 new jobs. Total jobs in database: 101.
```

The exact numbers depend on existing records. The script avoids inserting another job with the same **title, company, and location**.

## Step 5 — Verify in the browser

Start Django:

```powershell
python manage.py runserver
```

Open **http://127.0.0.1:8000/jobs/** and test searches such as `Python`, `Toronto`, and `Data Analyst`. You can also check the records at **http://127.0.0.1:8000/admin/** if you created a superuser and registered the `Job` model.

## Optional commands

```powershell
# Request 50 sample combinations
python manage.py seed_jobs --count 50

# Delete ALL existing jobs, then generate 100 fresh samples
python manage.py seed_jobs --clear --count 100
```

**Warning:** `--clear` permanently deletes existing job records, including any real listings. Only use it in a disposable classroom database. Running the normal command again may create **zero** new records because the same sample combinations already exist.

**Expected result:** Your existing SQLite database (`db.sqlite3` by default) contains sample jobs ready for the search lesson. No direct SQLite editing is required.
