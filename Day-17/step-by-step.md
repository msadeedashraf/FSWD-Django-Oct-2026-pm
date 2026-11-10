# Part 12 — Add a edit/delete Job Form

## Step 1. Add PermissionDenied to `jobs/views.py` in the jobs app


```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreateJobForm
from .models import Job


def job_list(request):
    quick_search = request.GET.get("q", "").strip()

    title = request.GET.get("title", "").strip()
    company = request.GET.get("company", "").strip()
    location = request.GET.get("location", "").strip()
    keyword = request.GET.get("keyword", "").strip()
    sort = request.GET.get("sort", "newest")

    jobs = Job.objects.all()

    if quick_search:
        jobs = jobs.filter(title__icontains=quick_search)

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

    if sort == "oldest":
        jobs = jobs.order_by("created_at")
    elif sort == "title":
        jobs = jobs.order_by("title")
    elif sort == "company":
        jobs = jobs.order_by("company")
    else:
        jobs = jobs.order_by("-created_at")

    advanced_search_active = any(
        [
            title,
            company,
            location,
            keyword,
            sort != "newest",
        ]
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


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    return render(
        request,
        "jobs/job_detail.html",
        {"job": job},
    )


@login_required(login_url="/users/login/")
def add_job(request):
    if request.method == "POST":
        form = CreateJobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()

            return redirect(
                "jobs:job_detail",
                job_id=job.id,
            )
    else:
        form = CreateJobForm()

    return render(
        request,
        "jobs/add_job.html",
        {
            "form": form,
            "page_title": "Add New Job",
            "button_text": "Save Job",
        },
    )


@login_required(login_url="/users/login/")
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Only the person who posted the job can edit it.
    if job.posted_by != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = CreateJobForm(
            request.POST,
            instance=job,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "jobs:job_detail",
                job_id=job.id,
            )
    else:
        form = CreateJobForm(instance=job)

    return render(
        request,
        "jobs/edit_job.html",
        {
            "form": form,
            "job": job,
        },
    )


@login_required(login_url="/users/login/")
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Only the person who posted the job can delete it.
    if job.posted_by != request.user:
        raise PermissionDenied

    if request.method == "POST":
        job.delete()
        return redirect("jobs:job_list")

    return render(
        request,
        "jobs/delete_job.html",
        {"job": job},
    )


```

---

## Step 2. Update jobs/urls.py

Open:

```text
jobs/urls.py
```

Update:

```python
from django.urls import path

from . import views


app_name = "jobs"


urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("add/", views.add_job, name="add_job"),

    path(
        "<int:job_id>/",
        views.job_detail,
        name="job_detail",
    ),

    path(
        "<int:job_id>/edit/",
        views.edit_job,
        name="edit_job",
    ),

    path(
        "<int:job_id>/delete/",
        views.delete_job,
        name="delete_job",
    ),
]
```

---

## Step 3. Create edit_job.html

Open:

```text
jobs/templates/jobs/edit_job.html
```

Update:

```python
{% extends "sharedpage.html" %}

{% block title %}
Edit {{ job.title }} | JobZila
{% endblock title %}

{% block main %}
<section class="job-form-section">

    <div class="job-form-card">

        <h2>Edit Job</h2>

        <p class="job-form-intro">
            Update the information for
            <strong>{{ job.title }}</strong>.
        </p>

        <form method="POST" class="job-form">
            {% csrf_token %}

            {{ form.as_p }}

            <div class="job-form-buttons">
                <button type="submit">
                    Update Job
                </button>

                <a href="{% url 'jobs:job_detail' job.id %}">
                    Cancel
                </a>
            </div>
        </form>

    </div>

</section>
{% endblock main %}
---

## Step 43. Create the add-job template

Create:

```text
jobs/templates/jobs/add_job.html
```

Add:

```python
{% extends 'sharedpage.html' %}

{% block title %}Add Job | JobZila{% endblock title %}

{% block main %}
<section class="job-form-section">

    <div class="job-form-card">
        <h2>Add New Job</h2>

        <p class="job-form-intro">
            Complete the form below to publish a new job opportunity.
        </p>

        <form method="POST" class="job-form">
            {% csrf_token %}

            {{ form.non_field_errors }}

            <div class="job-form-group">
                <label for="{{ form.title.id_for_label }}">
                    Job Title
                </label>

                {{ form.title }}
                {{ form.title.errors }}
            </div>

            <div class="job-form-group">
                <label for="{{ form.company.id_for_label }}">
                    Company
                </label>

                {{ form.company }}
                {{ form.company.errors }}
            </div>

            <div class="job-form-group">
                <label for="{{ form.location.id_for_label }}">
                    Location
                </label>

                {{ form.location }}
                {{ form.location.errors }}
            </div>

            <div class="job-form-group">
                <label for="{{ form.description.id_for_label }}">
                    Job Description
                </label>

                {{ form.description }}
                {{ form.description.errors }}
            </div>

            <div class="job-form-group">
                <label for="{{ form.apply_link.id_for_label }}">
                    Application Link
                </label>

                {{ form.apply_link }}

                <small>
                    Optional: enter the website where applicants can apply.
                </small>

                {{ form.apply_link.errors }}
            </div>

            <div class="job-form-buttons">
                <button type="submit">
                    Save Job
                </button>

                <a href="{% url 'jobs:job_list' %}">
                    Cancel
                </a>
            </div>
        </form>
    </div>

</section>
{% endblock main %}
```

## Step 4: Create delete_job.html

Create:

```text
jobs/templates/jobs/delete_job.html
```

Add:

```python
{% extends "sharedpage.html" %}

{% block title %}
Delete {{ job.title }} | JobZila
{% endblock title %}

{% block main %}
<section class="job-form-section">

    <div class="job-form-card delete-job-card">

        <h2>Delete Job</h2>

        <p class="delete-warning">
            Are you sure you want to permanently delete this job?
        </p>

        <div class="delete-job-information">
            <h3>{{ job.title }}</h3>

            <p>
                <strong>Company:</strong>
                {{ job.company }}
            </p>

            <p>
                <strong>Location:</strong>
                {{ job.location }}
            </p>
        </div>

        <p>
            This action cannot be undone.
        </p>

        <form method="POST" class="delete-job-form">
            {% csrf_token %}

            <button type="submit" class="delete-job-button">
                Yes, Delete Job
            </button>

            <a href="{% url 'jobs:job_detail' job.id %}">
                Cancel
            </a>
        </form>

    </div>

</section>
{% endblock main %}
```

## Step 5: Add Edit and Delete buttons to job_detail.html

- Update your job-detail page:

```python 
{% extends "sharedpage.html" %}

{% block title %}
{{ job.title }} | JobZila
{% endblock title %}

{% block main %}
<section class="jobs-listing-section">

    <article class="jobs-listing job-detail-card">

        <h2>{{ job.title }}</h2>

        <p>
            <strong>Company:</strong>
            {{ job.company }}
        </p>

        <p>
            <strong>Location:</strong>
            {{ job.location }}
        </p>
        <p>
            <strong>Create By:</strong>
            {{ job.posted_by }}
        </p>

        <p>
            <strong>Posted:</strong>
            {{ job.created_at|date:"M d, Y" }}
        </p>

        <div class="job-detail-description">
            <h3>Job Description</h3>

            <p>
                {{ job.description|linebreaks }}
            </p>
        </div>

        {% if job.apply_link %}
            <a
                href="{{ job.apply_link }}"
                target="_blank"
                rel="noopener noreferrer"
                class="view-job-link"
            >
                Apply for this Job
            </a>
        {% endif %}

        {% if user == job.posted_by %}
            <div class="job-management-actions">

                <a
                    href="{% url 'jobs:edit_job' job.id %}"
                    class="edit-job-link"
                >
                    Edit Job
                </a>

                <a
                    href="{% url 'jobs:delete_job' job.id %}"
                    class="delete-job-link"
                >
                    Delete Job
                </a>

            </div>
        {% endif %}

        <p class="back-to-jobs">
            <a href="{% url 'jobs:job_list' %}">
                Back to Jobs
            </a>
        </p>

    </article>

</section>
{% endblock main %}
```

## Step : 7 Add the link job details link on the job_list.html

- add the link 
  
```html
<a
                    
                    class="view-job-link"
                    href="{% url 'jobs:job_detail' job.id %}"
                >
                    View Job Details
                </a>
```

```python 
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
                            Job title
                        </option>

                        <option
                            value="company"
                            {% if sort == "company" %}selected{% endif %}
                        >
                            Company 
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
                    href="{% url 'jobs:job_detail' job.id %}"
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


## Step 8 : Add the CSS

- Add the css changes

```css
/* ========================================
   EDIT AND DELETE JOB
======================================== */

.job-management-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
}

.edit-job-link,
.delete-job-link {
    display: inline-block;
    padding: 9px 15px;
    border-radius: 3px;
    text-decoration: none;
    font-weight: bold;
}

.edit-job-link {
    background-color: #333;
    color: white;
}

.edit-job-link:hover {
    background-color: #ff8500;
}

.delete-job-link {
    border: 1px solid #c62828;
    background-color: white;
    color: #c62828;
}

.delete-job-link:hover {
    background-color: #c62828;
    color: white;
}

.back-to-jobs {
    margin-top: 20px;
}

.back-to-jobs a {
    color: #d96f00;
    text-decoration: none;
}

.back-to-jobs a:hover {
    text-decoration: underline;
}


/* Delete confirmation */

.delete-job-card {
    max-width: 600px;
}

.delete-warning {
    margin: 15px 0;
    padding: 12px;
    border: 1px solid #c62828;
    border-radius: 3px;
    background-color: #fff5f5;
    color: #a61b1b;
    font-weight: bold;
}

.delete-job-information {
    margin-bottom: 15px;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 3px;
    background-color: #f8f8f8;
}

.delete-job-information h3 {
    margin-bottom: 5px;
}

.delete-job-form {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 25px;
}

.delete-job-button {
    padding: 10px 18px;
    border: none;
    border-radius: 3px;
    background-color: #c62828;
    color: white;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
}

.delete-job-button:hover {
    background-color: #941c1c;
}

.delete-job-form a {
    color: #d96f00;
    text-decoration: none;
}

.delete-job-form a:hover {
    text-decoration: underline;
}

@media screen and (max-width: 700px) {
    .job-management-actions,
    .delete-job-form {
        flex-direction: column;
        align-items: stretch;
    }

    .edit-job-link,
    .delete-job-link,
    .delete-job-button,
    .delete-job-form a {
        width: 100%;
        text-align: center;
    }
}
```

## Step 7: Test the full CRUD workflow

-  Run the server:

```powershell
py manage.py runserver
```

```text
http://127.0.0.1:8000/jobs/add/
```

