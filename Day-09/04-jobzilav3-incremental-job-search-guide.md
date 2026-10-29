# 04 — JobZila v3: Add Job Search Incrementally

**Prerequisite:** Complete modules **01 → 02 → 03** in order. This is **Module 04**, not a new Django project. Start with the working Jobs app and populated database from the previous modules. This lesson builds search functionality in small changes that students can implement and test one at a time.

## What already exists — do not rebuild it

- Django project `jobzilav3`, project templates and static assets.
- `jobs` app, `Job` model (`title`, `company`, `location`, `description`, `apply_link`, `created_at`, `posted_by`), migrations and admin registration.
- `/jobs/` route, `jobs.job_list` view, and `jobs/templates/jobs/job_list.html` showing database records.
- `templates/sharedpage.html` with navigation and `static/css/styles.css` and `static/js/menu.js`.

**Rule:** Make each change in your *existing* project. Do not run `startproject`, `startapp`, or recreate the model. Do not replace the full stylesheet or delete the mobile menu JavaScript.

## Learning objectives

Read `request.GET`, filter Django QuerySets using `icontains` and `Q`, combine filters, sort, preserve form inputs, display a result count, and toggle advanced search with JavaScript.

## Step 18 — Verify the previous module

In PowerShell, from the folder containing `manage.py` (activate your existing `.venv` first):

```powershell
python manage.py check
python manage.py runserver
```

Open `http://127.0.0.1:8000/jobs/`. Verify existing jobs appear. If the list is empty, use `/admin/` to add at least five sample jobs with varied titles, companies, locations and descriptions. **Checkpoint:** all records display before adding search.

## Step 19 — Add a quick title search to the view

**Edit:** `jobs/views.py`. Replace only the existing `job_list` function with:

```python
from django.shortcuts import render
from .models import Job

def job_list(request):
    quick_search = request.GET.get("q", "").strip()
    jobs = Job.objects.all()

    if quick_search:
        jobs = jobs.filter(title__icontains=quick_search)

    jobs = jobs.order_by("-created_at")
    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "quick_search": quick_search,
    })
```

`request.GET` reads the URL query string. `title__icontains` matches part of a title without case sensitivity. **Checkpoint:** visiting `/jobs/?q=Python` displays only jobs with Python in their titles; `/jobs/` still shows everything.

## Step 20 — Add the quick-search form

**Edit:** `jobs/templates/jobs/job_list.html`. Immediately after `{% block main %}` and before the existing job listing, insert:

```html
<section class="jobs-search-section">
  <h2>Find Jobs</h2>
  <form method="GET" action="{% url 'jobs:job_list' %}">
    <label for="quick-search">Search by job title</label>
    <input id="quick-search" type="search" name="q"
           value="{{ quick_search }}" placeholder="Python Developer">
    <button type="submit">Search</button>
  </form>
</section>
```

Keep the existing `{% for job in jobs %}` loop. **Checkpoint:** submitting a title filters results and the entered term remains visible. Explain why GET is appropriate for shareable search URLs.

## Step 21 — Add a result count and empty state

**Edit:** `jobs/views.py`. Add `"result_count": jobs.count()` to the context dictionary. In the template, before the jobs loop, add:

```html
<h2>{{ result_count }} Job{{ result_count|pluralize }} Found</h2>
```

Inside the existing `{% for job in jobs %}` loop, immediately before `{% endfor %}`, add:

```html
{% empty %}
<p>No jobs found. Try another search.</p>
```

**Checkpoint:** an unmatched title displays `0 Jobs Found` and the empty-state message.

## Step 22 — Add advanced filters to the Django view

**Edit:** `jobs/views.py`. We now add title, company, location and keyword filters, while retaining quick title search. Replace the view with the complete final version below (do not add a second `job_list` function):

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

**Understand:** Each successive `.filter()` narrows the set (**AND**). The `Q(...) | Q(...)` keyword condition searches multiple fields (**OR**). Sorting is applied last. **Checkpoint:** test `/jobs/?company=Microsoft&location=Toronto` and `/jobs/?keyword=Python`.

## Step 23 — Replace the simple page with the completed search interface

**Edit:** `jobs/templates/jobs/job_list.html`. Now that the backend supports all filters, replace the temporary listing page with this complete template. It uses the existing `sharedpage.html` and does not introduce a new app.

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

**Checkpoint:** quick search, advanced form fields, selected sort value, result count, and clear-search link render. Advanced Search is initially hidden until the next JavaScript step. **Known limitation:** `View Job Details` has no `href` in the supplied implementation; it is a placeholder, not a functioning link.

## Step 24 — Append only the search CSS

**Edit:** `static/css/styles.css`. **Keep the existing CSS from Module 02.** Add the following at the very bottom. Do not paste the entire stylesheet from the old search guide because that duplicates earlier styles.

```css
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

**Checkpoint:** the search form and result cards have their own layout, and the existing header, footer and mobile menu still look correct.

## Step 25 — Add advanced-search toggle behavior

**Edit:** `static/js/menu.js`. Keep the existing hamburger-menu code from Module 02. Append only this code:

```javascript
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

**Checkpoint:** clicking Advanced Search opens and closes the panel and updates `aria-expanded`. Submitting advanced filters keeps the panel open when filters are active.

## Step 26 — Update the existing navigation label

**Edit:** `templates/sharedpage.html`. In the navigation, replace the old Jobs link with:

```html
<li><a href="{% url 'jobs:job_list' %}">Find Jobs</a></li>
```

Avoid adding a second duplicate Jobs link. Existing `/job-search/` from the static lesson is a separate old demonstration page; `/jobs/` is the live database-backed search.

## Step 27 — Test the full feature

Run:

```powershell
python manage.py check
python manage.py runserver
```

Test URLs:

```text
http://127.0.0.1:8000/jobs/
http://127.0.0.1:8000/jobs/?q=Python
http://127.0.0.1:8000/jobs/?location=Toronto
http://127.0.0.1:8000/jobs/?keyword=remote&sort=title
http://127.0.0.1:8000/jobs/?company=Microsoft&sort=oldest
```
## To reload the updated CSS press

- Save and refresh with Ctrl + Shift + R.

- [ ] Default shows all jobs, newest first.
- [ ] Quick search searches titles only.
- [ ] Title, company and location filter individually.
- [ ] Keyword searches title, company, location and description.
- [ ] Combined filters narrow results.
- [ ] Sorting works for newest, oldest, title and company.
- [ ] Result count and no-results message are correct.
- [ ] Inputs retain submitted values.
- [ ] Advanced Search toggle works, including after submission.
- [ ] Clear Search returns to all jobs.
- [ ] Header and mobile menu still work.

## Student exercises

1. Add six jobs and record expected counts for three search terms.
2. Explain why `q=Python` and `keyword=Python` can return different results.
3. Find a job that matches company and location together; explain the AND behavior.
4. Try an unmatched company; confirm the empty state.
5. Change the sort order and explain which field controls it.

## End of Module 05

Students now have a database-backed search page built on top of Modules 01–04. **Next module:** add a real job-detail route and page, or proceed to the Blogs app as a separate module. No new migration is required because this module does not change the `Job` model.
