"""Replace generated blog banners with real free-to-use Unsplash photos.

Place in blogs/management/commands/seed_blog_stock_images.py
Run: python manage.py seed_blog_stock_images
Requires: Pillow (python -m pip install Pillow)

Downloads 10 photos once, stores them in MEDIA_ROOT via Django ImageField,
and cycles through the photos for existing seeded blog posts.
"""
from io import BytesIO
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image
from blogs.models import Blog

# Specific Unsplash image IDs; no API key or random endpoint needed.
# Source/license: https://unsplash.com/license
PHOTOS = [
    ("coding", "photo-1498050108023-c5249f4df085"),
    ("office", "photo-1497366811353-6870744d04b2"),
    ("teamwork", "photo-1521737711867-e3b97375f902"),
    ("laptop", "photo-1516321318423-f06f85e504b3"),
    ("workspace", "photo-1497366754035-f200968a6e72"),
    ("interview", "photo-1573496359142-b8d87734a5a2"),
    ("analytics", "photo-1551288049-bebda4e38f71"),
    ("learning", "photo-1516321318423-f06f85e504b3"),
    ("meeting", "photo-1556761175-b413da4baf72"),
    ("technology", "photo-1518770660439-4636190af475"),
]


def fetch_photo(photo_id):
    url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1200&h=630&q=78"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (JobZila classroom seed)"})
    with urlopen(request, timeout=25) as response:
        data = response.read(6_000_001)
    if len(data) > 6_000_000:
        raise ValueError("Image exceeds 6 MB")
    img = Image.open(BytesIO(data)).convert("RGB")
    img.thumbnail((1200, 630))
    out = BytesIO()
    img.save(out, "JPEG", quality=82, optimize=True)
    return out.getvalue()


class Command(BaseCommand):
    help = "Download stock photos and assign them to existing seeded Blog records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)

    def handle(self, *args, **options):
        blogs = list(Blog.objects.order_by("id")[:options["count"]])
        if not blogs:
            raise CommandError("No blog posts found. Run seed_blogs first.")
        downloaded = []
        for label, photo_id in PHOTOS:
            try:
                data = fetch_photo(photo_id)
                downloaded.append((label, data))
                self.stdout.write(f"Downloaded {label}")
            except (HTTPError, URLError, OSError, ValueError) as exc:
                self.stderr.write(f"Skipped {label}: {exc}")
        if not downloaded:
            raise CommandError("Could not download any stock photos. Check internet access and retry.")
        for i, blog in enumerate(blogs):
            label, data = downloaded[i % len(downloaded)]
            # Reuse the saved media filename on repeated runs, not a new random file.
            filename = f"stock-blog-{blog.pk}-{label}.jpg"
            if blog.banner and blog.banner.name.startswith("blog_banners/stock-blog-"):
                blog.banner.delete(save=False)
            blog.banner.save(filename, ContentFile(data), save=True)
        self.stdout.write(self.style.SUCCESS(
            f"Assigned real stock photographs to {len(blogs)} blog posts using {len(downloaded)} source photos."
        ))
        self.stdout.write("Unsplash license: https://unsplash.com/license")
