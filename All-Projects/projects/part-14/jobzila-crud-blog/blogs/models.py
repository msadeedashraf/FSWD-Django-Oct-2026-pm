from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    slug = models.SlugField(unique=True)
    link = models.URLField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100)
    banner = models.ImageField(
        upload_to="blog_banners/",
        blank=True,
        null=True,
    )
