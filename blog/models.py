from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.urls import reverse
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
    reading_time = models.PositiveIntegerField(verbose_name="زمان مطالعه")
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

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])


class Ticket(models.Model):
    massage = models.TextField( verbose_name="پیام")
    name = models.CharField(max_length=250, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    subject = models.CharField(max_length=250, verbose_name="موضوع")

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت ها'

    def __str__(self):
        return self.subject


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    name = models.CharField(max_length=250, verbose_name="نام")
    body = models.TextField(verbose_name="متن کامنت")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")
    active = models.BooleanField(default=False, verbose_name="وضعیت")


    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=["created"]),
        ]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

        def __str__(self):
            return f"{self.name}:{self.post}"

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images", verbose_name="تصویر")
    image_file = models.ImageField(upload_to='post_images')
    title = models.CharField(max_length=250, null=True, blank=True, verbose_name="عنوان")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    # date
    created = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=["created"]),
        ]
        verbose_name = "تصویر"
        verbose_name_plural = "تصویرها ها"

        def __str__(self):
            return self.title if self.title else "None"