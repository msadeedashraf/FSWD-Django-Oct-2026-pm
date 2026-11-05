# Part 11 — Add a Job Form

## Step 40. Create `forms.py` in the jobs app

Create:

```text
jobs/forms.py
```

Add:

```python
from django import forms

from .models import Job


class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "location",
            "description",
            "apply_link",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Example: Python Developer",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "placeholder": "Example: Microsoft",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "Example: Toronto, ON",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe the job responsibilities and requirements",
                    "rows": 7,
                }
            ),
            "apply_link": forms.URLInput(
                attrs={
                    "placeholder": "https://example.com/apply",
                }
            ),
        }
```

---

## Step 41. Add the add-job URL

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
    path("<int:job_id>/", views.job_detail, name="job_detail"),
]
```

---

## Step 42. Add the add-job view

Open:

```text
jobs/views.py
```

Update:

```python
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreateJobForm
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

    # Quick search: title only
    if quick_search:
        jobs = jobs.filter(title__icontains=quick_search)

    # Advanced search
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

    # Sorting
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

            return redirect("jobs:job_detail", job_id=job.id)

    else:
        form = CreateJobForm()

    return render(
        request,
        "jobs/add_job.html",
        {"form": form},
    )```

This page is protected. Only logged-in users can add a job.

---

## Step 43. Create the add-job template

Create:

```text
jobs/templates/jobs/add_job.html
```

Add:

```html
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

Create:

```text
jobs/templates/jobs/job_detail.html
```

Add:

```html
{% extends "sharedpage.html" %}

{% block title %}
{{ job.title }} | JobZila
{% endblock title %}

{% block main %}
<section class="jobs-listing-section">

    <article class="jobs-listing">
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
            <strong>Posted:</strong>
            {{ job.created_at|date:"M d, Y" }}
        </p>

        <p>
            <strong>Description:</strong>
        </p>

        <p>
            {{ job.description }}
        </p>

        {% if job.apply_link %}
            <p>
                <a
                    href="{{ job.apply_link }}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="view-job-link"
                >
                    Apply for this Job
                </a>
            </p>
        {% endif %}

        <p>
            <a href="{% url 'jobs:job_list' %}">
                Back to Jobs
            </a>
        </p>
    </article>

</section>
{% endblock main %}
```



- Update the sharedpage.html

```
    {% if user.is_authenticated  %}


          <li><a href="">Add Blog</a></li>
          <li> <a href="{% url 'jobs:add_job' %}">Add Job</a></li>
          

          {% endif %}
```


- Add the css changes

```
/* ========================================
   ADD JOB FORM
======================================== */

.job-form-section {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 40px 20px;
}

.job-form-card {
    width: 100%;
    max-width: 750px;
    background: #fff;
    border: 1px solid #ccc;
    border-top: 5px solid #ff8500;
    border-radius: 5px;
    padding: 25px;
}

.job-form-card h2 {
    margin-bottom: 5px;
    color: #333;
}

.job-form-intro {
    margin-bottom: 25px;
    color: #666;
}

/* Works with {{ form.as_p }} */

.job-form p {
    margin-bottom: 18px;
}

.job-form label {
    display: block;
    margin-bottom: 6px;
    font-weight: bold;
    color: #333;
}

.job-form input,
.job-form textarea,
.job-form select {
    width: 100%;
    padding: 10px;
    margin-top: 4px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font-family: inherit;
    font-size: 16px;
}

.job-form textarea {
    min-height: 180px;
    resize: vertical;
}

.job-form input:focus,
.job-form textarea:focus,
.job-form select:focus {
    outline: none;
    border-color: #ff8500;
    box-shadow: 0 0 3px rgba(255,133,0,.35);
}

.job-form .helptext {
    display: block;
    margin-top: 5px;
    color: #666;
    font-size: 14px;
}

.job-form ul {
    margin: 6px 0 0 18px;
    color: #666;
    font-size: 14px;
}

.job-form .errorlist {
    margin: 6px 0;
    padding: 10px;
    border: 1px solid #dc3545;
    border-radius: 3px;
    background: #fff5f5;
    color: #c62828;
    list-style-position: inside;
}

/* Buttons */

.job-form-buttons {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 25px;
}

.job-form button {
    padding: 10px 18px;
    border: none;
    border-radius: 3px;
    background: #333;
    color: white;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
    transition: .2s;
}

.job-form button:hover {
    background: #ff8500;
}

.job-form-buttons a {
    color: #d96f00;
    text-decoration: none;
    font-weight: bold;
}

.job-form-buttons a:hover {
    text-decoration: underline;
}

@media (max-width:700px){

    .job-form-section{
        padding:20px 15px;
    }

    .job-form-card{
        padding:20px;
    }

    .job-form-buttons{
        flex-direction:column;
        align-items:stretch;
    }

    .job-form-buttons button,
    .job-form-buttons a{
        width:100%;
        text-align:center;
    }

}
```



Test:

```text
http://127.0.0.1:8000/jobs/add/
```

If you are not logged in, Django should send you to the login page.