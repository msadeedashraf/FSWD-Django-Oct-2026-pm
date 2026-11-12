"""Safely map existing blogs to real users and editorial teams.

Run: python manage.py assign_blog_authors --dry-run
     python manage.py assign_blog_authors
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from blogs.author_mapping import EDITORIAL_BY_USERNAME
from blogs.models import Blog


class Command(BaseCommand):
    help = "Assign existing blog records to users and editorial team bylines without deleting content or images."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview changes without saving")
        parser.add_argument("--overwrite", action="store_true", help="Also reassign blogs that already have an owner")

    def handle(self, *args, **options):
        User = get_user_model()
        names = list(EDITORIAL_BY_USERNAME)
        users = {}
        for name in names:
            try:
                users[name] = User.objects.get(username__iexact=name)
            except User.DoesNotExist:
                raise CommandError(f"Missing user '{name}'. Create it first with createsuperuser or admin.")
            except User.MultipleObjectsReturned:
                raise CommandError(f"Multiple users match '{name}' case-insensitively.")

        posts = Blog.objects.order_by("pk")
        updated = skipped = 0
        with transaction.atomic():
            for index, post in enumerate(posts.iterator()):
                if post.posted_by_id and not options["overwrite"]:
                    skipped += 1
                    continue
                username = names[index % len(names)]
                post.posted_by = users[username]
                post.author = EDITORIAL_BY_USERNAME[username]
                if not options["dry_run"]:
                    post.save(update_fields=["posted_by", "author"])
                updated += 1
            if options["dry_run"]:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(
            f"{'Would update' if options['dry_run'] else 'Updated'} {updated} blogs; skipped {skipped}."
        ))
