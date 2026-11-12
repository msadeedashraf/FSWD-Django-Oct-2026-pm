# JobZila — Blog author ownership and editorial mapping (Module 13 extension)

This package extends the Blog CRUD from Module 13. It is based on your uploaded `blogs.html` and the previously supplied Module 05/05C/13 guides. **The actual original `reset_seed_blogs.py` source was not provided**, so `seed_blog_data.py` is a new, non-destructive replacement with demonstration text; it does not reproduce the old 100 articles or download stock images.

## Step 1 — Back up first

Back up `db.sqlite3` and your `media/` directory. Do **not** run the old `reset_seed_blogs` command: it deletes every blog row.

## Step 2 — Confirm the four users exist

Use Django admin (`/admin/`) or `python manage.py createsuperuser` to create real accounts with usernames `sadeed`, `hazla`, `frank`, `sara`. **Do not create shared/default passwords in scripts.** The scripts stop with an error if an account is missing.

## Step 3 — Copy files into your existing Django app

- `blogs/author_mapping.py` — centralized mapping
- `blogs/models.py` — example complete Blog model, preserving existing fields and `posted_by` from Module 13; `author` is the editorial byline, and `author_display_name` is a read-only property.
- `blogs/management/commands/assign_blog_authors.py` — assign real owners to existing articles without deleting anything
- `blogs/management/commands/seed_blog_data.py` — create additional demo articles without overwriting old ones
- `blogs/templates/blogs/blogs.html` — your attached page with both names and real detail URLs

Make sure both `blogs/management/__init__.py` and `blogs/management/commands/__init__.py` exist (empty is fine). If you have customized `models.py`, merge changes rather than overwriting your customizations.

## Step 4 — Migrate the model

```powershell
py manage.py makemigrations blogs
py manage.py migrate
```

If Module 13 has already added `posted_by`, this may only migrate `banner` to `blank=True` (allowing image-free demo posts). `blank=True` affects form validation, not the database storage type. Existing images remain untouched.

## Step 5 — Safely assign existing seeded blogs to users

```powershell
py manage.py assign_blog_authors --dry-run
py manage.py assign_blog_authors
```

The command processes existing blog records in primary-key order, cycling through `sadeed`, `hazla`, `frank`, `sara`. It updates **only** `posted_by` and `author`. It does **not** change titles, bodies, slugs, links, dates, images, or delete rows.

**Important:** Blogs that already have a `posted_by` owner are **skipped** by default. To deliberately reassign those too, run `py manage.py assign_blog_authors --dry-run --overwrite`, review the count, then `py manage.py assign_blog_authors --overwrite`. This changes who can edit/delete those posts. Don't do it without permission from the current owners.

## Step 6 — Create new demo blog records (optional)

```powershell
py manage.py seed_blog_data --count 100 --dry-run
py manage.py seed_blog_data --count 100
```

This creates up to 100 **additional** example posts, each assigned to a real user and the corresponding editorial byline. Re-running it skips existing demo slugs. New posts have **no banner image** and use the placeholder already present in your template. Previously seeded posts retain their existing banner images. To keep only your current 100 seeded posts and their pictures, **skip this step** and run Step 5 instead.

## Step 7 — Keep the mapping in new CRUD posts

In `blogs/views.py`, import the helper:

```python
from .author_mapping import editorial_team_for
```

Inside `add_blog`, after `post.posted_by = request.user`, replace the old `post.author = request.user.get_full_name()...` line with:

```python
post.author = editorial_team_for(request.user)
```

In `edit_blog`, retain the existing `posted_by` ownership check. The editorial byline is intentionally **not** a user-editable ModelForm field. If a user changes teams, decide whether old articles should retain their historical byline; the script above updates only when explicitly invoked.

In `blog_detail.html`, change any `{{ post.author }}` byline to:

```django
By {{ post.author_display_name }}{% if post.author %} · {{ post.author }}{% endif %}
```

In `blogs/views.py`, optionally improve the listing query:

```python
def blog(request):
    blogs = Blog.objects.select_related("posted_by").order_by("-date")
    return render(request, "blogs/blogs.html", {"blogs": blogs})
```

## Step 8 — Verify

```powershell
py manage.py shell -c "from blogs.models import Blog; print([(b.id,b.posted_by.username if b.posted_by else None,b.author,b.banner.name) for b in Blog.objects.select_related('posted_by')[:12]])"
py manage.py check
py manage.py runserver
```

Open `http://127.0.0.1:8000/blogs/`. You should see `By Sadeed · JobZila Editorial Team` (or the other mapped accounts), and only the current owner should see Edit/Delete. Test that a different logged-in user gets HTTP 403 on another author's edit/delete URL.

## Why the model uses two fields instead of a second editorial-team table

The `posted_by` ForeignKey is the security principal; `author` remains the editorial team text for historical articles. `author_display_name` is derived from the related Django user, so no duplicate username field is needed. `author_mapping.py` is the single source of truth for newly created posts and the management scripts. If teams later become dynamic/admin-managed, introduce a separate EditorialTeam model then.

## Caution about link URLs

The updated template uses `{% url 'blogs:blog_detail' b.id %}` rather than `{{ b.link }}`. This fixes the old seed data's `link` values that point to `/blogs/` instead of the individual article. The new seed command still populates `link` to satisfy the legacy required URLField; don't rely on it for internal navigation. The demo script uses a localhost URL only as a legacy placeholder.
