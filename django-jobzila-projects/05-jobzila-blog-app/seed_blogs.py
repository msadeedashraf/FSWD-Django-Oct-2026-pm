"""Seed fictional JobZila blog posts.

Install Pillow first: python -m pip install Pillow
Run: python manage.py seed_blogs --count 100
"""
from datetime import timedelta
from io import BytesIO
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from blogs.models import Blog

TOPICS = [
    ("How to Write a Resume That Gets Noticed", "Resume Writing"),
    ("Preparing for Your Next Job Interview", "Interviews"),
    ("Building a Strong LinkedIn Profile", "Professional Branding"),
    ("Finding Your First Job in Canada", "Job Search"),
    ("Making a Career Change into Technology", "Career Transitions"),
    ("Essential Python Skills for New Developers", "Technology"),
    ("Starting a Career in Data Analytics", "Data Careers"),
    ("Understanding Artificial Intelligence at Work", "Artificial Intelligence"),
    ("Improving Communication at Work", "Workplace Skills"),
    ("Negotiating Your First Salary Offer", "Compensation"),
    ("Creating a Practical Learning Plan", "Professional Development"),
    ("Networking Without Feeling Awkward", "Networking"),
    ("How to Evaluate a Job Offer", "Job Offers"),
    ("Managing Your Time While Job Hunting", "Productivity"),
    ("Building a Portfolio That Shows Your Skills", "Portfolio"),
    ("Remote Work Skills Employers Value", "Remote Work"),
    ("Writing a Cover Letter with a Clear Message", "Applications"),
    ("Understanding Entry-Level Cybersecurity Roles", "Cybersecurity"),
    ("Preparing for a Technical Assessment", "Technical Interviews"),
    ("Using SQL to Solve Business Problems", "Data Skills"),
]
ANGLES = [
    "A Beginner's Guide", "Practical Steps", "Common Mistakes to Avoid",
    "A Checklist for Success", "Strategies You Can Use Today",
]
AUTHORS = ["JobZila Editorial Team", "Avery Morgan", "Jordan Lee", "Taylor Singh", "Casey Patel"]
PALETTES = [
    ((36, 44, 60), (255, 133, 0)),
    ((23, 60, 75), (255, 163, 59)),
    ((49, 40, 70), (244, 142, 54)),
    ((35, 65, 54), (255, 146, 49)),
]


def banner_bytes(title, category, index):
    """Create a local JPEG banner; no external image downloads required."""
    dark, accent = PALETTES[index % len(PALETTES)]
    image = Image.new("RGB", (1200, 630), dark)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 24, 630), fill=accent)
    draw.ellipse((865, -155, 1310, 290), outline=accent, width=15)
    draw.ellipse((945, 355, 1220, 630), outline=accent, width=10)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 53)
        label_font = ImageFont.truetype("DejaVuSans.ttf", 27)
    except OSError:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    draw.text((80, 85), "JOBZILA  /  INSIGHTS", font=label_font, fill=accent)
    # Wrap text by approximate measured width.
    lines, current = [], ""
    for word in title.split():
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=title_font)[2] > 790 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for line_no, line in enumerate(lines[:4]):
        draw.text((80, 180 + 77 * line_no), line, font=title_font, fill="white")
    draw.text((80, 565), category.upper(), font=label_font, fill=accent)
    output = BytesIO()
    image.save(output, format="JPEG", quality=86, optimize=True)
    return output.getvalue()


class Command(BaseCommand):
    help = "Create fictional JobZila blog posts with locally generated banners."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100, help="Number of sample posts (default: 100)")
        parser.add_argument("--clear", action="store_true", help="DELETE ALL existing blogs before seeding (development only)")

    def handle(self, *args, **options):
        count = options["count"]
        if not 1 <= count <= len(TOPICS) * len(ANGLES):
            raise CommandError("--count must be between 1 and 100.")

        if options["clear"]:
            deleted, _ = Blog.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing database objects. Old media files may remain."))

        rng = random.Random(42)
        combinations = [(topic, category, angle) for topic, category in TOPICS for angle in ANGLES]
        rng.shuffle(combinations)
        created = 0
        skipped = 0
        now = timezone.now()

        for index, (topic, category, angle) in enumerate(combinations[:count], start=1):
            title = f"{topic}: {angle}"
            slug = slugify(title)
            if Blog.objects.filter(slug=slug).exists():
                skipped += 1
                continue

            body = (
                f"{title}\n\n"
                f"Getting started with {category.lower()} is easier when you use a clear, repeatable process. "
                "Begin by identifying your goal and the specific skills or evidence you need to demonstrate.\n\n"
                "Step 1: Review your current situation. Write down your strengths, experience, and the gaps "
                "you want to address. Avoid making assumptions without checking the requirements.\n\n"
                "Step 2: Make a practical plan. Break the work into small tasks, set realistic deadlines, "
                "and keep a record of what you complete.\n\n"
                "Step 3: Practice and gather feedback. Ask a trusted colleague, instructor, or mentor "
                "to review your work. Use the feedback to improve one thing at a time.\n\n"
                "Step 4: Measure progress. Revisit your goals weekly and adjust your approach based on results.\n\n"
                "This is fictional demonstration content for the JobZila classroom project, not a real published article."
            )
            # Use a real route that exists in Module 05 (the blog listing).
            # The model currently has no detail-page URL, so this link returns to /blogs/.
            blog = Blog(
                title=title,
                body=body,
                slug=slug,
                link="/blogs/",
                date=now - timedelta(days=index * 2),
                author=rng.choice(AUTHORS),
            )
            filename = f"jobzila-blog-{slug}.jpg"
            blog.banner.save(filename, ContentFile(banner_bytes(title, category, index)), save=False)
            blog.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created {created} blogs; skipped {skipped} duplicates; total in database: {Blog.objects.count()}."
        ))
        self.stdout.write("Note: blog links point to /blogs/ until you implement individual blog detail pages.")
