# Part 9 — Add User Registration and Login

## Step 32. Create users app

```powershell
py .\manage.py startapp users
```

---

## Step 33. Register users app

Open:

```text
myproject/myproject/settings.py
```

Add `users`:

```python
INSTALLED_APPS = [
    ...
    "jobs",
    "users",
]
```

---

## Step 34. Create users URLs

Create:

```text
users/urls.py
```

Add:

```python
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
```

---

## Step 35. Connect users URLs to project

Open:

```text
myproject/myproject/urls.py
```

Add:

```python
path("users/", include("users.urls")),
```

Full example:

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
    path("users/", include("users.urls")),
]

```

---

## Step 36. Create registration and login views

Open:

```text
users/views.py
```

Add:

```python
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("jobs:job_list")
    else:
        form = UserCreationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("jobs:job_list")
    else:
        form = AuthenticationForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("jobs:job_list")
```

---

## Step 37. Create registration template

Create this folder:

```text
users/templates/users/
```

Create:

```text
register.html
```

Add:

```html
{% extends 'sharedpage.html' %}

{% block title %}Register | JobZila{% endblock title %}

{% block main %}
<section class="auth-section">
    <div class="auth-card">
        <h2>Create Account</h2>

        <p class="auth-intro">
            Register to post jobs and manage your account.
        </p>

        <form method="POST" class="auth-form">
            {% csrf_token %}
            {{ form.as_p }}

            <button type="submit">
                Register
            </button>
        </form>

        <p class="auth-footer">
            Already have an account?
            <a href="{% url 'users:login' %}">
                Login
            </a>
        </p>
    </div>
</section>
{% endblock main %}
```

---

## Step 38. Create login template

Create:

```text
users/templates/users/login.html
```

Add:

```html
{% extends 'sharedpage.html' %}

{% block title %}Login | JobZila{% endblock title %}

{% block main %}
<section class="auth-section">
    <div class="auth-card">
        <h2>Login</h2>

        <p class="auth-intro">
            Sign in to manage jobs and access your account.
        </p>

        <form method="POST" class="auth-form">
            {% csrf_token %}
            {{ form.as_p }}

            <button type="submit">
                Login
            </button>
        </form>

        <p class="auth-footer">
            Do not have an account?
            <a href="{% url 'users:register' %}">
                Create one
            </a>
        </p>
    </div>
</section>
{% endblock main %}
```

Test:

```text
http://127.0.0.1:8000/users/register/
http://127.0.0.1:8000/users/login/
```

- Add this to the sharedpage.html

```html
     {% if user.is_authenticated  %}


          <li><a href="">Add Blog</a></li>
          <li><a href="">Add Job</a></li>
          

          {% endif %}
         
 <li class="right-align">
    {% if user.is_authenticated %}

        <form
            method="POST"
            action="{% url 'users:logout' %}"
            class="logout-form"
        >
            {% csrf_token %}

            <button
                class="logout-button"
                type="submit"
            >
                Logout
            </button>
        </form>

    {% else %}

        <a href="{% url 'users:register' %}">
            Register
        </a>

        <a href="{% url 'users:login' %}">
            Login
        </a>

    {% endif %}
</li>
```
- Change the sharedpage.html

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


          {% if user.is_authenticated  %}


          <li><a href="">Add Blog</a></li>
          <li><a href="">Add Job</a></li>
          

          {% endif %}
         
 <li class="right-align">
    {% if user.is_authenticated %}

        <form
            method="POST"
            action="{% url 'users:logout' %}"
            class="logout-form"
        >
            {% csrf_token %}

            <button
                class="logout-button"
                type="submit"
            >
                Logout
            </button>
        </form>

    {% else %}

        <a href="{% url 'users:register' %}">
            Register
        </a>

        <a href="{% url 'users:login' %}">
            Login
        </a>

    {% endif %}
</li>
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


- Change the CSS

- For LOGIN AND REGISTER

```
/* ========================================
   LOGIN AND REGISTER
======================================== */

.auth-section {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 40px 20px;
}

.auth-card {
    width: 100%;
    max-width: 500px;
    padding: 25px;
    border: 1px solid #ccc;
    border-top: 5px solid #ff8500;
    border-radius: 5px;
    background-color: white;
}

.auth-card h2 {
    margin-bottom: 5px;
    color: #333;
}

.auth-intro {
    margin-bottom: 20px;
    color: #555;
}

.auth-form p {
    margin-bottom: 15px;
}

.auth-form label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.auth-form input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
}

.auth-form input:focus {
    border-color: #ff8500;
    outline: 1px solid #ff8500;
}

.auth-form button {
    width: 100%;
    margin-top: 5px;
    padding: 10px 15px;
    border: none;
    border-radius: 3px;
    background-color: #333;
    color: white;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
}

.auth-form button:hover {
    background-color: #ff8500;
}

.auth-form .helptext {
    display: block;
    margin-top: 5px;
    color: #666;
    font-size: 14px;
}

.auth-form ul {
    margin: 5px 0 10px 20px;
    color: #666;
    font-size: 14px;
}

.auth-form .errorlist {
    margin: 0 0 10px;
    padding: 10px;
    border: 1px solid #d9534f;
    border-radius: 3px;
    background-color: #fff2f2;
    color: #b52b27;
    list-style-position: inside;
}

.auth-footer {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #ddd;
    text-align: center;
    color: #555;
}

.auth-footer a {
    color: #d96f00;
    font-weight: bold;
    text-decoration: none;
}

.auth-footer a:hover {
    text-decoration: underline;
}

@media screen and (max-width: 700px) {
    .auth-section {
        padding: 20px 15px;
    }

    .auth-card {
        padding: 20px;
    }
}
```
  
```css
/* Push login, register, or logout to the right */

.nav-menu .right-align {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 25px;
}


/* Remove the form's default spacing */

.logout-form {
    display: flex;
    align-items: center;
    margin: 0;
}


/* Make logout look exactly like navigation links */

.logout-button {
    display: block;
    padding: 6px 0;
    border: none;
    background: transparent;
    color: white;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    cursor: pointer;
}

.logout-button:hover {
    color: #f8e1cc;
}
```
- For Mobile Navigation
```
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

    .nav-menu .right-align {
        width: 100%;
        margin-left: 0;
        flex-direction: column;
        align-items: stretch;
        gap: 0;
    }

    .nav-menu .right-align a,
    .nav-menu .logout-form,
    .nav-menu .logout-button {
        width: 100%;
    }

    .nav-menu .right-align a,
    .nav-menu .logout-button {
        padding: 12px 5px;
        text-align: left;
    }

    .nav-menu .right-align a + a,
    .nav-menu .logout-form {
        border-top: 1px solid rgba(255, 255, 255, 0.35);
    }

    .hero {
        min-height: 400px;
    }

    .hero-section h2 {
        font-size: 28px;
    }
}
```