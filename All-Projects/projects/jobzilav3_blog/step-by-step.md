## Starting code is jobzilav3_job_search

[starter code](/Day-04/projects/jobzilav3_job_search/)


### 

## JobZila v3: Adding Blog App 

# Part 5 — Create the Blog App

Now we will create a proper Django app for Blogs.

## Step 18. Create the Blogs app

```powershell
py .\manage.py startapp blogs
```

Django will create:

```text
blogs/
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

Add `blogs` inside `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "jobs",
    "blogs",
]
```

---

## Step 20. Create the Blog model

Open:

```text
blog/models.py
```

```
 python -m pip install Pillow
```


Add:

```python
from django.db import models
from django.contrib.auth.models import User


class Blog(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField()
    link = models.URLField()
    date = models.DateTimeField()
    author = models.CharField(max_length=50)
    banner = models.ImageField()    
```

---

## Step 21. Create and apply migrations

Whenever you create or change a model, run:

```powershell
py .\manage.py makemigrations
py .\manage.py migrate
```

This creates the database table for blogs.

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
blogs/admin.py
```

Add:

```python
from django.contrib import admin
from .models import Blog


admin.site.register(Blog)
```

Refresh the admin panel. You should now see **Blog**.

Add a few sample blogs from the admin panel.

---

# Part 7 — Show Jobs on the Website

## Step 24. Create jobs URLs

Create:

```text
blogs/urls.py
```

Add:

```python
from django.urls import path
from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.blog, name="blogs"),
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



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("jobs/", include("jobs.urls")),
    path("blogs/", include("blogs.urls")),
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
from .models import Blog

# Create your views here.

def blog(request):
    blogs = Blog.objects.all().order_by("-date")
    return render(request, "blogs/blogs.html", {"blogs": blogs})


```

---


## Step 27. Create the job list template

Create this folder:

```text
blogs/templates/blogs/
```

Inside it, create:

```text
blogs.html
```

Add:

```html
{% extends "sharedpage.html" %}

{% block title %}
    Blogs
{% endblock title %}

{% block main %}

<section class="blogs-section">

    <div class="blogs-header">
        <h2>Latest Blogs</h2>
        <p>Articles, career advice, and useful resources for job seekers.</p>
    </div>

    <div class="blogs-list">

        {% for b in blogs %}

            <article class="blog-card">

                <div class="blog-card-top">

                    <div>
                        <h3>
                            <a href="{{ b.link }}">
                                {{ b.title }}
                            </a>
                        </h3>

                        <p class="blog-author">
                            By <strong>{{ b.author }}</strong>
                        </p>
                    </div>

                    <p class="blog-date">
                        {{ b.date|date:"M d, Y" }}
                    </p>

                </div>

                {% if b.banner %}
                    <img
                        class="blog-banner"
                        src="{{ b.banner.url }}"
                        alt="{{ b.title }}"
                    />
                {% endif %}

                <p class="blog-description">
                    {{ b.body|truncatewords:35 }}
                </p>

                <a class="read-blog-link" href="{{ b.link }}">
                    Read More
                </a>

            </article>

        {% empty %}

            <div class="no-blog-results">
                <h3>No blogs available</h3>
                <p>New blog posts will appear here.</p>
            </div>

        {% endfor %}

    </div>

</section>

{% endblock main %}

```
- Add this to the css file
```
/* ========================================
   BLOG PAGE
======================================== */

.blogs-section {
    width: 100%;
    margin: 20px 20px 30px;
}

.blogs-header {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #ff8500;
}

.blogs-header h2 {
    margin-bottom: 5px;
}

.blogs-header p {
    color: #555;
}

.blogs-list {
    width: 100%;
}

.blog-card {
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: white;
}

.blog-card:hover {
    border-color: #ff8500;
}

.blog-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 15px;
}

.blog-card h3 {
    margin-bottom: 3px;
}

.blog-card h3 a {
    color: #333;
    text-decoration: none;
}

.blog-card h3 a:hover {
    color: #ff8500;
}

.blog-author {
    color: #666;
    font-size: 14px;
}

.blog-author strong {
    color: #d96f00;
}

.blog-date {
    flex-shrink: 0;
    color: #666;
    font-size: 14px;
}

.blog-banner {
    display: block;
    width: 100%;
    max-height: 320px;
    margin-bottom: 15px;
    border-radius: 5px;
    object-fit: cover;
}

.blog-description {
    margin-bottom: 15px;
}

.read-blog-link {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 3px;
    background-color: #333;
    color: white;
    text-decoration: none;
}

.read-blog-link:hover {
    background-color: #ff8500;
}

.no-blog-results {
    padding: 30px 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    text-align: center;
}

.no-blog-results h3 {
    margin-bottom: 5px;
}

@media screen and (max-width: 700px) {
    .blogs-section {
        margin: 15px;
    }

    .blog-card-top {
        flex-direction: column;
        gap: 5px;
    }

    .blog-banner {
        max-height: 220px;
    }
}
```

- Add a new blogs page link in the header menu

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
          <li><a href="{% url 'jobs:job_list' %}">Find Jobs</a></li>
          <li><a href="{% url 'blogs:blogs' %}">Blogs</a></li>
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
http://127.0.0.1:8000/blogs/
```

---