# Module 05A — Populate JobZila Blogs with Sample Data

This exercise adds up to **100 fictional blog posts** to the existing SQLite database using a Django management command. No model changes or new migrations are required.

## 1. Install Pillow

From the directory containing `manage.py`, with your virtual environment activated:

```powershell
python -m pip install Pillow
```

## 2. Create the command folders

Inside the existing `blogs` app, create the following structure. Both `__init__.py` files can be empty.

```text
blogs/
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── seed_blogs.py
```

Copy the supplied `seed_blogs.py` into `blogs/management/commands/`.

## 3. Confirm database migrations

```powershell
python manage.py migrate
```

## 4. Generate 100 sample posts

```powershell
python manage.py seed_blogs --count 100
```

The command prints how many records were created, skipped, and stored in total. It generates JPEG banner files using Pillow and saves them through Django's configured media storage.

## 5. Verify the results

```powershell
python manage.py shell
```

```python
from blogs.models import Blog
print(Blog.objects.count())
print(Blog.objects.first().title)
exit()
```

Open `http://127.0.0.1:8000/blogs/` to see the posts.

## Optional commands

```powershell
python manage.py seed_blogs --count 20
python manage.py seed_blogs --clear --count 100
```

**Caution:** `--clear` deletes **all** blog records. Use only on a disposable development database. Re-running without `--clear` skips posts whose slugs already exist.

## Important: showing the banners

In `settings.py`, ensure media storage is configured:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

In your project's main `urls.py`, add these imports and append the media route **only for local development**:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

The existing Module 05 `Blog` model has no individual blog detail view. Accordingly, seeded `link` values point to `/blogs/` until a detail route is built. Banner images are locally generated placeholders, and the article text is classroom demonstration content.
