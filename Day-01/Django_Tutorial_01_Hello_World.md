# Django Tutorial 01 — Your First Hello World Application

**Level:** Beginner  
**Duration:** 45–60 minutes  
**Environment:** Windows, VS Code, Python

## Learning Objectives

By the end of this lesson, students will be able to install Django, create a project and app, run the development server, create a view, configure URL routing, and display **Hello World** in a browser.

## 1. Prerequisites

Install Python and Visual Studio Code (VS Code). Open **Terminal → New Terminal** in VS Code.

Check Python and pip:

```powershell
python --version
python -m pip --version
```

## 2. Create a Project Folder

```powershell
mkdir DjangoLearning
cd DjangoLearning
code .
```

## 3. Create and Activate a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Your terminal prompt should now begin with `(.venv)`.

If PowerShell blocks activation, run this command and retry activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

The policy change applies only to the current PowerShell process.

## 4. Install Django

```powershell
python -m pip install django
python -m django --version
```

The version printed depends on the version installed.

## 5. Create Your Django Project

```powershell
django-admin startproject myproject .
```

The final dot (`.`) means to place the project in the current directory.

Expected structure:

```text
DjangoLearning/
├── .venv/
├── manage.py
└── myproject/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

| File | Purpose |
|---|---|
| `manage.py` | Run Django management commands |
| `settings.py` | Configure the project |
| `urls.py` | Route incoming URLs |
| `asgi.py` | ASGI server entry point |
| `wsgi.py` | WSGI server entry point |
| `__init__.py` | Mark the directory as a Python package |

## 6. Start the Development Server

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. You should see Django's default installation success page.

Stop the server with **Ctrl+C**.

> The development server is for learning and development, not production hosting.

## 7. Create Your First App

```powershell
python manage.py startapp hello
```

Updated structure:

```text
DjangoLearning/
├── .venv/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── hello/
    ├── migrations/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    └── views.py
```

A **project** contains overall configuration; an **app** groups related functionality.

## 8. Register the App

Open `myproject/settings.py`. Add `'hello',` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hello',
]
```

## 9. Create a View

Open `hello/views.py`:

```python
from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello World! Welcome to Django.")
```

- `home()` is a **view function**.
- `request` is the incoming HTTP request.
- `HttpResponse` creates the response returned to the browser.

## 10. Configure URL Routing

Create a new file named `hello/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
```

Update `myproject/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hello.urls')),
]
```

The project router delegates requests to the app router; the app router selects the view.

## 11. Run Hello World

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

Expected browser output:

```text
Hello World! Welcome to Django.
```

## 12. Understand the Request Flow

```text
Browser requests http://127.0.0.1:8000/
                  |
                  v
        myproject/urls.py
                  |
                  v
           hello/urls.py
                  |
                  v
      hello/views.py: home()
                  |
                  v
          HttpResponse(...)
                  |
                  v
       Browser displays text
```

The browser sends an HTTP request, Django resolves the URL, calls the matching view, and returns an HTTP response.

## 13. Student Exercises

### Exercise A: About Page

Add this function to `hello/views.py`:

```python
def about(request):
    return HttpResponse("This is my About page.")
```

Add this entry to the existing `urlpatterns` list in `hello/urls.py`:

```python
path('about/', views.about, name='about'),
```

Test <http://127.0.0.1:8000/about/>.

### Exercise B: Contact Page

Add this function to `hello/views.py`:

```python
def contact(request):
    return HttpResponse("Contact us at hello@example.com")
```

Add this URL entry:

```python
path('contact/', views.contact, name='contact'),
```

Test <http://127.0.0.1:8000/contact/>.

### Exercise C: Student Page

Independently create a `/student/` route that displays:

```text
Hello! My name is John and I am learning Django.
```

Test <http://127.0.0.1:8000/student/>.

## 14. Complete Reference Code

**`hello/views.py`**

```python
from django.http import HttpResponse


def home(request):
    return HttpResponse("Hello World! Welcome to Django.")


def about(request):
    return HttpResponse("This is my About page.")


def contact(request):
    return HttpResponse("Contact us at hello@example.com")


def student(request):
    return HttpResponse(
        "Hello! My name is John and I am learning Django."
    )
```

**`hello/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('student/', views.student, name='student'),
]
```

**`myproject/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hello.urls')),
]
```

## 15. Knowledge Check

1. What does `manage.py` do?
2. What is the difference between a Django project and an app?
3. Which file typically contains view functions?
4. What does `path('', views.home, name='home')` mean?
5. What does `HttpResponse` return?
6. Why do we use `include('hello.urls')`?

## 16. Common Errors

| Error | Solution |
|---|---|
| `No module named django` | Activate `.venv` and install Django |
| `django-admin` not recognized | Use `python -m django startproject myproject .` |
| `Page not found (404)` | Verify the URL patterns and path |
| `No module named hello.urls` | Create `hello/urls.py` and check spelling |
| Address already in use | Stop the other server or run `python manage.py runserver 8001` |
| PowerShell activation blocked | Apply the process-scoped policy command from Step 3 |

## 17. Next Lesson

**Django Templates:** Replace `HttpResponse("Hello World")` with an HTML template rendered using Django's `render()` function, introducing the Model–Template–View (MTV) architecture.
