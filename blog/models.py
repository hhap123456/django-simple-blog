from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from django_jalali.db import models as jmodels

#Managers
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Create your models here.
class Post(models.Model):
    class Status(models.TextChoices):   # for status field
        DRAFT = 'DR',   'Draft'
        PUBLISHED = 'PB', 'Published'
        REJECTED = 'RJ', 'Rejected',
    # relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts', verbose_name='نویسنده')
        # many-to-one relation
        # on_delete=models.CASCADE -> when user deleted, all of his post will be deleted.
        # related_name='user-posts' ->For access outside here   -

    # data fields
    title = models.CharField(max_length=250, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    slug = models.SlugField(max_length=250)
    # date
    publish = jmodels.jDateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")
    #publish = models.DateTimeField(default=timezone.now, verbose_name="تاریخ انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True)
    #created = models.DateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now=True)
    #updated = models.DateTimeField(auto_now=True)

    # choice fields
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name="وضعیت")
        # max_length=2 -> 2 charactor
        # choices -> inherit from parent class

    #objects = models.Manager()  # Default Manager
    objects = jmodels.jManager()
    published = PublishedManager()    # Custom Manager

    class Meta:
        ordering = ['-publish'] # sort by new posts
        indexes = [
            models.Index(fields=["publish"]),   # for database
        ]
        verbose_name = 'پست'
        verbose_name_plural = 'پست ها'


    def __str__(self):
        return self.title

