# JobZila v3 — Adding Job Search (Student Step-by-Step Guide)

**Continuation of the earlier JobZila project, before the Blogs app lesson.** This guide reconstructs the search functionality directly from the uploaded `jobzilav3_job_search.zip`. The earlier Blogs guide starts at Step 18; the search lesson below uses Steps 10–17 so it can be taught immediately beforehand.

## Learning objectives

Students will implement a database-backed job list, quick job-title search, advanced filters, ordering, results count, and an expandable search panel using Django, HTML, CSS, and JavaScript.

## Part 4 — Job Search

### Step 10. Open the existing Django project

Open the project directory containing `manage.py`. The ZIP includes `jobs/`, `jobzilav3/`, `templates/`, `static/`, and `db.sqlite3`. Use a virtual environment and install Django if it is not installed.

```powershell
cd jobzilav3_job_search
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install "Django>=6.0,<7.0"
py .\manage.py check
```

> If you already have a working environment, activate it rather than creating a new one. This uploaded project was generated with Django 6.0.7.

### Step 11. Confirm the Job model

The search uses existing job records stored in the database. Confirm this model in the jobs app; do not create a second Job model.

**File:** `jobs/models.py`

```python
# Create your models here.
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

The fields `title`, `company`, `location`, and `description` are searchable. `created_at` supports newest/oldest sorting.

If the model is new in your own earlier version, run:

```powershell
py .\manage.py makemigrations
py .\manage.py migrate
```

### Step 12. Create the job list view and filtering logic

Open `jobs/views.py`. The `GET` parameters come from the search forms. `icontains` performs case-insensitive substring matching. The `Q` expressions combine keyword matches with OR; the successive `.filter()` calls combine separate search fields with AND.

**File:** `jobs/views.py`

```python
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from .models import Job


def job_list(request):
    # Quick-search value
    quick_search = request.GET.get("q", "").strip()

    # Advanced-search values
    title = request.GET.get("title", "").strip()
    company = request.GET.get("company", "").strip()
    location = request.GET.get("location", "").strip()
    keyword = request.GET.get("keyword", "").strip()
    sort = request.GET.get("sort", "newest")

    jobs = Job.objects.all()

    # -------------------------------------
    # Quick search: title only
    # -------------------------------------
    if quick_search:
        jobs = jobs.filter(title__icontains=quick_search)

    # -------------------------------------
    # Advanced search: multiple filters
    # -------------------------------------
    if title:
        jobs = jobs.filter(title__icontains=title)

    if company:
        jobs = jobs.filter(company__icontains=company)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword)
            | Q(company__icontains=keyword)
            | Q(location__icontains=keyword)
            | Q(description__icontains=keyword)
        )

    # -------------------------------------
    # Sorting
    # -------------------------------------
    if sort == "oldest":
        jobs = jobs.order_by("created_at")

    elif sort == "title":
        jobs = jobs.order_by("title")

    elif sort == "company":
        jobs = jobs.order_by("company")

    else:
        jobs = jobs.order_by("-created_at")

    # Used to decide whether advanced search is active
    advanced_search_active = any(
        [title, company, location, keyword, sort != "newest"]
    )

    context = {
        "jobs": jobs,
        "quick_search": quick_search,
        "title_search": title,
        "company_search": company,
        "location_search": location,
        "keyword_search": keyword,
        "sort": sort,
        "advanced_search_active": advanced_search_active,
        "result_count": jobs.count(),
    }

    return render(request, "jobs/job_list.html", context)
```

**Trace the logic:** A quick search for `Python` filters only job titles. An advanced `location=Toronto` and `keyword=Python` request finds Toronto jobs whose title, company, location, or description contains Python. The default order is newest first.

### Step 13. Create the jobs URL configuration

**File:** `jobs/urls.py`

```python
from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
]
```

Confirm that the main project routes `/jobs/` into this URL configuration. The ZIP also retains older `/job-search/` and `/job-listing/` pages; the database-backed search built in this lesson is `/jobs/`.

**File:** `jobzilav3/urls.py`

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

### Step 14. Build the search and results template

Create or update `jobs/templates/jobs/job_list.html`. It inherits the shared page, submits filters with `GET`, preserves entered values, displays result counts, and renders matching jobs.

**File:** `jobs/templates/jobs/job_list.html`

```html
{% extends "sharedpage.html" %}

{% block title %}
Find Jobs | JobZila
{% endblock title %}

{% block main %}
<section class="jobs-search-section">

    <div class="jobs-search-header">
        <h2>Find Jobs</h2>
        <p>
            Search available jobs by title or use advanced search
            to filter by multiple criteria.
        </p>
    </div>

    <!-- Quick title search -->
    <div class="job-search-box">
        <form
            method="GET"
            action="{% url 'jobs:job_list' %}"
            class="quick-search-form"
        >
            <label for="quick-search">Search by job title</label>

            <div class="quick-search-row">
                <input
                    type="search"
                    id="quick-search"
                    name="q"
                    value="{{ quick_search }}"
                    placeholder="For example: Python Developer"
                />

                <button type="submit">
                    Search
                </button>
            </div>
        </form>

        <button
            type="button"
            id="advanced-search-toggle"
            class="advanced-search-toggle"
            aria-expanded="{% if advanced_search_active %}true{% else %}false{% endif %}"
            aria-controls="advanced-search"
        >
            Advanced Search
        </button>
    </div>

    <!-- Advanced search -->
    <div
        id="advanced-search"
        class="advanced-search-box {% if advanced_search_active %}show{% endif %}"
    >
        <h3>Advanced Search</h3>

        <p>
            Complete one or more fields to narrow the job results.
        </p>

        <form
            method="GET"
            action="{% url 'jobs:job_list' %}"
            class="advanced-search-form"
        >
            <div class="advanced-search-fields">

                <div class="search-field">
                    <label for="title">Job title</label>
                    <input
                        type="text"
                        id="title"
                        name="title"
                        value="{{ title_search }}"
                        placeholder="Software Developer"
                    />
                </div>

                <div class="search-field">
                    <label for="company">Company</label>
                    <input
                        type="text"
                        id="company"
                        name="company"
                        value="{{ company_search }}"
                        placeholder="Microsoft"
                    />
                </div>

                <div class="search-field">
                    <label for="location">Location</label>
                    <input
                        type="text"
                        id="location"
                        name="location"
                        value="{{ location_search }}"
                        placeholder="Toronto"
                    />
                </div>

                <div class="search-field">
                    <label for="keyword">Keyword</label>
                    <input
                        type="text"
                        id="keyword"
                        name="keyword"
                        value="{{ keyword_search }}"
                        placeholder="Python, remote, senior..."
                    />
                </div>

                <div class="search-field">
                    <label for="sort">Sort results</label>

                    <select id="sort" name="sort">
                        <option
                            value="newest"
                            {% if sort == "newest" %}selected{% endif %}
                        >
                            Newest first
                        </option>

                        <option
                            value="oldest"
                            {% if sort == "oldest" %}selected{% endif %}
                        >
                            Oldest first
                        </option>

                        <option
                            value="title"
                            {% if sort == "title" %}selected{% endif %}
                        >
                            Job title A–Z
                        </option>

                        <option
                            value="company"
                            {% if sort == "company" %}selected{% endif %}
                        >
                            Company A–Z
                        </option>
                    </select>
                </div>

            </div>

            <div class="advanced-search-buttons">
                <button type="submit">
                    Apply Filters
                </button>

                <a href="{% url 'jobs:job_list' %}">
                    Clear Search
                </a>
            </div>
        </form>
    </div>

    <!-- Results heading -->
    <div class="job-results-heading">
        <div>
            <h2>
                {{ result_count }}
                Job{{ result_count|pluralize }}
                Found
            </h2>

            {% if quick_search %}
                <p>
                    Results for job title:
                    <strong>{{ quick_search }}</strong>
                </p>
            {% elif advanced_search_active %}
                <p>Results matching your selected filters.</p>
            {% else %}
                <p>All currently available jobs.</p>
            {% endif %}
        </div>

        {% if quick_search or advanced_search_active %}
            <a href="{% url 'jobs:job_list' %}">
                View All Jobs
            </a>
        {% endif %}
    </div>

    <!-- Job results -->
    <div class="jobs-results-list">

        {% for job in jobs %}

            <article class="job-result-card">
                <div class="job-result-top">
                    <div>
                        <h3>
                        
                             {{ job.title }}
                        </h3>

                        <p class="job-company-name">
                            {{ job.company }}
                        </p>
                    </div>

                    <p class="job-posted-date">
                        {{ job.created_at|date:"M d, Y" }}
                    </p>
                </div>

                <div class="job-result-information">
                    <p>
                        <strong>Location:</strong>
                        {{ job.location }}
                    </p>

                    <p>
                        <strong>Company:</strong>
                        {{ job.company }}
                    </p>
                </div>

                <p class="job-result-description">
                    {{ job.description|truncatewords:30 }}
                </p>

               
                <a
                    
                    class="view-job-link"
                >
                    View Job Details
                </a>
            </article>

        {% empty %}

            <div class="no-job-results">
                <h3>No jobs found</h3>

                <p>
                    Try another title, location, company, or keyword.
                </p>

                <a href="{% url 'jobs:job_list' %}">
                    Clear Search
                </a>
            </div>

        {% endfor %}

    </div>

</section>
{% endblock main %}
```

**Important limitation in the uploaded version:** The `View Job Details` anchor has no `href` and therefore does not navigate anywhere. Building a real job-detail page is a separate lesson; do not present this button as working functionality.

### Step 15. Add the styling

The ZIP already contains the search styles in `static/css/styles.css`. If you are following this lesson from an earlier project version, merge the search-related styles into your existing stylesheet; do not overwrite unrelated CSS. The full uploaded stylesheet is provided below so the page matches the starter project.

**File:** `static/css/styles.css`

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




/* ========================================
   JOB SEARCH AND RESULTS
======================================== */

.jobs-search-section {
    width: 100%;
    margin: 20px 20px 30px;
}

.jobs-search-header {
    margin-bottom: 20px;
}

.jobs-search-header h2 {
    margin-bottom: 5px;
}

.jobs-search-header p {
    color: #555;
}


/* Quick search */

.job-search-box {
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f8f8f8;
}

.quick-search-form label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
}

.quick-search-row {
    display: flex;
    gap: 10px;
}

.quick-search-row input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
}

.quick-search-row input:focus {
    outline: 2px solid #ff8500;
    border-color: #ff8500;
}

.quick-search-row button {
    background-color: #333;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
}

.quick-search-row button:hover {
    background-color: #ff8500;
}


/* Advanced search button */

.advanced-search-toggle {
    margin-top: 15px;
    padding: 0;
    border: none;
    background: transparent;
    color: #d96f00;
    font-family: inherit;
    font-size: 16px;
    font-weight: bold;
    text-decoration: underline;
    cursor: pointer;
}

.advanced-search-toggle:hover {
    color: #333;
}


/* Advanced search panel */

.advanced-search-box {
    display: none;
    margin-bottom: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-top: 5px solid #ff8500;
    border-radius: 5px;
}

.advanced-search-box.show {
    display: block;
}

.advanced-search-box h3 {
    margin-bottom: 5px;
}

.advanced-search-box > p {
    margin-bottom: 20px;
    color: #555;
}

.advanced-search-fields {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

.search-field {
    display: flex;
    flex-direction: column;
}

.search-field label {
    margin-bottom: 5px;
    font-weight: bold;
}

.search-field input,
.search-field select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
    background-color: white;
}

.search-field input:focus,
.search-field select:focus {
    outline: 2px solid #ff8500;
    border-color: #ff8500;
}

.advanced-search-buttons {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 20px;
}

.advanced-search-buttons button {
    background-color: #333;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
}

.advanced-search-buttons button:hover {
    background-color: #ff8500;
}

.advanced-search-buttons a {
    color: #d96f00;
    text-decoration: none;
}

.advanced-search-buttons a:hover {
    text-decoration: underline;
}


/* Results heading */

.job-results-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #ff8500;
}

.job-results-heading h2 {
    margin-bottom: 3px;
}

.job-results-heading p {
    color: #555;
}

.job-results-heading > a {
    color: #d96f00;
    font-weight: bold;
    text-decoration: none;
}

.job-results-heading > a:hover {
    text-decoration: underline;
}


/* Job cards */

.jobs-results-list {
    width: 100%;
}

.job-result-card {
    margin-bottom: 15px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: white;
}

.job-result-card:hover {
    border-color: #ff8500;
}

.job-result-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 10px;
}

.job-result-card h3 {
    margin-bottom: 2px;
}

.job-result-card h3 a {
    color: #333;
    text-decoration: none;
}

.job-result-card h3 a:hover {
    color: #ff8500;
}

.job-company-name {
    color: #d96f00;
    font-weight: bold;
}

.job-posted-date {
    flex-shrink: 0;
    color: #666;
    font-size: 14px;
}

.job-result-information {
    display: flex;
    flex-wrap: wrap;
    gap: 25px;
    margin-bottom: 10px;
    padding: 8px 0;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
}

.job-result-description {
    margin-bottom: 15px;
}

.view-job-link {
    display: inline-block;
    background-color: #333;
    color: white;
    padding: 8px 14px;
    border-radius: 3px;
    text-decoration: none;
}

.view-job-link:hover {
    background-color: #ff8500;
}


/* No results */

.no-job-results {
    padding: 30px 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    text-align: center;
}

.no-job-results h3 {
    margin-bottom: 5px;
}

.no-job-results p {
    margin-bottom: 15px;
}

.no-job-results a {
    color: #d96f00;
    font-weight: bold;
    text-decoration: none;
}

.no-job-results a:hover {
    text-decoration: underline;
}


/* Job search mobile layout */

@media screen and (max-width: 700px) {
    .jobs-search-section {
        margin: 15px;
    }

    .quick-search-row {
        flex-direction: column;
    }

    .quick-search-row button {
        width: 100%;
    }

    .advanced-search-fields {
        grid-template-columns: 1fr;
    }

    .advanced-search-buttons {
        align-items: stretch;
        flex-direction: column;
    }

    .advanced-search-buttons button,
    .advanced-search-buttons a {
        width: 100%;
        text-align: center;
    }

    .job-results-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .job-result-top {
        flex-direction: column;
        gap: 5px;
    }

    .job-result-information {
        flex-direction: column;
        gap: 4px;
    }
}
```

### Step 16. Make Advanced Search expandable

The JavaScript below retains the existing mobile navigation toggle and adds the advanced search show/hide behavior. Put it in `static/js/menu.js`.

**File:** `static/js/menu.js`

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


const advancedSearchToggle = document.querySelector(
    "#advanced-search-toggle"
);

const advancedSearchBox = document.querySelector(
    "#advanced-search"
);

if (advancedSearchToggle && advancedSearchBox) {
    advancedSearchToggle.addEventListener("click", function () {
        advancedSearchBox.classList.toggle("show");

        const isOpen = advancedSearchBox.classList.contains("show");

        advancedSearchToggle.setAttribute(
            "aria-expanded",
            isOpen
        );

        advancedSearchToggle.textContent = isOpen
            ? "Hide Advanced Search"
            : "Advanced Search";
    });
}
```

Ensure `templates/sharedpage.html` loads both the stylesheet and the JavaScript, and links to the named `jobs:job_list` route.

**File:** `templates/sharedpage.html`

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
          <!-- <li><a href="{% url 'job_search' %}">Job Search</a></li> -->
          <!-- <li><a href="{% url 'job_listing' %}">Job Listing</a></li> -->
          <li><a href="{% url 'jobs:job_list' %}">Find Jobs</a></li>
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

### Step 17. Run and test Job Search

```powershell
py .\manage.py migrate
py .\manage.py runserver
```

Open `http://127.0.0.1:8000/jobs/`. Add sample Job records in `/admin/` if necessary.

**Student test checklist**

- [ ] The Find Jobs navigation link opens `/jobs/`.
- [ ] All jobs appear with the default newest-first order.
- [ ] Searching `Python` in the quick search filters **titles only**.
- [ ] Advanced Search opens and closes when clicked.
- [ ] Company, location, title, and keyword filters work separately.
- [ ] Multiple advanced fields narrow results together.
- [ ] Keyword matches title, company, location, or description.
- [ ] Newest, oldest, title A–Z, and company A–Z sorting work.
- [ ] Result count changes with filters.
- [ ] No-match searches display the empty state.
- [ ] Clear Search and View All Jobs restore the unfiltered list.
- [ ] Entered search values remain visible after submission.

**Try these URLs** (results depend on the sample jobs in your database):

```text
http://127.0.0.1:8000/jobs/?q=Python
http://127.0.0.1:8000/jobs/?location=Toronto
http://127.0.0.1:8000/jobs/?keyword=remote&sort=title
http://127.0.0.1:8000/jobs/?company=Microsoft&sort=oldest
```

## What students learned

A browser sends query-string parameters through a `GET` form. Django reads them from `request.GET`, filters a QuerySet, sorts the results, and passes both the results and selected filters to the template. JavaScript controls only the visibility of the advanced form; Django performs the actual searching.

## Next lesson — Blogs app

Continue with your original `step-by-step.md`, starting at **Step 18: Create the Blogs app**. The existing search code does not need to be removed. When using that older guide, correct its inconsistent references to `blog/` versus `blogs/` and `jobs/views.py` versus `blogs/views.py`; the blog view and model belong in the `blogs` app.
