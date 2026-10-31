# Module 05B — Add Real Stock Photos to JobZila Blog Posts

This updates the **existing blog records** created by `seed_blogs.py`. It does not create more posts or change the Blog model.

## 1. Save the management command

Copy `seed_blog_stock_images.py` into:

```text
blogs/management/commands/seed_blog_stock_images.py
```

Ensure both `management/` and `commands/` contain `__init__.py`.

## 2. Install Pillow

From the folder containing `manage.py`:

```powershell
python -m pip install Pillow
```

## 3. Seed blogs (only if not already seeded)

```powershell
python manage.py seed_blogs --count 100
```

## 4. Download stock photos and update the database

```powershell
python manage.py seed_blog_stock_images --count 100
```

This command requires an internet connection. It downloads real Unsplash photos, saves copies through Django's `ImageField`, and assigns them to your existing 100 blog posts. Ten stock image sources are reused across posts. Failed downloads are skipped; if none succeed, the command exits with an error.

## 5. Verify media settings

In `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

In your **project** `urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 6. View the result

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/blogs/` and refresh the page.

## Photo usage

Images are sourced from Unsplash and governed by its license: https://unsplash.com/license. Attribution is appreciated. This is a classroom demo; do not present fictional posts as genuine articles. The photos are downloaded when you run the command, not bundled in the script.
