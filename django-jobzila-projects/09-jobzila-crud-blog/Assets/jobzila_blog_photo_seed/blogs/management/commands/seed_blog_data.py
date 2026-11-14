"""Download 10 photographic JPEG banners and seed Blog rows with valid image paths.

Requires Pillow. Back up SQLite and media before --replace.
"""
from datetime import timedelta
from io import BytesIO
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw

from blogs.models import Blog

# Public Unsplash image endpoints; photos can change/disappear. Verify before production use.
# These are deliberately named by topic, not claimed to be the original Module 05C photos.
TOPICS = [
    ("career", "Career Planning", "Build a realistic career plan", "photo-1497366811353-6870744d04b2"),
    ("resume", "Resume Writing", "Improve your resume for recruiters", "photo-1455390582262-044cdead277a"),
    ("interview", "Interview Preparation", "Prepare for your next interview", "photo-1521737711867-e3b97375f902"),
    ("python", "Python Skills", "Learn practical Python for work", "photo-1515879218367-8466d910aaa4"),
    ("sql", "SQL Skills", "Use SQL to solve business problems", "photo-1551288049-bebda4e38f71"),
    ("cloud", "Cloud Computing", "Understand cloud career pathways", "photo-1451187580459-43490279c0fa"),
    ("analytics", "Data Analytics", "Develop a data analytics portfolio", "photo-1460925895917-afdab827c52f"),
    ("ai", "Artificial Intelligence", "Explore AI skills for modern jobs", "photo-1677442136019-21780ecad995"),
    ("network", "Networking", "Build a professional network", "photo-1528605248644-14dd04022da1"),
    ("growth", "Career Growth", "Plan your next professional milestone", "photo-1486406146926-c627a92ad1ab"),
]

# Username -> editorial byline; no additional DB mapping table.
EDITORIAL_BY_USERNAME = {
    "sadeed": "JobZila Editorial Team",
    "hazla": "Career Research Desk",
    "frank": "Technology Learning Team",
    "sara": "JobZila Editorial Team",
}


def normalize_jpeg(raw):
    """Reject invalid images, normalize valid ones to 1200x630 JPEG."""
    with Image.open(BytesIO(raw)) as im:
        im.load()
        if im.width < 200 or im.height < 150:
            raise ValueError("Image resolution too small")
        im = im.convert("RGB")
        # Center crop, preserving aspect ratio.
        target_ratio = 1200 / 630
        w, h = im.size
        if w / h > target_ratio:
            nw = round(h * target_ratio)
            im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = round(w / target_ratio)
            im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
        im = im.resize((1200, 630), Image.Resampling.LANCZOS)
        out = BytesIO()
        im.save(out, "JPEG", quality=88, optimize=True)
        return out.getvalue()


def fallback_jpeg(topic):
    im = Image.new("RGB", (1200, 630), (29, 47, 69))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 25, 630), fill=(255, 133, 0))
    d.text((90, 180), "JOBZILA INSIGHTS", fill=(255, 133, 0))
    d.text((90, 290), topic, fill="white")
    out = BytesIO()
    im.save(out, "JPEG", quality=90)
    return out.getvalue()


class Command(BaseCommand):
    help = "Download 10 photos into media/blog_banners and seed blogs with user ownership."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--replace", action="store_true")
        parser.add_argument("--confirm", action="store_true")
        parser.add_argument("--refresh-images", action="store_true", help="Replace the 10 named image files")
        parser.add_argument("--no-download", action="store_true", help="Use locally generated fallback JPEGs")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        count = opts["count"]
        if not 1 <= count <= 1000:
            raise CommandError("--count must be 1..1000")
        if opts["replace"] and not opts["confirm"]:
            raise CommandError("--replace requires --confirm; back up your DB first")
        if not settings.MEDIA_ROOT:
            raise CommandError("Set MEDIA_ROOT in settings.py")
        User = get_user_model()
        users = {}
        for name in EDITORIAL_BY_USERNAME:
            try:
                users[name] = User.objects.get(username=name)
            except User.DoesNotExist:
                raise CommandError(f"Create Django user '{name}' before seeding")
        if opts["dry_run"]:
            self.stdout.write(f"Would prepare 10 JPEGs and {'replace' if opts['replace'] else 'add'} {count} blog records")
            return

        storage = Blog._meta.get_field("banner").storage
        paths = {}
        for key, topic, _heading, photo_id in TOPICS:
            path = f"blog_banners/{key}.jpg"
            # Replace explicitly to correct stale/wrong images from previous scripts.
            if opts["refresh_images"] and storage.exists(path):
                storage.delete(path)
            if not storage.exists(path):
                raw = None
                if not opts["no_download"]:
                    url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1200&h=630&q=85"
                    try:
                        req = Request(url, headers={"User-Agent": "JobZilaDemoSeeder/1.0"})
                        with urlopen(req, timeout=15) as response:
                            if int(response.headers.get("Content-Length", "0")) > 12_000_000:
                                raise ValueError("Image too large")
                            raw = response.read(12_000_001)
                            if len(raw) > 12_000_000:
                                raise ValueError("Image too large")
                        raw = normalize_jpeg(raw)
                        self.stdout.write(f"Downloaded: {path}")
                    except Exception as exc:
                        self.stderr.write(f"Download failed for {topic}: {exc}; generating fallback")
                if raw is None:
                    raw = fallback_jpeg(topic)
                actual = storage.save(path, ContentFile(raw))
                if actual != path:
                    raise CommandError(f"Unexpected storage filename {actual}; expected {path}")
            # Existing files must be valid; don't silently link to corrupt files.
            try:
                with storage.open(path, "rb") as f:
                    with Image.open(f) as im:
                        im.verify()
            except Exception as exc:
                raise CommandError(f"Invalid banner {path}: {exc}. Retry with --refresh-images")
            paths[key] = path

        names = list(EDITORIAL_BY_USERNAME)
        created = 0
        with transaction.atomic():
            if opts["replace"]:
                Blog.objects.all().delete()
            for i in range(count):
                key, topic, heading, _photo_id = TOPICS[i % len(TOPICS)]
                slug = f"{key}-{i+1:04d}"
                if Blog.objects.filter(slug=slug).exists():
                    continue
                username = names[i % len(names)]
                Blog.objects.create(
                    title=f"{heading}: Guide {i+1}",
                    body=(f"{topic}: Set a clear goal, practice useful skills, "
                          "build a project, document outcomes, and seek feedback.\n\n"
                          "This is sample content for classroom use."),
                    slug=slug,
                    link="",
                    date=timezone.now() - timedelta(days=i),
                    author=EDITORIAL_BY_USERNAME[username],
                    posted_by=users[username],
                    banner=paths[key],
                )
                created += 1
        missing = [b.pk for b in Blog.objects.all() if not b.banner or not storage.exists(b.banner.name)]
        if missing:
            raise CommandError(f"Missing banner files for blog IDs: {missing[:20]}")
        self.stdout.write(self.style.SUCCESS(f"Created {created} blogs; verified all current banner paths"))
