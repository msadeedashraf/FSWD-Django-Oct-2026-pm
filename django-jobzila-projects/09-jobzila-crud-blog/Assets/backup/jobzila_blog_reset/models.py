from django.conf import settings
from django.db import models


class Blog(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField()
    link = models.URLField()
    date = models.DateTimeField()
    # Editorial byline (not the login name)
    author = models.CharField(max_length=50)
    banner = models.ImageField(blank=True)
    # Django account responsible for editing/deleting this article
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
    )

    @property
    def author_username(self):
        return self.posted_by.username if self.posted_by_id else ""

    @property
    def author_display_name(self):
        if not self.posted_by_id:
            return "JobZila Contributor"
        return self.posted_by.get_full_name() or self.posted_by.username

    def __str__(self):
        return self.title
