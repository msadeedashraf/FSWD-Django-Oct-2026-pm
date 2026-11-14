"""Django command: python manage.py reseed_blog_data --count 100

Place at blogs/management/commands/reseed_blog_data.py.
Requires Pillow: python -m pip install Pillow
"""
import io
import random
import re
from datetime import timedelta
from urllib.request import Request, urlopen

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from blogs.models import Blog

# Fixed photo URLs; unlike source.unsplash.com random redirects, these are reproducible.
# Image downloads are best-effort: a locally generated topic-labelled JPEG is used on failure.
PHOTO_IDS = {
    "career": "photo-1521737711867-e3b97375f902",
    "resume": "photo-1586281380349-632531db7ed4",
    "interview": "photo-1573496359142-b8d87734a5a2",
    "python": "photo-1515879218367-8466d910aaa4",
    "sql": "photo-1544383835-bda2bc66a55d",
    "cloud": "photo-1451187580459-43490279c0fa",
    "analytics": "photo-1551288049-bebda4e38f71",
    "ai": "photo-1677442136019-21780ecad995",
    "network": "photo-1558494949-ef010cbdcc31",
    "growth": "photo-1460925895917-afdab827c52f",
}

BYLINES = {
    "sadeed": "JobZila Editorial Team",
    "hazla": "Career Research Desk",
    "frank": "Technology Learning Team",
    "sara": "JobZila Editorial Team",
}

TOPICS = {
    "career": ["Planning Your Next Career Move", "How to Change Careers Confidently", "Building a Career Roadmap"],
    "resume": ["Writing a Resume That Gets Noticed", "Common Resume Mistakes to Avoid", "Tailoring Your Resume to a Job"],
    "interview": ["Preparing for Your Next Interview", "Answering Behavioral Interview Questions", "Following Up After an Interview"],
    "python": ["Learning Python for Your Career", "Python Projects for Beginners", "Building Practical Python Skills"],
    "sql": ["SQL Skills Employers Look For", "Practicing SQL with Real Data", "Getting Started with Database Queries"],
    "cloud": ["Getting Started with Cloud Computing", "Cloud Skills for Entry-Level Roles", "Understanding Cloud Career Paths"],
    "analytics": ["Building a Data Analytics Portfolio", "Data Analysis Skills to Practice", "Presenting Data Insights Clearly"],
    "ai": ["Understanding AI in the Workplace", "Building Practical AI Skills", "Preparing for AI-Related Roles"],
    "network": ["Fundamentals of Computer Networking", "Networking Skills for IT Careers", "Understanding Modern IT Infrastructure"],
    "growth": ["Setting Professional Growth Goals", "Building Better Learning Habits", "Developing Workplace Communication Skills"],
}

KEYWORDS = {
    "resume": ("resume", "cv", "cover letter"),
    "interview": ("interview", "recruiter"),
    "python": ("python", "django", "programming"),
    "sql": ("sql", "database", "query"),
    "cloud": ("cloud", "azure", "aws"),
    "analytics": ("analytic", "data", "dashboard", "power bi"),
    "ai": ("artificial intelligence", "machine learning", " ai ", "chatgpt"),
    "network": ("network", "infrastructure", "cybersecurity"),
    "growth": ("growth", "learning", "communication", "leadership"),
    "career": ("career", "job", "work"),
}


def topic_for(title, fallback="career"):
    text = f" {title.lower()} "
    for topic, words in KEYWORDS.items():
        if any(word in text for word in words):
            return topic
    return fallback


def jpeg_bytes(raw):
    with Image.open(io.BytesIO(raw)) as im:
        im = im.convert("RGB")
        im.thumbnail((1200, 675))
        canvas = Image.new("RGB", (1200, 675), "#e8edf4")
        canvas.paste(im, ((1200 - im.width) // 2, (675 - im.height) // 2))
        out = io.BytesIO()
        canvas.save(out, "JPEG", quality=87, optimize=True)
        return out.getvalue()


def fallback_jpeg(topic):
    im = Image.new("RGB", (1200, 675), (30, 48, 74))
    draw = ImageDraw.Draw(im)
    draw.rectangle((50, 55, 1150, 620), outline=(110, 155, 204), width=5)
    draw.text((100, 260), "JOBZILA INSIGHTS", fill="white")
    draw.text((100, 330), topic.upper(), fill=(125, 210, 250))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=90)
    return out.getvalue()


class Command(BaseCommand):
    help = "Download 10 topic JPEGs, seed/repair blogs, and verify all banner files."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--refresh-images", action="store_true", help="Replace existing 10 JPEG files")
        parser.add_argument("--no-download", action="store_true", help="Use locally generated JPEGs for missing/refresh images")
        parser.add_argument("--replace", action="store_true", help="Delete existing blogs before seeding")
        parser.add_argument("--confirm", action="store_true", help="Required with --replace")

    def handle(self, *args, **opts):
        count = opts["count"]
        if count < 1:
            raise CommandError("--count must be at least 1")
        if opts["replace"] and not opts["confirm"]:
            raise CommandError("--replace deletes existing blogs; add --confirm if intended")

        users = list(get_user_model().objects.filter(username__in=BYLINES).order_by("username"))
        if not users:
            raise CommandError("Create at least one Django user: sadeed, hazla, frank, or sara")

        storage = Blog._meta.get_field("banner").storage
        banner_paths = {}
        for topic, photo_id in PHOTO_IDS.items():
            path = f"blog_banners/{topic}.jpg"
            if opts["refresh_images"] or not storage.exists(path):
                data = None
                if not opts["no_download"]:
                    url = f"https://images.unsplash.com/{photo_id}?w=1200&h=675&fit=crop&auto=format"
                    try:
                        request = Request(url, headers={"User-Agent": "Mozilla/5.0 (JobZila demo seeder)"})
                        with urlopen(request, timeout=12) as response:
                            raw = response.read(8 * 1024 * 1024 + 1)
                        if len(raw) > 8 * 1024 * 1024:
                            raise ValueError("image exceeds 8 MB")
                        data = jpeg_bytes(raw)
                        label = "Downloaded"
                    except (OSError, ValueError, UnidentifiedImageError) as exc:
                        self.stderr.write(f"Photo unavailable for {topic}: {exc}")
                if data is None:
                    data = fallback_jpeg(topic)
                    label = "Generated fallback"
                # Storage.save() can rename on collision, so explicitly delete first.
                if storage.exists(path):
                    storage.delete(path)
                actual_path = storage.save(path, ContentFile(data))
                if actual_path != path:
                    raise CommandError(f"Storage renamed {path} to {actual_path}; check storage configuration")
                self.stdout.write(f"{label}: {path}")
            else:
                self.stdout.write(f"Reusing: {path}")
            # Check the stored bytes can actually be opened as an image.
            try:
                with storage.open(path, "rb") as handle:
                    with Image.open(handle) as image:
                        image.verify()
            except (OSError, ValueError, UnidentifiedImageError) as exc:
                raise CommandError(f"Invalid image at {path}: {exc}") from exc
            banner_paths[topic] = path

        with transaction.atomic():
            if opts["replace"]:
                Blog.objects.all().delete()

            existing = list(Blog.objects.order_by("pk"))
            # Repair all existing blog records; match banners to title topics.
            for index, blog in enumerate(existing):
                topic = topic_for(blog.title, list(PHOTO_IDS)[index % len(PHOTO_IDS)])
                blog.banner = banner_paths[topic]
            if existing:
                Blog.objects.bulk_update(existing, ["banner"])

            # Create enough new records to reach --count, without deleting existing ones.
            to_create = max(0, count - len(existing))
            for index in range(to_create):
                number = len(existing) + index
                topic = list(TOPICS)[number % len(TOPICS)]
                title_base = TOPICS[topic][(number // len(TOPICS)) % len(TOPICS[topic])]
                title = f"{title_base} — Guide {number + 1}"
                slug_base = slugify(title)[:42] or "jobzila-article"
                slug = slug_base
                suffix = 2
                while Blog.objects.filter(slug=slug).exists():
                    slug = f"{slug_base}-{suffix}"
                    suffix += 1
                user = users[number % len(users)]
                body = (
                    f"{title_base}. This practical guide introduces the main ideas, "
                    "explains common mistakes, and suggests exercises you can use "
                    "to strengthen your skills and prepare for your next opportunity. "
                    "Start with one achievable goal, practice consistently, "
                    "and review your progress each week."
                )
                Blog.objects.create(
                    title=title,
                    body=body,
                    slug=slug,
                    link="",  # Local detail URLs can be built in the view/template.
                    date=timezone.now() - timedelta(days=number % 180),
                    author=BYLINES[user.username],
                    posted_by=user,
                    banner=banner_paths[topic],
                )

        missing = [
            (blog.pk, blog.banner.name)
            for blog in Blog.objects.all()
            if not blog.banner or not blog.banner.storage.exists(blog.banner.name)
        ]
        if missing:
            raise CommandError(f"Missing banner files for blog IDs: {missing[:20]}")
        self.stdout.write(self.style.SUCCESS(
            f"Success: {Blog.objects.count()} blogs; all banner paths point to existing files."
        ))
