from django.conf import settings
from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(unique=True)
    link = models.URLField(blank=True)
    date = models.DateTimeField()
    author = models.CharField(max_length=50)  # Editorial team byline
    banner = models.ImageField(upload_to='blog_banners/', blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='blog_posts',
    )

    @property
    def author_display_name(self):
        return self.posted_by.get_full_name() or self.posted_by.username

    def __str__(self):
        return self.title
