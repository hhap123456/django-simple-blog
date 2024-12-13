from django.contrib import admin
from .models import Post, Ticket
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin

# For Persianization
admin.sites.AdminSite.site_header = "پنل مدیریت جنگو"
admin.sites.AdminSite.site_title = "پنل"
admin.sites.AdminSite.index_title = "پنل مدیریت"



# Register your models here.
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

    # i added
    @staticmethod
    def short_description(obj):     # for shorting description to 10 charactor
        return obj.description[:10] + '...' if len(obj.description) > 10 else obj.description

    empty_value_display = '--empty--'     # show this if field is empty


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'phone',)

