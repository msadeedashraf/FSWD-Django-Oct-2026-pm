# Part 1 — Create the Project Environment

## Step 1. Create the project folder

Open PowerShell or Command Prompt and run:

```powershell
mkdir jobzila
cd jobzila
```

This folder will hold the full Django project.

---

## Step 2. Create a virtual environment

```powershell
py -m venv .venv
```

A virtual environment keeps this project’s packages separate from other Python projects.

---

## Step 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see something like this at the start of your terminal:

```powershell
(.venv)
```

That means the virtual environment is active.

---

## Step 4. Install Django

```powershell
pip install Django
```

Check that Django installed correctly:

```powershell
pip list
```

---

## Step 5. Save installed packages

```powershell
pip freeze > requirements.txt
```

This creates a list of packages needed for the project.

Later, another student can install the same packages using:

```powershell
pip install -r requirements.txt
```

---

# Part 2 — Start the Django Project

## Step 6. Create the Django project

```powershell
django-admin startproject myproject
cd myproject
```

Your folder structure should look like this:

```text
jobzila/
│
├── .venv/
├── requirements.txt
└── myproject/
    ├── manage.py
    └── myproject/
        ├── __init__.py
        ├── settings.py
        ├── urls.py
        ├── asgi.py
        └── wsgi.py
```

---

## Step 7. Run the server

```powershell
py .\manage.py runserver
```

Open this in your browser:

```text
http://127.0.0.1:8000/
```

If you see the Django welcome page, your project is working.

---


# Part 3 — Create Basic Pages

At first, we will create simple pages using Django views.

## Step 8. Create `views.py`

Inside this folder:

```text
myproject/myproject/
```

Create a new file called:

```text
views.py
```

Add this code:

```python
from django.http import HttpResponse


def homepage(request):
    return HttpResponse("Welcome to JobZila Home Page")


def contact(request):
    return HttpResponse("Contact JobZila")
```

---

## Step 9. Connect views to URLs

Open:

```text
myproject/myproject/urls.py
```

Update it:

```python
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.homepage),
    path("contact/", views.contact),
]
```

Test these URLs:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/contact/
```

At this point, Django is sending plain text responses.

---


