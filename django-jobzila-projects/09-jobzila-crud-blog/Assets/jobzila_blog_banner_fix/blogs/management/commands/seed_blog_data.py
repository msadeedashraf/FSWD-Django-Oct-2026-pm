"""Seed demo blogs with owner IDs, editorial bylines and real JPEG banners.

Run: py manage.py seed_blog_data --count 100
     py manage.py seed_blog_data --count 100 --replace --confirm

Images are saved to MEDIA_ROOT/blog_banners/<topic>.jpg using Django storage.
"""
from datetime import timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

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


def make_jpeg(title, index):
    """Generate an original offline JPEG; no external service required."""
    palettes = [
        ((22, 42, 66), (245, 139, 36)),
        ((24, 59, 66), (88, 196, 174)),
        ((56, 39, 73), (225, 151, 92)),
        ((31, 51, 82), (115, 177, 238)),
    ]
    background, accent = palettes[index % len(palettes)]
    im = Image.new("RGB", (1200, 630), background)
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 22, 630), fill=accent)
    draw.rounded_rectangle((72, 110, 1128, 520), radius=24, outline=accent, width=4)
    draw.text((100, 165), "JOBZILA INSIGHTS", fill=accent)
    # Use bundled Pillow font if available, otherwise Pillow's default.
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 54)
    except OSError:
        font = ImageFont.load_default()
    # Wrap topic words into short lines.
    words, lines, line = title.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if len(trial) > 19 and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    for row, text in enumerate(lines):
        draw.text((100, 265 + row * 75), text, font=font, fill="white")
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


class Command(BaseCommand):
    help = "Seed blogs with actual JPEG files, Django user owners and editorial bylines."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--replace", action="store_true", help="Delete existing blog rows before seeding")
        parser.add_argument("--confirm", action="store_true", help="Required with --replace")

    def handle(self, *args, **options):
        count = options["count"]
        if not 1 <= count <= 1000:
            raise CommandError("--count must be between 1 and 1000")
        if options["replace"] and not options["confirm"]:
            raise CommandError("--replace requires --confirm. Back up db.sqlite3 and media first.")
        if not settings.MEDIA_ROOT:
            raise CommandError("MEDIA_ROOT must be configured")
        if not hasattr(Blog, "posted_by"):
            raise CommandError("Blog.posted_by is missing; apply the model migration first")

        User = get_user_model()
        names = list(EDITORIAL_BY_USERNAME)
        users = {}
        for name in names:
            try:
                users[name] = User.objects.get(username__iexact=name)
            except User.DoesNotExist:
                raise CommandError(f"Missing Django user: {name}")
            except User.MultipleObjectsReturned:
                raise CommandError(f"Multiple Django users match: {name}")

        if options["dry_run"]:
            self.stdout.write(f"DRY RUN: would {'replace all existing posts and ' if options['replace'] else ''}seed up to {count} posts with 10 JPEG banners.")
            return

        # Generate or reuse exactly ten named JPEGs. Files are shared across articles.
        # Image files are not part of the DB transaction; leave existing images intact.
        field = Blog._meta.get_field("banner")
        storage = field.storage
        banner_paths = {}
        for i, (topic, _heading, key) in enumerate(TOPICS):
            filename = f"blog_banners/{key}.jpg"
            if not storage.exists(filename):
                storage.save(filename, ContentFile(make_jpeg(topic, i)))
            banner_paths[key] = filename

        created = 0
        with transaction.atomic():
            if options["replace"]:
                Blog.objects.all().delete()  # does not delete image files
            for index in range(count):
                topic, heading, key = TOPICS[index % len(TOPICS)]
                serial = index + 1
                slug = f"{slugify(key)}-{serial:04d}"
                if Blog.objects.filter(slug=slug).exists():
                    continue
                username = names[index % len(names)]
                Blog.objects.create(
                    title=f"{heading}: Guide {serial}",
                    body=(f"{topic}: Start by defining a clear goal and evaluating your current skills.\n\n"
                          "Create a practical project, document results, and ask for feedback.\n\n"
                          "Replace this sample with original editorial content."),
                    slug=slug,
                    link="",  # Internal navigation should use {% url 'blogs:blog_detail' b.id %}
                    date=timezone.now() - timedelta(days=index),
                    author=EDITORIAL_BY_USERNAME[username],
                    posted_by=users[username],
                    banner=banner_paths[key],
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} blogs; banners in MEDIA_ROOT/blog_banners/ (10 JPEG files)."))
