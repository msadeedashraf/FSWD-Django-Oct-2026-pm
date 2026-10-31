"""Reset ONLY Blog records and seed 100 demo posts with local banner images.

Install: python -m pip install Pillow
Place: blogs/management/commands/reset_seed_blogs.py
Run: python manage.py reset_seed_blogs --confirm
"""
from datetime import timedelta
from io import BytesIO
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from blogs.models import Blog

TOPICS = [
    ("Python Development", "python", "photo-1515879218367-8466d910aaa4"),
    ("Data Analytics", "data", "photo-1551288049-bebda4e38f71"),
    ("Artificial Intelligence", "ai", "photo-1677442136019-21780ecad995"),
    ("Job Interviews", "interviews", "photo-1521737711867-e3b97375f902"),
    ("Remote Work", "remote", "photo-1497366811353-6870744d04b2"),
    ("Cloud Computing", "cloud", "photo-1451187580459-43490279c0fa"),
    ("Cybersecurity", "security", "photo-1550751827-4bd374c3f58b"),
    ("Career Planning", "career", "photo-1522071820081-009f0129c71c"),
    ("Web Development", "web", "photo-1498050108023-c5249f4df085"),
    ("Project Management", "projects", "photo-1552664730-d307ca884978"),
]
ANGLES = [
    "A Beginner's Guide to {}", "Practical Skills for {}", "Common Mistakes in {}",
    "How to Build a Portfolio in {}", "Career Opportunities in {}",
    "Tools and Techniques for {}", "A 30-Day Learning Plan for {}",
    "What Employers Look for in {}", "Interview Preparation for {}",
    "How to Get Started with {}",
]
AUTHORS = ["JobZila Editorial Team", "Career Research Desk", "Technology Learning Team"]


def stock_photo(photo_id):
    """Best-effort Unsplash photo; no API key required, may fail offline."""
    url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1200&h=675&q=75"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (JobZila classroom demo)"})
    try:
        with urlopen(req, timeout=7) as response:
            data = response.read(3_000_000)
        im = Image.open(BytesIO(data)).convert("RGB")
        im.thumbnail((1200, 675))
        output = BytesIO()
        im.save(output, format="JPEG", quality=85)
        return output.getvalue()
    except Exception:
        return None


def fallback_banner(topic, index):
    colors = ["#253B55", "#184E77", "#264653", "#343A40", "#3D405B"]
    im = Image.new("RGB", (1200, 675), colors[index % len(colors)])
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 615, 1200, 675), fill="#FF8500")
    font = ImageFont.load_default()
    draw.text((70, 285), topic, fill="white", font=font)
    draw.text((70, 632), "JOBZILA  |  CAREER INSIGHTS", fill="white", font=font)
    output = BytesIO()
    im.save(output, format="JPEG", quality=88)
    return output.getvalue()


class Command(BaseCommand):
    help = "Delete Blog records and recreate demo posts with media-backed banners."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--confirm", action="store_true", help="Required: permits deleting existing Blog records")
        parser.add_argument("--no-download", action="store_true", help="Generate all banners locally (no network)")

    def handle(self, *args, **options):
        count = options["count"]
        if not options["confirm"]:
            raise CommandError("This deletes ALL Blog records. Rerun with --confirm if this is a disposable demo database.")
        if not 1 <= count <= 100:
            raise CommandError("--count must be between 1 and 100")

        # Download only ten images, then reuse bytes for the 100 local banner files.
        images = {}
        for topic, key, photo_id in TOPICS:
            images[key] = None if options["no_download"] else stock_photo(photo_id)
            if images[key] is None:
                self.stdout.write(f"Using generated banner for {topic}")

        # Only delete banner files referenced by existing Blog records, not unrelated media.
        old_files = [(b.banner.storage, b.banner.name) for b in Blog.objects.exclude(banner="") if b.banner.name]
        with transaction.atomic():
            Blog.objects.all().delete()
            now = timezone.now()
            for index in range(count):
                topic, key, _ = TOPICS[index % len(TOPICS)]
                angle = ANGLES[index // len(TOPICS)]
                title = angle.format(topic)
                slug = slugify(title)
                body = (
                    f"{title}\n\n"
                    f"Understanding {topic.lower()} starts with a clear goal and a practical learning plan. "
                    "Identify the core skills, practice them in small projects, and document what you learn.\n\n"
                    "Start by choosing one beginner-friendly resource. Spend time applying the ideas instead of "
                    "only watching tutorials. Save examples of your work and explain the decisions you made.\n\n"
                    "As you progress, ask for feedback, improve your portfolio, and prepare to describe your "
                    "experience clearly in interviews. Consistent practice matters more than collecting certificates.\n\n"
                    "This is fictional classroom sample content, not a real job posting or professional advice."
                )
                # Current Module 05 model uses a URLField for link, not a detail-page URL.
                blog = Blog(
                    title=title,
                    slug=slug,
                    body=body,
                    link="http://127.0.0.1:8000/blogs/",
                    date=now - timedelta(days=index),
                    author=AUTHORS[index % len(AUTHORS)],
                )
                photo = images[key] or fallback_banner(topic, index)
                # ImageField.save() stores the file under MEDIA_ROOT and records its path.
                blog.banner.save(f"jobzila-{slug}.jpg", ContentFile(photo), save=False)
                blog.save()
        # Cleanup only after a successful DB transaction. Avoid deleting paths still used.
        current_names = set(Blog.objects.exclude(banner="").values_list("banner", flat=True))
        for storage, name in set(old_files):
            if name not in current_names and name.startswith("blog_banners/"):
                try:
                    storage.delete(name)
                except Exception as exc:
                    self.stderr.write(f"Could not delete old banner {name}: {exc}")
        self.stdout.write(self.style.SUCCESS(f"Created {count} blogs with saved banner files."))
        self.stdout.write("Verify MEDIA_URL, MEDIA_ROOT, and development media URL routing in Django settings/urls.py")
