"""Seed sample JobZila jobs: python manage.py seed_jobs --count 100"""
import random
from django.core.management.base import BaseCommand
from jobs.models import Job

TITLES = [
    'Python Developer', 'Software Developer', 'Full Stack Developer',
    'Frontend Developer', 'Backend Developer', 'Data Analyst',
    'Data Scientist', 'Machine Learning Engineer', 'AI Engineer',
    'DevOps Engineer', 'Cloud Engineer', 'Database Administrator',
    'Cybersecurity Analyst', 'Business Analyst', 'Product Manager',
    'Project Manager', 'QA Engineer', 'UI/UX Designer',
    'Technical Support Specialist', 'Power BI Developer',
]
COMPANIES = [
    'Maple Tech Solutions', 'Northern Analytics', 'BrightPath Digital',
    'Summit Software', 'BlueLake Systems', 'Evergreen Consulting',
    'Northstar Innovations', 'CloudBridge Labs', 'Cedar Data Group',
    'UrbanCode Studio',
]
LOCATIONS = [
    'Toronto, ON', 'Hamilton, ON', 'Mississauga, ON', 'Burlington, ON',
    'Ottawa, ON', 'Waterloo, ON', 'London, ON', 'Vancouver, BC',
    'Calgary, AB', 'Montreal, QC',
]
SKILLS = [
    'Python, Django, REST APIs, and SQL',
    'JavaScript, React, HTML, and CSS',
    'Power BI, Excel, SQL, and reporting',
    'Azure, Docker, CI/CD, and cloud services',
    'data modeling, analytics, and problem solving',
    'communication, teamwork, and agile delivery',
]

class Command(BaseCommand):
    help = 'Create sample Job records for search and filtering lessons.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100)
        parser.add_argument('--clear', action='store_true', help='Delete ALL existing jobs before seeding (destructive).')

    def handle(self, *args, **options):
        count = options['count']
        if count < 1:
            self.stderr.write('Count must be at least 1.')
            return
        if options['clear']:
            deleted, _ = Job.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} database objects.'))

        random.seed(42)
        combinations = [(title, company, location) for title in TITLES for company in COMPANIES for location in LOCATIONS]
        random.shuffle(combinations)
        created = 0
        for title, company, location in combinations[:min(count, len(combinations))]:
            skill = random.choice(SKILLS)
            description = (
                f'{company} is hiring a {title} in {location}. '
                f'The successful candidate will work with {skill}. '
                'Responsibilities include collaborating with colleagues, delivering reliable solutions, '
                'documenting work, and improving business outcomes. '
                'This is a fictional job listing created for classroom testing.'
            )
            _, was_created = Job.objects.get_or_create(
                title=title, company=company, location=location,
                defaults={
                    'description': description,
                    'apply_link': 'https://teczila.com/careers/',
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Created {created} new jobs. Total jobs in database: {Job.objects.count()}.'
        ))
        if count > len(combinations):
            self.stdout.write(self.style.WARNING(f'Maximum unique combinations: {len(combinations)}.'))
