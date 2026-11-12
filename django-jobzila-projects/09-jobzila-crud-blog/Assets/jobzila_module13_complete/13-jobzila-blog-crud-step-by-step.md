# Module 13 — JobZila v3: Rebuild Blog Data and Implement Full CRUD

**Continuation of Module 05 (Blog app), Module 05C (seeded blog images), Part 11 (Add Job), and Part 12 (Edit/Delete Job).** This module is written as a student lab with explanations, full replacement files, commands, and validation. It uses the existing `blogs` app, `sharedpage.html`, and your attached Insights listing design.

## What we have already achieved and why this module exists

1. Module 05 introduced `Blog(title, body, slug, link, date, author, banner)`, admin registration, `/blogs/`, and `blogs.html`.
2. Module 05C created seeded demonstration blogs and optional images. Its `reset_seed_blogs` command deletes Blog rows; **do not run it after this update**, because its assumptions may no longer match the new model.
3. Parts 11–12 established the Job CRUD pattern: `ModelForm`, function-based views, `login_required`, ownership checks, URL names, shared templates, and POST-only deletion.
4. We now need Blog CRUD with real ownership, while preserving the *editorial team* label as a separate public byline.

### The key data-model decision

`posted_by` is a `ForeignKey` to Django's configured User model. The physical SQLite column is `posted_by_id`, containing an **integer user primary key**, not the username. `author` is a `CharField` containing the editorial team label. A separate editorial-team database table is unnecessary for this lesson. The Python dictionary in `author_mapping.py` is configuration, **not a database table**.

| Username used for lookup | Editorial byline (`author`) |
|---|---|
| `sadeed` | JobZila Editorial Team |
| `hazla` | Career Research Desk |
| `frank` | Technology Learning Team |
| `sara` | JobZila Editorial Team |

**This mapping is our agreed demonstration configuration; adjust the dictionary if the desired editorial assignments differ.** The user IDs are not assumed to be 1, 2, 3, 4; Django resolves them from the existing accounts.

## Project files supplied

Copy the supplied `blogs/` files into your existing Django project. **Do not replace the entire project or delete the `jobs` or `users` apps.**

```text
blogs/
├── models.py
├── forms.py
├── views.py
├── urls.py
├── author_mapping.py
├── blog_crud.css                # append to existing static/css/styles.css
├── templates/blogs/
│   ├── blogs.html
│   ├── add_blog.html
│   ├── blog_detail.html
│   ├── edit_blog.html
│   └── delete_blog.html
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── seed_blog_data.py
```

## Step 1 — Protect the database and media

The requested *true table rebuild* destroys every existing Blog row, including its IDs, ownership, and stored banner paths. It **does not delete image files automatically**. Back up both the SQLite database and `media/`. Do this on a disposable local teaching database, **not production**.

```powershell
# Run from the directory containing manage.py
Copy-Item .\db.sqlite3 .\db.sqlite3.before_blog_rebuild
if (Test-Path .\media) { Copy-Item .\media .\media.before_blog_rebuild -Recurse }
```

Confirm your existing four users first:

```powershell
py manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); print(list(U.objects.filter(username__in=['sadeed','hazla','frank','sara']).values_list('id','username')))"
```

Create missing accounts using your existing registration flow or `py manage.py createsuperuser` as appropriate. **Do not automatically invent passwords or overwrite existing accounts.**

## Step 2 — Final model and database reasoning

We intentionally use `on_delete=PROTECT` and require an owner. That prevents accidental user deletion from orphaning a blog. `slug` is unique for readable identifiers, but the public detail URL uses the numeric blog ID. `banner` is optional so classroom demo posts work without image files. The legacy `link` field is retained but is not used for internal navigation.


**File: `blogs/models.py`**

```python
from django.conf import settings
from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(unique=True)
    link = models.URLField(blank=True)
    date = models.DateTimeField()
    author = models.CharField(max_length=50)  # Editorial team byline
    banner = models.ImageField(upload_to='blog_banners/', blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='blog_posts',
    )

    @property
    def author_display_name(self):
        return self.posted_by.get_full_name() or self.posted_by.username

    def __str__(self):
        return self.title
```

## Step 3 — Rebuild the `blogs_blog` table using a Django migration

**Do not run raw `DROP TABLE blogs_blog` in SQLite** and then hope `makemigrations` repairs the schema: Django's migration history would still say the model exists. Instead, create a migration that explicitly performs `DeleteModel` followed by `CreateModel`. This genuinely drops and recreates the table, and records the change in Django migration history.

**First:** make sure `blogs/models.py` contains the final model from Step 2. Then create an empty migration:

```powershell
py manage.py makemigrations blogs --empty --name rebuild_blog_table
```

Open the newly generated `blogs/migrations/00XX_rebuild_blog_table.py`. **Keep its generated `dependencies` exactly as Django wrote them**; add `migrations.swappable_dependency(settings.AUTH_USER_MODEL)` to that list if it is not already represented in the dependency chain. Replace its `operations` with the following (retain the generated file's imports/dependencies and add `from django.conf import settings` if needed):

```python
operations = [
    migrations.DeleteModel(name='Blog'),
    migrations.CreateModel(
        name='Blog',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                       serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=255)),
            ('body', models.TextField()),
            ('slug', models.SlugField(unique=True)),
            ('link', models.URLField(blank=True)),
            ('date', models.DateTimeField()),
            ('author', models.CharField(max_length=50)),
            ('banner', models.ImageField(upload_to='blog_banners/', blank=True)),
            ('posted_by', models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='blog_posts',
            )),
        ],
    ),
]
```

Make sure these imports are available at the top:

```python
from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
```

**Important:** the `id` example assumes the project uses Django's `BigAutoField` default. If your existing migrations use `AutoField`, match the project's actual primary-key configuration instead. If other tables have foreign keys to `Blog`, this destructive migration may be blocked by database constraints; inspect and handle those relationships first. Never fake a migration just to make it pass.

Inspect the SQL and migration plan, then apply:

```powershell
py manage.py sqlmigrate blogs 00XX  # replace 00XX with the generated migration number
py manage.py migrate --plan
py manage.py migrate
py manage.py makemigrations blogs --check --dry-run
```

**Expected:** `blogs_blog` exists again with no rows; `posted_by_id` references your User table; no pending Blog model changes. If Django reports an unapplied migration or a foreign-key constraint failure, stop and fix it before seeding.

**Why not use the earlier `reset_blog_table.py` command?** Runtime schema-editor drops can be fragile with SQLite foreign-key enforcement and don't create a corresponding migration record. This migration approach is safer for a reproducible lesson.

## Step 4 — Configure the username → editorial team mapping


**File: `blogs/author_mapping.py`**

```python
"""Single source of truth for JobZila's editorial bylines."""
EDITORIAL_BY_USERNAME = {
    "sadeed": "JobZila Editorial Team",
    "hazla": "Career Research Desk",
    "frank": "Technology Learning Team",
    "sara": "JobZila Editorial Team",
}


def editorial_team_for(user):
    return EDITORIAL_BY_USERNAME.get(user.username.lower(), "JobZila Editorial Team")
```

The mapping determines the value of `author` **at creation time**. `posted_by_id` remains the user ID. Editing a blog will not silently change its original owner or editorial label. If a team name changes later, update the dictionary for future posts and separately decide whether existing bylines should change.

## Step 5 — Seed 100 blogs with real owners


**File: `blogs/management/commands/seed_blog_data.py`**

```python
"""Non-destructive demo blog seed with real owner accounts and editorial bylines.

Run: python manage.py seed_blog_data --count 100
The command only creates records and never deletes existing blogs.
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from blogs.author_mapping import EDITORIAL_BY_USERNAME
from blogs.models import Blog

TOPICS = [
    ("Career Planning", "Build a realistic career plan", "career"),
    ("Resume Writing", "Improve your resume for recruiters", "resume"),
    ("Interview Preparation", "Prepare for your next interview", "interview"),
    ("Python Skills", "Learn practical Python for work", "python"),
    ("SQL Skills", "Use SQL to solve business problems", "sql"),
    ("Cloud Computing", "Understand cloud career pathways", "cloud"),
    ("Data Analytics", "Develop a data analytics portfolio", "analytics"),
    ("Artificial Intelligence", "Explore AI skills for modern jobs", "ai"),
    ("Networking", "Build a professional network", "network"),
    ("Career Growth", "Plan your next professional milestone", "growth"),
]


class Command(BaseCommand):
    help = "Create demo blog posts with mapped Django users and editorial bylines; no destructive reset."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        count = options["count"]
        if not 1 <= count <= 1000:
            raise CommandError("--count must be between 1 and 1000")
        User = get_user_model()
        names = list(EDITORIAL_BY_USERNAME)
        users = {}
        for name in names:
            try:
                users[name] = User.objects.get(username__iexact=name)
            except User.DoesNotExist:
                raise CommandError(f"Missing user '{name}'. Create the account first.")
            except User.MultipleObjectsReturned:
                raise CommandError(f"Multiple accounts match '{name}'")

        created = 0
        with transaction.atomic():
            for index in range(count):
                topic, heading, key = TOPICS[index % len(TOPICS)]
                serial = index + 1
                slug = f"{slugify(key)}-{serial:04d}"
                if Blog.objects.filter(slug=slug).exists():
                    continue  # repeatable: never overwrite an existing article
                username = names[index % len(names)]
                user = users[username]
                if options["dry_run"]:
                    created += 1
                    continue
                post = Blog.objects.create(
                    title=f"{heading}: Guide {serial}",
                    body=(f"{topic}: Start by defining a clear goal and evaluating your current skills.\n\n"
                          "Create a small practical project, document the results, and ask for feedback.\n\n"
                          "Use this demonstration article as a starting point and replace it with original editorial content."),
                    slug=slug,
                    link="",  # Internal links are generated by Django URL reversing
                    date=timezone.now() - timedelta(days=index),
                    author=EDITORIAL_BY_USERNAME[username],
                    posted_by=user,
                    banner="",  # demo posts have a placeholder instead of an uploaded image
                )
                created += 1
            if options["dry_run"]:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            f"{'Would create' if options['dry_run'] else 'Created'} {created} demo blogs."
        ))
```

The seed command checks that all four users exist, assigns owners round-robin, and writes the corresponding editorial team to `author`. It creates demonstration text and **no banner images**. Existing image-rich seed content from Module 05C is not recreated by this simplified script. It skips any already-used demo slugs, so running it twice does not duplicate those entries.

```powershell
py manage.py seed_blog_data --count 100 --dry-run
py manage.py seed_blog_data --count 100
```

Check actual IDs and bylines:

```powershell
py manage.py shell -c "from blogs.models import Blog; print('Total:', Blog.objects.count()); print(list(Blog.objects.values_list('id','posted_by_id','posted_by__username','author')[:12]))"
```

You should see 100 records after a fresh rebuild. `posted_by_id` values depend on your actual User table.

## Step 6 — Create the ModelForm (same approach as Jobs)


**File: `blogs/forms.py`**

```python
from django import forms
from .models import Blog


class CreateBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'body', 'banner']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Article title'}),
            'body': forms.Textarea(attrs={'rows': 12, 'placeholder': 'Write your article'}),
            'banner': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
```

The form exposes only title, body, and banner. **Never include `posted_by` or `author` as editable public form fields**: the server assigns those values, preventing users from impersonating other authors. `ImageField` needs Pillow (`py -m pip install Pillow`) and multipart form encoding.

## Step 7 — Build the views (CRUD + authorization)


**File: `blogs/views.py`**

```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from .author_mapping import editorial_team_for
from .forms import CreateBlogForm
from .models import Blog


def blog(request):
    blogs = Blog.objects.select_related('posted_by').order_by('-date')
    return render(request, 'blogs/blogs.html', {'blogs': blogs})


def blog_detail(request, blog_id):
    post = get_object_or_404(Blog.objects.select_related('posted_by'), pk=blog_id)
    return render(request, 'blogs/blog_detail.html', {'post': post})


def unique_slug(title, exclude_pk=None):
    base = (slugify(title) or 'article')[:40]
    slug = base
    index = 2
    qs = Blog.objects.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f'{base}-{index}'
        index += 1
    return slug


@login_required(login_url='/users/login/')
def add_blog(request):
    form = CreateBlogForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.posted_by = request.user
        post.author = editorial_team_for(request.user)
        post.date = timezone.now()
        post.slug = unique_slug(post.title)
        post.save()
        return redirect('blogs:blog_detail', blog_id=post.pk)
    return render(request, 'blogs/add_blog.html', {'form': form})


@login_required(login_url='/users/login/')
def edit_blog(request, blog_id):
    post = get_object_or_404(Blog, pk=blog_id)
    if post.posted_by_id != request.user.pk:
        raise PermissionDenied
    form = CreateBlogForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        # Keep slug stable so existing article links remain valid.
        post.save()
        return redirect('blogs:blog_detail', blog_id=post.pk)
    return render(request, 'blogs/edit_blog.html', {'form': form, 'post': post})


@login_required(login_url='/users/login/')
def delete_blog(request, blog_id):
    post = get_object_or_404(Blog, pk=blog_id)
    if post.posted_by_id != request.user.pk:
        raise PermissionDenied
    if request.method == 'POST':
        post.delete()
        return redirect('blogs:blogs')
    return render(request, 'blogs/delete_blog.html', {'post': post})
```

**How it works:**

- **Create:** `form.save(commit=False)` allows server assignment of `posted_by`, `author`, `date`, and a unique slug before saving.
- **Read:** the listing and detail pages are public; `select_related('posted_by')` avoids repeated User queries when rendering bylines.
- **Update:** `instance=post` updates the same row; only the owner passes the ID check. Slugs stay stable after title edits.
- **Delete:** GET displays a confirmation page; only a CSRF-protected POST deletes the record.
- **Authorization:** `login_required` sends guests to `/users/login/`; unauthorized logged-in users receive HTTP 403. Hiding edit buttons alone is **not** security.

## Step 8 — Register Blog URLs


**File: `blogs/urls.py`**

```python
from django.urls import path
from . import views

app_name = 'blogs'
urlpatterns = [
    path('', views.blog, name='blogs'),
    path('add/', views.add_blog, name='add_blog'),
    path('<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('<int:blog_id>/edit/', views.edit_blog, name='edit_blog'),
    path('<int:blog_id>/delete/', views.delete_blog, name='delete_blog'),
]
```

Confirm the main project's `urls.py` already includes:

```python
path('blogs/', include('blogs.urls')),
```

Keep the existing `blogs:blogs` URL name so the shared navigation remains compatible.

## Step 9 — Update the attached Insights listing page


**File: `blogs/templates/blogs/blogs.html`**

```html
{% extends "sharedpage.html" %}
{% block title %}Career Insights | JobZila{% endblock title %}
{% block main %}
<section class="blogs-section">
  <header class="blogs-header">
    <span class="blogs-eyebrow">JobZila / Insights</span>
    <h1>Career advice worth reading.</h1>
    <p>Practical articles on job searching, interviews, skills, and career growth.</p>
  </header>
  <div class="blogs-toolbar">
    <strong>Latest articles</strong>
    <span class="blogs-count">{{ blogs|length }} article{{ blogs|length|pluralize }}</span>
  </div>
  <div class="blogs-list">
    {% for b in blogs %}
      <article class="blog-card">
        <div class="blog-banner-wrap">
          {% if b.banner %}
            <img class="blog-banner" src="{{ b.banner.url }}" alt="{{ b.title }}" loading="lazy">
          {% else %}
            <div class="blog-banner-placeholder">JOBZILA INSIGHTS</div>
          {% endif %}
        </div>
        <div class="blog-card-content">
          <div class="blog-card-top">
            <span class="blog-topic">Career Insights</span>
            <time class="blog-date" datetime="{{ b.date|date:'Y-m-d' }}">{{ b.date|date:"M d, Y" }}</time>
          </div>
          <h2><a href="{% url 'blogs:blog_detail' b.id %}">{{ b.title }}</a></h2>
          <p class="blog-description">{{ b.body|truncatewords:30 }}</p>
          <div class="blog-card-footer">
            <span class="blog-author">By {{ b.author_display_name }} · {{ b.author }}</span>
            <a class="read-blog-link" href="{% url 'blogs:blog_detail' b.id %}">Read article →</a>
            {% if user.is_authenticated and b.posted_by_id == user.id %}
              <div class="blog-management-actions">
                <a href="{% url 'blogs:edit_blog' b.id %}">Edit</a>
                <a href="{% url 'blogs:delete_blog' b.id %}">Delete</a>
              </div>
            {% endif %}
          </div>
        </div>
      </article>
    {% empty %}
      <div class="no-blog-results"><h2>No articles yet</h2><p>Check back for career advice and resources.</p></div>
    {% endfor %}
  </div>
</section>
{% endblock main %}
```

We retained the user's attached blog-card design. The key changes are: internal detail links use `{% url 'blogs:blog_detail' b.id %}` instead of the legacy `b.link`; the byline shows the account's display name and editorial team; and owner-only Edit/Delete links are included.

## Step 10 — Add Blog template


**File: `blogs/templates/blogs/add_blog.html`**

```html
{% extends 'sharedpage.html' %}
{% block title %}Add Blog | JobZila{% endblock title %}
{% block main %}
<section class="blog-form-section"><div class="blog-form-card">
<h2>Add New Blog</h2>
<form method="post" enctype="multipart/form-data" class="blog-form">
{% csrf_token %}
{{ form.as_p }}
<div class="blog-form-buttons"><button type="submit">Publish Blog</button><a href="{% url 'blogs:blogs' %}">Cancel</a></div>
</form></div></section>
{% endblock main %}
```

`enctype="multipart/form-data"` is essential for banner uploads. The CSRF token protects the form submission.

## Step 11 — Detail template


**File: `blogs/templates/blogs/blog_detail.html`**

```html
{% extends 'sharedpage.html' %}
{% block title %}{{ post.title }} | JobZila{% endblock title %}
{% block main %}
<section class="blog-form-section"><article class="blog-form-card">
<h1>{{ post.title }}</h1>
<p>By {{ post.author_display_name }} · {{ post.author }} · {{ post.date|date:'M d, Y' }}</p>
{% if post.banner %}<img class="blog-banner" src="{{ post.banner.url }}" alt="{{ post.title }}">{% endif %}
<div class="blog-body">{{ post.body|linebreaks }}</div>
{% if user.is_authenticated and post.posted_by_id == user.id %}
<div class="blog-management-actions"><a href="{% url 'blogs:edit_blog' post.id %}">Edit</a> <a href="{% url 'blogs:delete_blog' post.id %}">Delete</a></div>
{% endif %}
<p><a href="{% url 'blogs:blogs' %}">Back to Blogs</a></p>
</article></section>
{% endblock main %}
```

The full body uses Django's `linebreaks` filter, which escapes HTML by default. Do not mark arbitrary user-supplied HTML as safe.

## Step 12 — Edit template


**File: `blogs/templates/blogs/edit_blog.html`**

```html
{% extends 'sharedpage.html' %}
{% block title %}Edit Blog | JobZila{% endblock title %}
{% block main %}
<section class="blog-form-section"><div class="blog-form-card">
<h2>Edit {{ post.title }}</h2>
<form method="post" enctype="multipart/form-data" class="blog-form">
{% csrf_token %}
{{ form.as_p }}
<div class="blog-form-buttons"><button type="submit">Update Blog</button><a href="{% url 'blogs:blog_detail' post.id %}">Cancel</a></div>
</form></div></section>
{% endblock main %}
```

This is the same ModelForm pattern as the Job Edit screen, but it includes `request.FILES` to support replacement banners.

## Step 13 — Delete confirmation template


**File: `blogs/templates/blogs/delete_blog.html`**

```html
{% extends 'sharedpage.html' %}
{% block title %}Delete Blog | JobZila{% endblock title %}
{% block main %}
<section class="blog-form-section"><div class="blog-form-card">
<h2>Delete Blog</h2><p>Are you sure you want to permanently delete <strong>{{ post.title }}</strong>?</p>
<form method="post" class="blog-form">{% csrf_token %}
<div class="blog-form-buttons"><button class="delete-blog-button" type="submit">Yes, Delete Blog</button><a href="{% url 'blogs:blog_detail' post.id %}">Cancel</a></div>
</form></div></section>
{% endblock main %}
```

Deleting the database row does **not** automatically delete its uploaded banner from storage. That can be handled later with an explicit file-lifecycle policy; do not blindly delete shared files.

## Step 14 — Append CSS to your existing stylesheet


**File: `blogs/blog_crud.css`**

```css
/* Append to your existing static/css/styles.css */
.blog-form-section { display:flex; justify-content:center; padding:40px 20px; }
.blog-form-card { width:100%; max-width:800px; background:white; border:1px solid #ddd; border-top:5px solid #ff8500; border-radius:5px; padding:25px; }
.blog-form p { margin:0 0 18px; }
.blog-form label { display:block; font-weight:700; margin-bottom:6px; }
.blog-form input, .blog-form textarea { box-sizing:border-box; width:100%; padding:10px; border:1px solid #ccc; border-radius:4px; font:inherit; }
.blog-form input[type=file] { padding:8px; }
.blog-form-buttons, .blog-management-actions { display:flex; align-items:center; gap:14px; margin-top:20px; }
.blog-form button { padding:10px 18px; border:0; border-radius:3px; color:white; background:#333; cursor:pointer; }
.blog-form button:hover { background:#ff8500; }
.blog-form .delete-blog-button { background:#b42318; }
.blog-management-actions a { color:#d96f00; font-weight:bold; }
.blog-body { line-height:1.7; overflow-wrap:anywhere; }
@media(max-width:700px) { .blog-form-buttons { flex-direction:column; align-items:stretch; } }
```

Append these rules to `static/css/styles.css` (or the stylesheet already loaded by `sharedpage.html`). They complement rather than replace your existing Insights card styling.

## Step 15 — Update the shared navigation

Inside the existing authenticated-user navigation block in `sharedpage.html`, use:

```django
{% if user.is_authenticated %}
  <li><a href="{% url 'blogs:add_blog' %}">Add Blog</a></li>
  <li><a href="{% url 'jobs:add_job' %}">Add Job</a></li>
{% endif %}
```

Do not duplicate the authenticated-user block if one already exists.

## Step 16 — Media configuration

In `settings.py` (if not already present):

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

In the **project-level** `urls.py` (development only):

```python
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

This is not a production media-serving configuration.

## Step 17 — Verify full CRUD and permissions

```powershell
py manage.py check
py manage.py runserver
```

| Action | Test URL | Expected |
|---|---|---|
| List | `/blogs/` | 100 seeded articles and both byline fields |
| Detail | `/blogs/1/` | Full article and banner if supplied |
| Create | `/blogs/add/` | Login required; save assigns `posted_by_id` |
| Edit | `/blogs/1/edit/` | Only the article owner can update |
| Delete GET | `/blogs/1/delete/` | Confirmation, no deletion yet |
| Delete POST | `/blogs/1/delete/` | Owner's CSRF-protected POST removes row |
| Unauthorized edit | Open another user's article | HTTP 403 |
| Unauthorized delete | Open another user's article | HTTP 403 |

The ID `1` is illustrative: use an ID returned by your seed query.

### SQL inspection in SQLite Browser / VS Code

```sql
SELECT b.id, b.title, b.posted_by_id,
       u.username, b.author AS editorial_team
FROM blogs_blog AS b
JOIN auth_user AS u ON u.id = b.posted_by_id
ORDER BY b.id
LIMIT 20;
```

`auth_user` is the default Django User table; a custom user model may use a different table. This query demonstrates why `posted_by_id` is a real foreign key and `author` is merely the editorial display string.

## Troubleshooting and safety notes

- **`no such table: blogs_blog`**: the rebuild migration did not apply successfully; inspect `showmigrations blogs` and `migrate --plan`.
- **`no such column: posted_by_id`**: your schema and model disagree; do not fake migrations, inspect the actual schema.
- **Missing users**: create `sadeed`, `hazla`, `frank`, and `sara` before seeding.
- **`NoReverseMatch`**: verify `blogs/urls.py` has `app_name='blogs'` and the exact route names.
- **No images**: the simplified seed deliberately leaves banners empty; manual uploads require Pillow and media configuration.
- **403 on Edit/Delete**: the account must match `posted_by_id`; signing in as a different user is insufficient.
- **Old links**: seeded `link` values are blank; all internal navigation should use Django URL tags. Keep the field for compatibility until a separate schema cleanup.
- **Do not use `reset_seed_blogs`** from Module 05C after migrating to this schema unless you adapt and review its code.

## Final learning outcomes

Students should be able to explain Django migrations versus raw SQL, foreign keys and User IDs, the distinction between ownership and editorial bylines, ModelForms, multipart uploads, GET vs POST, CSRF, 403 permission checks, and reusable CRUD templates.

**Scope:** These files are built from the supplied lesson guides and attached listing template. They are syntax-checked but have not been run against your actual project database. Review the migration dependencies and any cross-table relationships before applying the destructive rebuild.

