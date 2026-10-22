# JobZila v3: Converting a Static Website into a Django Project

## Module goal

In this module, you will take an existing static JobZila website built with HTML, CSS, and JavaScript and convert it into a Django project.

You will learn how to:

- create and run a Django project;
- connect URLs to view functions;
- render HTML templates;
- configure project-level templates;
- configure CSS, JavaScript, and image files as Django static files;
- remove repeated HTML using the DRY principle;
- create a shared layout with `sharedpage.html`;
- use template inheritance with `{% extends %}` and `{% block %}`;
- replace direct page links with Django `{% url %}` tags;
- build a responsive hamburger menu;
- troubleshoot common template and static-file errors.

This version intentionally does **not** create a Django app yet. Apps, models, databases, CRUD, authentication, APIs, and forms will come later.

---

# 1. Starting point

Assume you already have a static website with files similar to these:

```text
jobzila-static/
├── index.html
├── job_search.html
├── job_listing.html
├── terms.html
├── privacy.html
├── contact_us.html
├── styles.css
├── mainPic.jpg
└── menu.js
```

Each HTML page currently repeats the same:

- `<head>` section;
- header;
- navigation menu;
- footer;
- CSS and JavaScript links.

That repetition is what we will remove using Django template inheritance.

---

# 2. Create the working folder

Open PowerShell or the VS Code terminal and move to the location where you want to create the project.

```powershell
cd D:\path\to\your\projects
```

Create a project folder:

```powershell
mkdir jobzila-v3-templates
cd jobzila-v3-templates
```

---

# 3. Create and activate a virtual environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Your terminal should now begin with:

```text
(.venv)
```

Verify the active Python interpreter:

```powershell
python -c "import sys; print(sys.executable)"
```

The path should point to `.venv\Scripts\python.exe`.

> Use `python`, not `py`, after activating the virtual environment. This avoids accidentally using another Python installation such as Anaconda.

---

# 4. Install Django

```powershell
python -m pip install django
```

Confirm the installation:

```powershell
python -m django --version
```

---

# 5. Create the Django project

Run:

```powershell
python -m django startproject jobzilav3
```

Move into the folder containing `manage.py`:

```powershell
cd jobzilav3
```

The initial structure should look like this:

```text
jobzilav3/
├── manage.py
└── jobzilav3/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

Run the default project:

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Stop the server with:

```text
Ctrl + C
```

---

# 6. Create the templates and static folders

Beside `manage.py`, create:

```text
templates/
static/
```

Inside `static`, create:

```text
static/
├── css/
├── images/
└── js/
```

The project should now look like this:

```text
jobzilav3/
├── manage.py
├── templates/
├── static/
│   ├── css/
│   ├── images/
│   └── js/
└── jobzilav3/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

---

# 7. Copy the original static website files

Copy the files into their Django locations:

```text
styles.css   → static/css/styles.css
mainPic.jpg  → static/images/mainPic.jpg
menu.js      → static/js/menu.js
```

Copy the HTML files into `templates` and rename `index.html` to `home.html`:

```text
templates/
├── home.html
├── job_search.html
├── job_listing.html
├── terms.html
├── privacy.html
└── contact_us.html
```

Later, we will create:

```text
templates/sharedpage.html
```

---

# 8. Configure the templates folder

Open:

```text
jobzilav3/settings.py
```

Find the `TEMPLATES` setting and change:

```python
"DIRS": [],
```

to:

```python
"DIRS": [BASE_DIR / "templates"],
```

The important section should be:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

This tells Django to search the project-level `templates` folder.

---

# 9. Configure static files

At the bottom of `settings.py`, use:

```python
STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

This tells Django where to find the project-level CSS, JavaScript, and image files.

Your settings now connect:

```text
BASE_DIR/templates
BASE_DIR/static
```

---

# 10. Create the project-level views file

Because this lesson focuses only on converting a static website, create `views.py` inside the inner project folder beside `urls.py`.

```text
jobzilav3/
├── manage.py
└── jobzilav3/
    ├── settings.py
    ├── urls.py
    ├── views.py
    ├── asgi.py
    └── wsgi.py
```

Add this code to `jobzilav3/views.py`:

```python
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def job_search(request):
    return render(request, "job_search.html")


def job_listing(request):
    return render(request, "job_listing.html")


def terms(request):
    return render(request, "terms.html")


def privacy(request):
    return render(request, "privacy.html")


def contact(request):
    return render(request, "contact_us.html")
```

Each function receives a browser request and returns an HTML template.

The basic flow is:

```text
Browser request
      ↓
urls.py
      ↓
view function
      ↓
HTML template
      ↓
Browser response
```

---

# 11. Connect URLs to views

Replace the contents of `jobzilav3/urls.py` with:

```python
from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("job-search/", views.job_search, name="job_search"),
    path("job-listing/", views.job_listing, name="job_listing"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("contact/", views.contact, name="contact"),
]
```

Understand one route:

```python
path("job-search/", views.job_search, name="job_search")
```

- `"job-search/"` is the browser URL.
- `views.job_search` is the function Django runs.
- `name="job_search"` gives the route a reusable Django name.

---

# 12. Identify the repeated HTML

Before Django, every page probably contains:

```html
<!doctype html>
<html>
  <head>...</head>
  <body>
    <header>...</header>
    <nav>...</nav>

    Page-specific content

    <footer>...</footer>
  </body>
</html>
```

Repeating this in six files creates several problems:

- changing the navigation requires editing every page;
- links can become inconsistent;
- repeated code is harder to maintain;
- mistakes are copied across the project.

Django solves this with the **DRY principle**:

> Do not Repeat Yourself.

---

# 13. Create `sharedpage.html`

Create:

```text
templates/sharedpage.html
```

Add:

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
          <li><a href="{% url 'job_listing' %}">Job Listing</a></li>
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

Important Django template tags:

```django
{% load static %}
```

Loads Django's static-file template tag.

```django
{% static 'css/styles.css' %}
```

Builds the correct URL for a static file.

```django
{% url 'home' %}
```

Builds a URL using the route name from `urls.py`.

```django
{% block main %}{% endblock main %}
```

Creates a replaceable area for page-specific content.

---

# 14. Convert `home.html`

Remove the repeated document structure from the original `index.html`.

Use:

```html
{% extends "sharedpage.html" %}

{% block title %}Home | JobZila{% endblock title %}

{% block main %}
<section class="hero">
  <section class="hero-section">
    <h2>Welcome to JobZila</h2>
    <p>
      Lorem ipsum dolor sit amet consectetur adipisicing elit. Ullam delectus
      aperiam corporis, veniam sequi vero eos minima perspiciatis ut corrupti ex
      in.
    </p>
  </section>
</section>
{% endblock main %}
```

Do not add another `<main>` element here. The shared template already provides it.

---

# 15. Convert the remaining pages

Every child page follows the same pattern:

```html
{% extends "sharedpage.html" %}

{% block title %}Page Name | JobZila{% endblock title %}

{% block main %}
  Page-specific HTML only
{% endblock main %}
```

Example: `job_search.html`

```html
{% extends "sharedpage.html" %}

{% block title %}Job Search | JobZila{% endblock title %}

{% block main %}
<section class="contact-section">
  <h2>Job Search</h2>

  <div class="contact">
    <form action="" class="contact-form">
      <input
        type="text"
        id="keyword"
        name="keyword"
        required
        placeholder="Keyword"
      />

      <input
        type="text"
        id="location"
        name="location"
        required
        placeholder="Location"
      />

      <select name="category" id="category">
        <option value="">All Categories</option>
        <option value="it">IT</option>
        <option value="finance">Finance</option>
        <option value="billing">Billing</option>
        <option value="marketing">Marketing</option>
      </select>

      <input type="submit" value="Search Jobs" />
    </form>
  </div>
</section>
{% endblock main %}
```

The form is only visual at this stage. It does not yet submit data to Django.

---

# 16. Convert static CSS paths

Django loads the CSS file in `sharedpage.html`:

```html
<link rel="stylesheet" href="{% static 'css/styles.css' %}" />
```

Inside the CSS file, image paths are relative to the CSS file.

The CSS file is located at:

```text
static/css/styles.css
```

The image is located at:

```text
static/images/mainPic.jpg
```

Therefore, the background path must move up one folder:

```css
background-image: url("../images/mainPic.jpg");
```

Do not use:

```css
background-image: url("images/mainPic.jpg");
```

That incorrectly looks for:

```text
static/css/images/mainPic.jpg
```

---

# 17. Use the cleaned CSS

Save this as:

```text
static/css/styles.css
```

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html,
body {
    min-height: 100%;
}

body {
    min-height: 100vh;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
    display: flex;
    flex-direction: column;
}

main {
    flex: 1;
    display: flex;
}

header {
    background-color: #333;
    color: white;
}

header h1 {
    padding: 20px;
}

.navbar {
    position: relative;
    width: 100%;
    background-color: #ff8500;
    padding: 10px 20px;
}

.nav-menu {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 25px;
    margin: 0;
    padding: 0;
    list-style: none;
}

.nav-menu li {
    list-style: none;
}

.nav-menu a {
    display: block;
    color: white;
    text-decoration: none;
    padding: 6px 0;
}

.nav-menu a:hover {
    color: #f8e1cc;
}

.menu-toggle {
    display: none;
    background: transparent;
    color: white;
    border: 2px solid white;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 28px;
    line-height: 1;
    cursor: pointer;
}

footer {
    width: 100%;
    background-color: #333;
    color: white;
    padding: 20px;
    text-align: center;
}

footer a {
    color: #f7c784;
    text-decoration: none;
}

footer a:hover {
    color: #f28d21;
}

.hero {
    flex: 1;
    min-height: 500px;
    width: 100%;
    background-image: url("../images/mainPic.jpg");
    background-size: cover;
    background-position: center 25%;
    background-repeat: no-repeat;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.hero-section {
    max-width: 800px;
    padding: 30px;
    border-radius: 8px;
    text-align: center;
    background-color: rgba(0, 0, 0, 0.45);
}

.hero-section h2 {
    color: #56a8f0;
    font-size: 36px;
}

.hero-section p {
    margin-top: 30px;
    color: rgb(239, 231, 181);
}

.privacy-section,
.terms-section,
.jobs-listing-section,
.contact-section {
    width: 100%;
    margin: 20px 20px 30px;
}

.privacy-section h2,
.terms-section h2,
.jobs-listing-section h2,
.contact-section h2 {
    margin-bottom: 10px;
}

.privacy,
.terms,
.jobs-listing,
.contact {
    margin-bottom: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 20px;
}

.contact-form {
    padding: 20px;
}

.contact-form input,
.contact-form textarea,
.contact-form select {
    width: 100%;
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
}

.contact-form textarea {
    min-height: 120px;
    resize: vertical;
}

.contact-form input[type="submit"] {
    width: auto;
    background-color: #333;
    color: white;
    padding: 10px 15px;
    margin-top: 10px;
    border: none;
    cursor: pointer;
}

.contact-form input[type="submit"]:hover {
    background-color: #ff8500;
}

@media screen and (max-width: 700px) {
    .menu-toggle {
        display: block;
        margin-left: auto;
    }

    .nav-menu {
        display: none;
        flex-direction: column;
        align-items: stretch;
        gap: 0;
        width: 100%;
        margin-top: 10px;
    }

    .nav-menu.active {
        display: flex;
    }

    .nav-menu li {
        width: 100%;
        border-top: 1px solid rgba(255, 255, 255, 0.35);
    }

    .nav-menu a {
        width: 100%;
        padding: 12px 5px;
    }

    .hero {
        min-height: 400px;
    }

    .hero-section h2 {
        font-size: 28px;
    }
}
```

The `body`, `main`, and `footer` rules prevent unwanted white space before the footer:

```css
body {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

main {
    flex: 1;
}
```

---

# 18. Add the hamburger-menu JavaScript

Save this as:

```text
static/js/menu.js
```

```javascript
const menuButton = document.querySelector(".menu-toggle");
const navigationMenu = document.querySelector(".nav-menu");

if (menuButton && navigationMenu) {
    menuButton.addEventListener("click", function () {
        navigationMenu.classList.toggle("active");

        const isOpen = navigationMenu.classList.contains("active");

        menuButton.setAttribute("aria-expanded", isOpen);
        menuButton.textContent = isOpen ? "✕" : "☰";
    });
}
```

The script is loaded once from `sharedpage.html`:

```html
<script src="{% static 'js/menu.js' %}"></script>
```

That means every page receives the same responsive navigation behavior.

---

# 19. Final project structure

Your completed project should look like this:

```text
jobzilav3/
├── manage.py
├── db.sqlite3
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   │   └── mainPic.jpg
│   └── js/
│       └── menu.js
├── templates/
│   ├── sharedpage.html
│   ├── home.html
│   ├── job_search.html
│   ├── job_listing.html
│   ├── terms.html
│   ├── privacy.html
│   └── contact_us.html
└── jobzilav3/
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    ├── views.py
    └── wsgi.py
```

Do not include `__pycache__` folders when sharing the project. Python recreates them automatically.

---

# 20. Apply Django's built-in migrations

Run:

```powershell
python manage.py migrate
```

This creates the built-in database tables required by Django's admin, authentication, sessions, and content-type systems.

These migrations do not yet create JobZila-specific tables.

---

# 21. Run and test the project

Start the server:

```powershell
python manage.py runserver
```

Test these addresses:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/job-search/
http://127.0.0.1:8000/job-listing/
http://127.0.0.1:8000/terms/
http://127.0.0.1:8000/privacy/
http://127.0.0.1:8000/contact/
```

Resize the browser below 700 pixels and confirm that the hamburger menu appears.

---

# 22. Common errors and fixes

## Error: `django-admin` is not recognized

Use:

```powershell
python -m django startproject jobzilav3
```

Also confirm Django is installed inside the active virtual environment.

---

## Error: `TemplateDoesNotExist`

Check:

```python
"DIRS": [BASE_DIR / "templates"],
```

Also verify that the file exists inside `templates` and the filename matches exactly.

---

## Error: `NoReverseMatch`

Example:

```text
Reverse for 'job_search' not found
```

This means the template contains:

```django
{% url 'job_search' %}
```

but `urls.py` does not contain a route named `job_search`.

The names must match:

```python
path("job-search/", views.job_search, name="job_search")
```

---

## Error: view has no attribute

Example:

```text
module 'jobzilav3.views' has no attribute 'home'
```

Confirm that `views.py` contains:

```python
def home(request):
    return render(request, "home.html")
```

The function name after `views.` in `urls.py` must exist in `views.py`.

---

## CSS does not update

Use a hard refresh:

```text
Ctrl + Shift + R
```

You can also temporarily use:

```html
<link rel="stylesheet" href="{% static 'css/styles.css' %}?v=2" />
```

The query string forces the browser to request a newer copy.

---

## CSS loads but the background image does not

Verify:

```text
static/css/styles.css
static/images/mainPic.jpg
```

Then use:

```css
background-image: url("../images/mainPic.jpg");
```

---

## Django template code still runs inside an HTML comment

This does not reliably disable Django template tags:

```html
<!-- <a href="{% url 'contact' %}">Contact</a> -->
```

Use a Django comment:

```django
{% comment %}
<a href="{% url 'contact' %}">Contact</a>
{% endcomment %}
```

Or remove the unused code.

---

# 23. Student checkpoint

By the end of this activity, you should be able to explain:

1. What is the difference between a Django project and a Django app?
2. Why did we create `views.py`?
3. What does `render()` do?
4. How does a URL route reach a template?
5. Why is `sharedpage.html` useful?
6. What problem does DRY solve?
7. What does `{% extends %}` do?
8. What does `{% block main %}` do?
9. Why do we use `{% static %}`?
10. Why do we use `{% url %}` instead of linking directly to `.html` files?
11. Why is the image path in CSS `../images/mainPic.jpg`?
12. Why can browser caching make correct CSS appear broken?

---

# 24. Practice tasks

## Task 1: Add an About page

Create:

```text
templates/about.html
```

Add a view, URL, navigation link, and content block.

## Task 2: Add an active navigation style

Give the current page's navigation link a different background or underline.

## Task 3: Improve the home hero

Change:

- hero heading;
- paragraph;
- background position;
- overlay opacity.

## Task 4: Add a second image

Place another image inside `static/images` and display it using:

```django
{% load static %}
<img src="{% static 'images/example.jpg' %}" alt="Example" />
```

## Task 5: Create a 404 practice route

Visit a URL that does not exist and observe Django's development error page.

---

# 25. What comes next

This project currently uses project-level views and templates to teach the request-response cycle without extra complexity.

The next stage is to create real Django apps:

```powershell
python manage.py startapp jobs
python manage.py startapp users
```

Then the project can grow into:

```text
jobs/       → job models, listings, forms, and CRUD
users/      → registration, login, logout, and profiles
api/        → REST API endpoints
```

At that point, templates and views will move into their related apps, and JobZila will begin using database-driven content instead of hard-coded HTML.
