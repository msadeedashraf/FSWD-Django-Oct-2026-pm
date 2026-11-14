# JobZila Module 13 — Restore banner images in seed data

This replacement `seed_blog_data.py` creates ten reusable **offline JPEG** files and stores their relative paths in the `Blog.banner` ImageField. It assigns `posted_by` to the existing Django users (`sadeed`, `hazla`, `frank`, `sara`) and preserves the mapped `author` editorial byline. It does **not** drop or recreate the database table.

**Important:** The exact filenames from the original Module 05C seed *source code* were not supplied. The original guide documents ten reusable topic images but not their filenames. This script uses deterministic filenames: `career.jpg`, `resume.jpg`, `interview.jpg`, `python.jpg`, `sql.jpg`, `cloud.jpg`, `analytics.jpg`, `ai.jpg`, `network.jpg`, `growth.jpg` under `media/blog_banners/`. It reuses those files if they exist, without overwriting them. To match an earlier custom naming scheme, change `filename = f"blog_banners/{key}.jpg"`.

## Installation

1. Back up `db.sqlite3` and `media/`.
2. Install Pillow: `py -m pip install Pillow`.
3. Copy the command to `blogs/management/commands/seed_blog_data.py` (keep `__init__.py` in both management directories). Copy `author_mapping.py` to `blogs/` if missing.
4. Confirm `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'` in settings, and local DEBUG media serving in the project URLs.
5. Ensure your Blog model has `posted_by`, `author`, `banner` and other original fields, and migrations are applied. Confirm the four user accounts exist.
6. Preview: `py manage.py seed_blog_data --count 100 --dry-run`.
7. If existing 100 posts were seeded without images and you want to replace them: `py manage.py seed_blog_data --count 100 --replace --confirm`. This **deletes all existing Blog rows**, including any manually created posts. Alternatively, run without `--replace` to add missing demo slugs; existing rows are skipped and won't get banners retroactively.
8. Verify: `py manage.py shell -c "from blogs.models import Blog; print(Blog.objects.count()); print(list(Blog.objects.values_list('posted_by__username','author','banner')[:5]))"`.

Your blog template should use `{% if b.banner %}<img src="{{ b.banner.url }}" alt="{{ b.title }}">{% endif %}` and detail links should use `{% url 'blogs:blog_detail' b.id %}`. No `--no-download` option is necessary: all images are generated locally.

**Note:** Filesystem writes are not rolled back if a database transaction fails. Existing named images are left unchanged, and unused images can be cleaned up separately after checking references.
