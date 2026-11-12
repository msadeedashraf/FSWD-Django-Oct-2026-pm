# Module 13 — JobZila v3 Blog CRUD (Create, Read, Update, Delete)

This module continues the existing `blogs` app from Module 05 and follows the `CreateJobForm`, function-based views, `login_required`, ownership checks, confirmation screen, and `sharedpage.html` pattern used in Parts 11–12.

**Important:** Do not run `reset_seed_blogs` while following this module. That command deletes existing blog rows. Back up `db.sqlite3` and `media/` before changing the model.

## Step 1 — Add blog ownership to `blogs/models.py`

Your existing Blog model already contains `title`, `body`, `slug`, `link`, `date`, `author`, and `banner`. Keep those fields and add `posted_by` only:

```python
from django.conf import settings
from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField()
    link = models.URLField()
    date = models.DateTimeField()
    author = models.CharField(max_length=50)
    banner = models.ImageField()

    # Nullable so existing seeded posts survive the migration.
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
    )

    def __str__(self):
        return self.title
```

`posted_by` is the authenticated owner. The existing `author` remains a display string. Existing posts will have `posted_by=None`, so nobody can edit or delete them through these public CRUD views until you assign an owner. The nullable relationship also avoids deleting blog posts when a user is deleted.

Run:

```powershell
py manage.py makemigrations blogs
py manage.py migrate
```

## Step 2 — Create `blogs/forms.py`

Just like `CreateJobForm`, use a Django `ModelForm`. The internal fields (`posted_by`, `author`, `date`, `slug`, `link`) are deliberately excluded: the server will populate them.

```python
from django import forms
from .models import Blog

class CreateBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["title", "body", "banner"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Example: How to Prepare for a Python Interview"
            }),
            "body": forms.Textarea(attrs={
                "placeholder": "Write your article here...",
                "rows": 12,
            }),
            "banner": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }
```

**Why `request.FILES`?** The Blog model has an `ImageField`, unlike Jobs. File uploads need both `request.FILES` in the view and `enctype="multipart/form-data"` in the HTML form.

## Step 3 — Update `blogs/views.py`

Replace its existing contents with the following. The existing `blog` listing view and `blogs.html` template name are preserved.

```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .forms import CreateBlogForm
from .models import Blog


def blog(request):
    blogs = Blog.objects.all().order_by("-date")
    return render(request, "blogs/blogs.html", {"blogs": blogs})


def blog_detail(request, blog_id):
    post = get_object_or_404(Blog, id=blog_id)
    return render(request, "blogs/blog_detail.html", {"post": post})


def save_blog_metadata(request, post):
    """Set the derived fields not exposed in the ModelForm."""
    post.slug = (slugify(post.title) or "blog")[:35] + f"-{post.pk}"
    post.link = request.build_absolute_uri(
        reverse("blogs:blog_detail", args=[post.pk])
    )
    post.save(update_fields=["slug", "link"])


@login_required(login_url="/users/login/")
def add_blog(request):
    if request.method == "POST":
        form = CreateBlogForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.posted_by = request.user
            post.author = request.user.get_full_name()[:50] or request.user.username[:50]
            post.date = timezone.now()
            # Required legacy model fields; replaced after first save.
            post.slug = "blog"
            post.link = request.build_absolute_uri(reverse("blogs:blogs"))
            post.save()
            save_blog_metadata(request, post)
            return redirect("blogs:blog_detail", blog_id=post.id)
    else:
        form = CreateBlogForm()

    return render(request, "blogs/add_blog.html", {"form": form})


@login_required(login_url="/users/login/")
def edit_blog(request, blog_id):
    post = get_object_or_404(Blog, id=blog_id)
    if post.posted_by_id != request.user.id:
        raise PermissionDenied

    if request.method == "POST":
        form = CreateBlogForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            save_blog_metadata(request, post)
            return redirect("blogs:blog_detail", blog_id=post.id)
    else:
        form = CreateBlogForm(instance=post)

    return render(request, "blogs/edit_blog.html", {
        "form": form,
        "post": post,
    })


@login_required(login_url="/users/login/")
def delete_blog(request, blog_id):
    post = get_object_or_404(Blog, id=blog_id)
    if post.posted_by_id != request.user.id:
        raise PermissionDenied

    if request.method == "POST":
        post.delete()
        return redirect("blogs:blogs")

    return render(request, "blogs/delete_blog.html", {"post": post})
```

**Classroom discussion:** `form.save(commit=False)` lets us set server-controlled values before inserting a new record. `instance=post` makes the form update an existing row rather than create another. `PermissionDenied` produces HTTP 403; a URL hidden from the UI is not a security boundary. Deletion happens only after a POST with CSRF protection.

**Note about the existing `link` field:** The older seed guide populated it with a listing-page URL. New posts now store their absolute detail-page URL. This works with the existing required `URLField`, but an internal absolute URL may become stale when the domain changes. In a later refactor, remove `link` from the model and generate detail links with `{% url %}` everywhere.

## Step 4 — Update `blogs/urls.py`

Keep the existing namespace and listing route:

```python
from django.urls import path
from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.blog, name="blogs"),
    path("add/", views.add_blog, name="add_blog"),
    path("<int:blog_id>/", views.blog_detail, name="blog_detail"),
    path("<int:blog_id>/edit/", views.edit_blog, name="edit_blog"),
    path("<int:blog_id>/delete/", views.delete_blog, name="delete_blog"),
]
```

The main project's existing `path("blogs/", include("blogs.urls"))` does **not** need to change.

## Step 5 — Create `blogs/templates/blogs/add_blog.html`

```django
{% extends "sharedpage.html" %}

{% block title %}Add Blog | JobZila{% endblock title %}

{% block main %}
<section class="blog-form-section">
    <div class="blog-form-card">
        <h2>Add New Blog</h2>
        <p class="blog-form-intro">Complete the form to publish a new article.</p>

        <form method="POST" enctype="multipart/form-data" class="blog-form">
            {% csrf_token %}
            {{ form.non_field_errors }}

            <div class="blog-form-group">
                <label for="{{ form.title.id_for_label }}">Blog Title</label>
                {{ form.title }}
                {{ form.title.errors }}
            </div>

            <div class="blog-form-group">
                <label for="{{ form.body.id_for_label }}">Blog Content</label>
                {{ form.body }}
                {{ form.body.errors }}
            </div>

            <div class="blog-form-group">
                <label for="{{ form.banner.id_for_label }}">Banner Image</label>
                {{ form.banner }}
                {{ form.banner.errors }}
            </div>

            <div class="blog-form-buttons">
                <button type="submit">Save Blog</button>
                <a href="{% url 'blogs:blogs' %}">Cancel</a>
            </div>
        </form>
    </div>
</section>
{% endblock main %}
```

## Step 6 — Create `blogs/templates/blogs/blog_detail.html`

```django
{% extends "sharedpage.html" %}

{% block title %}{{ post.title }} | JobZila{% endblock title %}

{% block main %}
<section class="blogs-section">
    <article class="blog-card blog-detail-card">
        <h2>{{ post.title }}</h2>
        <p>By <strong>{{ post.author }}</strong> | {{ post.date|date:"M d, Y" }}</p>

        {% if post.banner %}
            <img class="blog-banner" src="{{ post.banner.url }}" alt="{{ post.title }}">
        {% endif %}

        <div class="blog-detail-body">{{ post.body|linebreaks }}</div>

        {% if user.is_authenticated and post.posted_by_id == user.id %}
            <div class="blog-management-actions">
                <a class="edit-blog-link" href="{% url 'blogs:edit_blog' post.id %}">Edit Blog</a>
                <a class="delete-blog-link" href="{% url 'blogs:delete_blog' post.id %}">Delete Blog</a>
            </div>
        {% endif %}

        <p class="back-to-blogs"><a href="{% url 'blogs:blogs' %}">Back to Blogs</a></p>
    </article>
</section>
{% endblock main %}
```

**Template note:** Django templates do not reliably support arbitrary Python expressions, but this direct field comparison is supported by Django's `{% if %}` tag.

## Step 7 — Create `blogs/templates/blogs/edit_blog.html`

```django
{% extends "sharedpage.html" %}

{% block title %}Edit {{ post.title }} | JobZila{% endblock title %}

{% block main %}
<section class="blog-form-section">
    <div class="blog-form-card">
        <h2>Edit Blog</h2>
        <p class="blog-form-intro">Update <strong>{{ post.title }}</strong>.</p>

        <form method="POST" enctype="multipart/form-data" class="blog-form">
            {% csrf_token %}
            {{ form.as_p }}
            <div class="blog-form-buttons">
                <button type="submit">Update Blog</button>
                <a href="{% url 'blogs:blog_detail' post.id %}">Cancel</a>
            </div>
        </form>
    </div>
</section>
{% endblock main %}
```

`instance=post` in the view prepopulates the form. If the user leaves the existing image unchanged, Django retains it. Selecting a new image updates the database reference; the old file is not automatically deleted from storage.

## Step 8 — Create `blogs/templates/blogs/delete_blog.html`

```django
{% extends "sharedpage.html" %}

{% block title %}Delete {{ post.title }} | JobZila{% endblock title %}

{% block main %}
<section class="blog-form-section">
    <div class="blog-form-card delete-blog-card">
        <h2>Delete Blog</h2>
        <p class="delete-blog-warning">Are you sure you want to permanently delete this article?</p>
        <h3>{{ post.title }}</h3>
        <p>By {{ post.author }}</p>
        <p>This action cannot be undone.</p>

        <form method="POST" class="delete-blog-form">
            {% csrf_token %}
            <button type="submit" class="delete-blog-button">Yes, Delete Blog</button>
            <a href="{% url 'blogs:blog_detail' post.id %}">Cancel</a>
        </form>
    </div>
</section>
{% endblock main %}
```

## Step 9 — Update the existing `blogs/templates/blogs/blogs.html`

**Do not replace the entire listing template.** Change the title link and the Read More link inside `{% for b in blogs %}`. Both currently use `{{ b.link }}`.

```django
<h3>
    <a href="{% url 'blogs:blog_detail' b.id %}">{{ b.title }}</a>
</h3>
```

And:

```django
<a class="read-blog-link" href="{% url 'blogs:blog_detail' b.id %}">
    Read More
</a>
```

Now both existing seeded posts and newly created posts open their own detail pages, regardless of their stored `link` value.

## Step 10 — Update the navigation in `sharedpage.html`

Your Part 11 guide already includes a placeholder `Add Blog` item. Replace **that item** rather than adding a duplicate:

```django
{% if user.is_authenticated %}
    <li><a href="{% url 'blogs:add_blog' %}">Add Blog</a></li>
    <li><a href="{% url 'jobs:add_job' %}">Add Job</a></li>
{% endif %}
```

Keep the existing public Blogs menu link `{% url 'blogs:blogs' %}`.

## Step 11 — Add CSS to your existing `styles.css`

Append this after your existing Blog and Job CSS. It deliberately mirrors the orange/charcoal JobZila design.

```css
/* ========================================
   BLOG CRUD FORMS AND ACTIONS
======================================== */
.blog-form-section {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 40px 20px;
}

.blog-form-card {
    width: 100%;
    max-width: 750px;
    background: #fff;
    border: 1px solid #ccc;
    border-top: 5px solid #ff8500;
    border-radius: 5px;
    padding: 25px;
}

.blog-form-card h2 { color: #333; margin-bottom: 8px; }
.blog-form-intro { color: #666; margin-bottom: 25px; }
.blog-form p, .blog-form-group { margin-bottom: 18px; }
.blog-form label { display: block; margin-bottom: 6px; font-weight: bold; }

.blog-form input, .blog-form textarea, .blog-form select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 3px;
    font: inherit;
}

.blog-form input[type="checkbox"] { width: auto; }
.blog-form textarea { min-height: 200px; resize: vertical; }
.blog-form input:focus, .blog-form textarea:focus {
    outline: none;
    border-color: #ff8500;
    box-shadow: 0 0 3px rgba(255, 133, 0, .35);
}

.blog-form .errorlist { color: #c62828; margin: 6px 0; }
.blog-form-buttons, .blog-management-actions, .delete-blog-form {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-top: 24px;
}

.blog-form button, .edit-blog-link, .delete-blog-button {
    padding: 10px 18px;
    border: 0;
    border-radius: 3px;
    background: #333;
    color: white;
    text-decoration: none;
    font: inherit;
    cursor: pointer;
}

.blog-form button:hover, .edit-blog-link:hover { background: #ff8500; }
.blog-form-buttons a, .delete-blog-form a, .back-to-blogs a {
    color: #d96f00;
    text-decoration: none;
}

.delete-blog-link {
    padding: 9px 15px;
    border: 1px solid #c62828;
    border-radius: 3px;
    color: #c62828;
    text-decoration: none;
}
.delete-blog-link:hover { background: #c62828; color: #fff; }
.delete-blog-card { max-width: 600px; }
.delete-blog-warning {
    padding: 12px;
    margin: 15px 0;
    background: #fff5f5;
    border: 1px solid #c62828;
    color: #a61b1b;
}
.delete-blog-button { background: #c62828; }
.delete-blog-button:hover { background: #941c1c; }
.blog-detail-body { margin-top: 20px; overflow-wrap: anywhere; }
.blog-management-actions { border-top: 1px solid #ddd; padding-top: 20px; }
.back-to-blogs { margin-top: 20px; }

@media (max-width: 700px) {
    .blog-form-section { padding: 20px 15px; }
    .blog-form-card { padding: 20px; }
    .blog-form-buttons, .blog-management-actions, .delete-blog-form {
        flex-direction: column;
        align-items: stretch;
    }
    .blog-form-buttons button, .edit-blog-link, .delete-blog-link,
    .delete-blog-button { width: 100%; text-align: center; }
}
```

## Step 12 — Verify media configuration

The Module 05C image guide already covered this. Confirm the following still exists in the project settings:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

And in the **main** project `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

This serves uploaded files only during local development. Do not use it as production media hosting.

## Step 13 — Optional: Assign existing seeded posts to a trusted account

Old seed records have no owner. To let a teacher edit them through the new UI, run the following **only after choosing the correct account** (replace `YOUR_USERNAME`):

```powershell
py manage.py shell
```

```python
from django.contrib.auth import get_user_model
from blogs.models import Blog

User = get_user_model()
owner = User.objects.get(username="YOUR_USERNAME")
updated = Blog.objects.filter(posted_by__isnull=True).update(posted_by=owner)
print("Assigned posts:", updated)
exit()
```

This does not alter blog text, images, or display author names. Do not automatically assign legacy posts to whichever user happens to be logged in.

## Step 14 — Test the complete CRUD workflow

```powershell
py manage.py check
py manage.py runserver
```

| Test | URL | Expected result |
|---|---|---|
| Public list | `http://127.0.0.1:8000/blogs/` | Existing blog cards appear |
| Public detail | `http://127.0.0.1:8000/blogs/1/` | Article and image appear if ID 1 exists |
| Create | `http://127.0.0.1:8000/blogs/add/` | Login required; valid form creates a blog |
| Edit | `/blogs/<id>/edit/` | Owner sees prefilled form; saved changes appear |
| Delete GET | `/blogs/<id>/delete/` | Owner sees confirmation; nothing deleted yet |
| Delete POST | Same URL | Owner's article deleted and redirected to list |
| Unauthorized edit/delete | Other user's blog | HTTP 403 |
| Anonymous edit/delete | Any blog | Redirect to login |

**Important test:** Upload a banner while creating a blog. If the form does not save, check `enctype="multipart/form-data"`, `request.FILES`, Pillow, and your media settings.

**What students learned:** `ModelForm`, GET vs POST, `request.FILES`, model instances, server-controlled metadata, ownership with `ForeignKey`, authentication, authorization (403), CSRF, redirects, URL namespaces, and safe delete confirmation.

### Future improvements (not required for this module)

- Replace the legacy `link` field with generated internal URLs.
- Add draft/published status and pagination.
- Validate uploaded image size and file type; secure media serving in production.
- Handle orphaned banner files after updates/deletes.
- Use transaction-safe logic and a unique slug strategy if switching from ID-based URLs to slug-based URLs.
