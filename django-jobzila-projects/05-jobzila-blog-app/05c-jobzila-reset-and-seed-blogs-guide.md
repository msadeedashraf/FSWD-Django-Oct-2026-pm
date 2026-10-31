# Module 05C — Reset and Seed JobZila Blogs (with Images)

This short guide replaces the earlier two-step blog seeding workflow with **one Django management command**: `reset_seed_blogs.py`.

> **Warning:** This command permanently deletes **all records in the `Blog` table** before creating new demo posts. It does **not** delete Jobs records. Use it only with a disposable development database. Back up `db.sqlite3` first if needed.

## Step 1 — Install Pillow

Open a terminal in the Django project directory (the one containing `manage.py`), activate your virtual environment, and run:

```powershell
python -m pip install Pillow
```

## Step 2 — Place the command in the Blogs app

Save `reset_seed_blogs.py` in this location:

```text
blogs/
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── reset_seed_blogs.py
```

Both `__init__.py` files may be empty. The command imports your existing `blogs.models.Blog` model.

## Step 3 — Configure image storage

In your project's **settings.py**, add these settings if they are not already present:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

In the **main project `urls.py`** (not `blogs/urls.py`), add:

```python
from django.conf import settings
from django.conf.urls.static import static

# Keep all your existing urlpatterns above this block.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

This media-serving configuration is intended for local development, **not production**.

## Step 4 — Apply migrations and run the reset

```powershell
python manage.py migrate
python manage.py reset_seed_blogs --count 100 --confirm
```

The script downloads up to 10 stock images (one per topic) and reuses their image data across 100 posts. If a download fails, it creates a local JPEG fallback banner. Each blog's `banner` field is saved using Django's image storage.

**Offline option:** To use generated banners without downloading stock photographs:

```powershell
python manage.py reset_seed_blogs --count 100 --confirm --no-download
```

`--count` accepts values from **1 to 100**. `--confirm` is required because the command deletes the existing Blog records.

## Step 5 — Verify the database and files

Run this command from the same project directory:

```powershell
python manage.py shell -c "from blogs.models import Blog; print('Blogs:', Blog.objects.count()); print([(b.title, b.banner.name, b.banner.storage.exists(b.banner.name)) for b in Blog.objects.all()[:5]])"
```

Expected: `Blogs: 100` and `True` for each of the five image-existence checks. The files are saved under `MEDIA_ROOT`, typically in `media/` or a subdirectory defined by `Blog.banner`'s `upload_to` setting.

## Step 6 — Display images on the Blogs page

In `blogs/templates/blogs/blogs.html`, make sure your image uses the `ImageField` URL:

```django
{% if b.banner %}
    <img class="blog-banner" src="{{ b.banner.url }}" alt="{{ b.title }}">
{% endif %}
```

If the template uses another loop variable for the featured article, use **that article's** `.banner.url` instead.

Start Django:

```powershell
python manage.py runserver
```

Open **http://127.0.0.1:8000/blogs/** and hard-refresh with **Ctrl + Shift + R**.

## Troubleshooting

- **`Unknown command: reset_seed_blogs`** — Check the exact directory structure, spelling, and `__init__.py` files; confirm `blogs` is in `INSTALLED_APPS`.
- **`No module named PIL`** — Install Pillow in the same virtual environment running Django.
- **Database records exist but images do not appear** — Check `MEDIA_URL`, `MEDIA_ROOT`, the main URL configuration, and the template's `banner.url` reference.
- **Image existence shows `False`** — Check that `MEDIA_ROOT` points to the location where the files were saved; rerun the seed command only if you are comfortable deleting the Blog records again.
- **Stock photos unavailable** — The script uses generated fallback banners automatically; external image downloads require internet access.

**Note:** This Module 05 script sets `link` to the local `/blogs/` listing because an individual blog detail page has not yet been added. Clicking “Read More” will therefore return to the listing until a detail route is implemented.
