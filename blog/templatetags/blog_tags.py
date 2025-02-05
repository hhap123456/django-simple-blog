from django import template
from django.template.defaulttags import comment
from django_jalali.templatetags.jformat import jformat
from django.db.models import Count, Q
from ..models import Post, Comment,User
from markdown import markdown
from django.utils.safestring import mark_safe
from random import randint

register = template.Library()

@register.simple_tag()
def total_posts():
    return Post.published.count()

@register.simple_tag()
def total_comments():
    return Comment.objects.filter(active=True).count()

@register.simple_tag()
def last_post():
    return jformat(Post.published.first().publish, "%Y/%m/%d - %H:%I")

@register.inclusion_tag('partials/latest_post.html')
def latest_post(count=5):
    last_posts = Post.published.order_by('-publish')[:count]
    context = {
        'last_posts': last_posts
    }

    return context

@register.simple_tag()
def most_popular_posts(count=5):
    return Post.published.annotate(comments_count=Count('comments')).order_by('-comments_count')[:count]

@register.filter(name='markdown')
def to_markdown(value):
    return mark_safe(markdown(value))

@register.simple_tag()
def most_reading_time():
    return Post.published.order_by('-reading_time').first().reading_time

@register.simple_tag()
def least_reading_time():
    return Post.published.order_by('reading_time').first().reading_time

@register.simple_tag()
def active_users(count=5):
    return User.objects.annotate(post_count=Count('user_post'),
                                 filter=Q(comments__active=True)).order_by('-post_count')[:count]

@register.filter
def is_post(obj):
    return obj.__class__.__name__ == 'Post'

@register.filter
def is_image(obj):
    return obj.__class__.__name__ == 'Image'

@register.simple_tag()
def most_popular_author_posts(pk, count=5):
    return Post.published.filter(author_id=pk).annotate(comments_count=Count('comments'),
                                                        filter=Q(comments__active=True)).order_by('-comments_count')[:count]

@register.simple_tag()
def suggested_post():
    count = Post.published.count()
    random_pk = randint(0, count - 1)

    return Post.published.all()[random_pk]