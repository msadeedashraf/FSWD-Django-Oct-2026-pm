## JobZila v3: Adding Jobs App 

# Part 5 — Create the Jobs App

Now we will create a proper Django app for job listings.

## Step 18. Create the jobs app

```powershell
py .\manage.py startapp jobs
```

Django will create:

```text
jobs/
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── views.py
└── migrations/
```

---

## Step 19. Register the app

Open:

```text
myproject/myproject/settings.py
```

Add `jobs` inside `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "jobs",
]
```

---

## Step 20. Create the Job model

Open:

```text
jobs/models.py
```

Add:

```python
from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    apply_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"
```

This model represents one job post.

---

## Step 21. Create and apply migrations

Whenever you create or change a model, run:

```powershell
py .\manage.py makemigrations
py .\manage.py migrate
```

This creates the database table for jobs.

---

# Part 6 — Use the Admin Panel

## Step 22. Create an admin user

```powershell
py .\manage.py createsuperuser
```

Enter username, email, and password.

Then run the server:

```powershell
py .\manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

---

## Step 23. Register the Job model in admin

Open:

```text
jobs/admin.py
```

Add:

```python
from django.contrib import admin
from .models import Job


admin.site.register(Job)
```

Refresh the admin panel. You should now see **Jobs**.

Add a few sample jobs from the admin panel.

---

# Part 7 — Show Jobs on the Website

## Step 24. Create jobs URLs

Create:

```text
jobs/urls.py
```

Add:

```python
from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
]
```

---

## Step 25. Connect jobs URLs to the main project

Open:

```text
myproject/myproject/urls.py
```

Update:

```python
from django.contrib import admin
from django.urls import path, include
from . import views

from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("job-search/", views.job_search, name="job_search"),
    path("job-listing/", views.job_listing, name="job_listing"),
    path("jobs/", include("jobs.urls")),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
]

```

---

## Step 26. Create the job list view

Open:

```text
jobs/views.py
```

Add:

```python
from django.shortcuts import render
from .models import Job

# Create your views here.

def job_list(request):
    jobs = Job.objects.all().order_by("-created_at")
    return render(request, "jobs/job_list.html", {"jobs": jobs})

```

---

## Step 27. Create the job list template

Create this folder:

```text
jobs/templates/jobs/
```

Inside it, create:

```text
job_list.html
```

Add:

```html
{% extends 'sharedpage.html' %}

{% block title %}Job Listing | JobZila{% endblock title %}

{% block main %}


<section class="jobs-listing-section">
    
    <h2>Job Listing New</h2>
    
    {% for job in jobs %}
            <div class="jobs-listing">
                <h3>{{job.title}}</h3>
              <p>{{job.company}}</p>
              <p>{{job.location}}</p>
              <p>
                {{job.description}}
              </p>

            </div>

           
            {% endfor %}

        </section>





 
{% endblock main %}

```

- Add a new jobs page link to replace the jobs listing page

```html 
<li><a href="{% url 'jobs:job_list' %}">Jobs</a></li>
```

Open:

```text
jobzilav3_app/jobzilav3/templates/sharedpage.html
```


```html
{% load static %}
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}JobZila{% endblock title %}</title>
    <link rel="stylesheet" href="{% static 'css/styles.css' %}" />
  </head>
  <body>
    <header>
      <h1>JobZila</h1>

      <nav class="navbar">
        <button
          class="menu-toggle"
          type="button"
          aria-label="Open navigation menu"
          aria-expanded="false"
          aria-controls="main-menu"
        >
          ☰
        </button>

        <ul id="main-menu" class="nav-menu">
          <li><a href="{% url 'home' %}">Home</a></li>
          <li><a href="{% url 'job_search' %}">Job Search</a></li>
          <!-- <li><a href="{% url 'job_listing' %}">Job Listing</a></li> -->
          <li><a href="{% url 'jobs:job_list' %}">Jobs</a></li>
          <li><a href="{% url 'terms' %}">Terms of Service</a></li>
          <li><a href="{% url 'privacy' %}">Privacy Policy</a></li>
          <li><a href="{% url 'contact' %}">Contact</a></li>
        </ul>
      </nav>
    </header>

    <main>
      {% block main %}{% endblock main %}
    </main>

    <footer>
      <p>
        &copy; 2026 JobZila. All rights reserved.
        <a href="{% url 'contact' %}">Contact Us</a> |
        <a href="{% url 'terms' %}">Terms</a> |
        <a href="{% url 'privacy' %}">Privacy</a>
      </p>
    </footer>

    <script src="{% static 'js/menu.js' %}"></script>
  </body>
</html>



```




Test:

```text
http://127.0.0.1:8000/jobs/
```

---