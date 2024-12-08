from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    class Status(models.TextChoices):   # for status field
        DRAFT = 'DR',   'Draft'
        PUBLISHED = 'PB', 'Published'
        REJECTED = 'RJ', 'Rejected',
    # relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
        # many-to-one relation
        # on_delete=models.CASCADE -> when user deleted, all of his post will be deleted.
        # related_name='user-posts' ->For access outside here   -

    # data fields
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=250)
    # date
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # choice fields
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
        # max_length=2 -> 2 charactor
        # choices -> inherit from parent class

    class Meta:
        ordering = ['-publish'] # sort by new posts
        indexes = [
            models.Index(fields=["publish"]),   # for database
        ]

    def __str__(self):
        return self.title

