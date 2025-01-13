from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Post, Ticket, Comment, Image, Account
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin

# For Persianization
admin.sites.AdminSite.site_header = "پنل مدیریت جنگو"
admin.sites.AdminSite.site_title = "پنل"
admin.sites.AdminSite.index_title = "پنل مدیریت"

# inlines

class ImageInLine(admin.TabularInline):
    model = Image
    extra = 0
    # i added
    readonly_fields = ('image_preview',)
    fields = ('image_file', 'title', 'description', 'image_preview')

    def image_preview(self, obj):
        if obj.image_file:  # Replace 'image' with your image field name
            return mark_safe(f'<img src="{obj.image_file.url}" width="280" />')
        return "No image"

    image_preview.short_description = 'پیش نمایش'


class CommentInLine(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'short_description', 'publish', 'status')
        # description >> short_description
    ordering = ('-publish',)
    list_filter = ['status', ('publish', JDateFieldListFilter), 'author']  # set filter buttons
    search_fields = ('title', 'description',)
    raw_id_fields = ('author',)     # new author panel in add/change post
    date_hierarchy = 'publish'
    prepopulated_fields = {"slug": ("title",)}      # auto fill slug
    list_editable = ('status',)     # change in main view
    list_display_links = ('title', 'author',)       # make link (blue)

    inlines = [
        ImageInLine,
        CommentInLine
    ]

    # i added
    @staticmethod
    def short_description(obj):     # for shorting description to 10 charactor
        return obj.description[:10] + '...' if len(obj.description) > 10 else obj.description

    empty_value_display = '--empty--'     # show this if field is empty


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'phone',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "post", "active",)
    list_filter = ('active', ('created', JDateFieldListFilter), ('updated', JDateFieldListFilter),)
    search_fields = ('name', 'body',)
    list_editable = ('active',)
    
    
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("post", "created", "title")

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'job', 'bio', 'photo']
