# JobZila Blog — photographic banner seed

This replaces `blogs/management/commands/seed_blog_data.py`. It downloads **10 topic-associated Unsplash photographs** to `MEDIA_ROOT/blog_banners/`, converts them to valid 1200×630 JPEG files, and reuses them across 100 blog rows. If a download fails, it generates a visible fallback graphic and reports the failure. **These are not verified to be the exact images from the original Module 05C script** because its full source/URL list was not provided. Replace `TOPICS` photo IDs with the original IDs if exact image matching is required.

## Install

1. Back up `db.sqlite3` and the entire `media/` folder.
2. Copy `seed_blog_data.py` into `blogs/management/commands/` (keep both `__init__.py` files).
3. Install Pillow: `py -m pip install Pillow`.
4. Ensure `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'` in settings.py; enable `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` in the main URL config when `DEBUG=True`.
5. Ensure the Blog model has `posted_by` ForeignKey, `author` CharField, `banner` ImageField and your four Django users exist. Apply migrations before running the seed command.

## Commands

```powershell
py manage.py seed_blog_data --count 100 --dry-run
py manage.py seed_blog_data --count 100 --replace --confirm --refresh-images
```

`--replace` deletes existing blog rows (not jobs/users); `--refresh-images` deletes and recreates the 10 named banner files (including existing photos under those names). Both are destructive: back up first. Without `--refresh-images`, existing valid JPEGs are reused. Use `--no-download` only if you intentionally want generated offline placeholders.

## Verify

```powershell
py manage.py shell -c "from blogs.models import Blog; print('Count:',Blog.objects.count()); print([(b.posted_by.username,b.author,b.banner.name,b.banner.storage.exists(b.banner.name)) for b in Blog.objects.all()[:10]])"
```

In the template use `{% if b.banner %}<img src="{{ b.banner.url }}" alt="{{ b.title }}">{% endif %}`. The `link` column is intentionally empty; for detail links use `{% url 'blogs:blog_detail' b.id %}` (assuming this is your route name).

**Note:** Downloading external photos may require checking the image provider's usage terms before commercial deployment. This script is intended for local educational demonstrations. Image downloads and file deletions are not rolled back by database transactions.
