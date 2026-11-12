"""Django management command: blogs/management/commands/reset_blog_table.py

Rebuild ONLY the blogs_blog table from the current migrated Blog model,
then seed it. Destructive. Use on a disposable local development DB only.
"""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from blogs.models import Blog
from blogs.author_mapping import EDITORIAL_BY_USERNAME


class Command(BaseCommand):
    help = 'DROP and recreate blogs_blog, then seed sample articles (DESTRUCTIVE).'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true')
        parser.add_argument('--count', type=int, default=100)

    def handle(self, *args, **options):
        if not options['confirm']:
            raise CommandError('Back up db.sqlite3 first, then pass --confirm.')
        count = options['count']
        if not 1 <= count <= 1000:
            raise CommandError('--count must be between 1 and 1000')
        if connection.vendor != 'sqlite':
            raise CommandError('This classroom command supports SQLite only.')
        User = get_user_model()
        missing = [name for name in EDITORIAL_BY_USERNAME
                   if not User.objects.filter(username__iexact=name).exists()]
        if missing:
            raise CommandError('Create these users before reset: ' + ', '.join(missing))
        table = Blog._meta.db_table
        if table != 'blogs_blog':
            raise CommandError(f'Unexpected table {table!r}; refusing reset.')
        existing = table in connection.introspection.table_names()
        with transaction.atomic():
            with connection.schema_editor() as editor:
                if existing:
                    editor.delete_model(Blog)
                editor.create_model(Blog)
            call_command('seed_blog_data', count=count, stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS(
            f'Rebuilt {table} and seeded {count} articles.'
        ))
