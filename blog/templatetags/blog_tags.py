from django import template
from django_jalali.templatetags.jformat import jformat
from django.db.models import Count
from ..models import Post, Comment
from markdown import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag()
def total_posts():
    return Post.published.count()

@register.simple_tag()
def total_comments():
    return Comment.objects.filter(active=True).count()

@register.simple_tag()
def last_post():
    return jformat(Post.published.last().publish, "%Y/%M/%d - %H:%I")

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