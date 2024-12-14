from django import template
from django_jalali.templatetags.jformat import jformat

from ..models import Post, Comment

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