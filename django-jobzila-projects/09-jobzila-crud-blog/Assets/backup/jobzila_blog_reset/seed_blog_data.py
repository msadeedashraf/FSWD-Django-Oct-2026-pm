"""Non-destructive demo blog seed with real owner accounts and editorial bylines.

Run: python manage.py seed_blog_data --count 100
The command only creates records and never deletes existing blogs.
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
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


class Command(BaseCommand):
    help = "Create demo blog posts with mapped Django users and editorial bylines; no destructive reset."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        count = options["count"]
        if not 1 <= count <= 1000:
            raise CommandError("--count must be between 1 and 1000")
        User = get_user_model()
        names = list(EDITORIAL_BY_USERNAME)
        users = {}
        for name in names:
            try:
                users[name] = User.objects.get(username__iexact=name)
            except User.DoesNotExist:
                raise CommandError(f"Missing user '{name}'. Create the account first.")
            except User.MultipleObjectsReturned:
                raise CommandError(f"Multiple accounts match '{name}'")

        created = 0
        with transaction.atomic():
            for index in range(count):
                topic, heading, key = TOPICS[index % len(TOPICS)]
                serial = index + 1
                slug = f"{slugify(key)}-{serial:04d}"
                if Blog.objects.filter(slug=slug).exists():
                    continue  # repeatable: never overwrite an existing article
                username = names[index % len(names)]
                user = users[username]
                if options["dry_run"]:
                    created += 1
                    continue
                post = Blog.objects.create(
                    title=f"{heading}: Guide {serial}",
                    body=(f"{topic}: Start by defining a clear goal and evaluating your current skills.\n\n"
                          "Create a small practical project, document the results, and ask for feedback.\n\n"
                          "Use this demonstration article as a starting point and replace it with original editorial content."),
                    slug=slug,
                    link="http://localhost:8000/blogs/",  # overwritten immediately below
                    date=timezone.now() - timedelta(days=index),
                    author=EDITORIAL_BY_USERNAME[username],
                    posted_by=user,
                    banner="",  # demo posts have a placeholder instead of an uploaded image
                )
                post.link = f"http://127.0.0.1:8000{reverse('blogs:blog_detail', args=[post.pk])}"
                post.save(update_fields=["link"])
                created += 1
            if options["dry_run"]:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            f"{'Would create' if options['dry_run'] else 'Created'} {created} demo blogs."
        ))
