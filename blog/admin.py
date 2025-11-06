from django.contrib import admin
from .models import Blog, Post
from import_export.admin import ImportExportModelAdmin


class BlogAdmin(ImportExportModelAdmin):
    list_display = ["title", "created_by", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["title"]
    list_per_page = 25
    ordering = ["-created_at"]

    def created_by(self, obj):
        return obj.user.username

    created_by.short_description = "Created by"
    created_by.admin_order_field = "user__username"


class PostAdmin(ImportExportModelAdmin):
    list_display = ["title", "blog", "published_at", "updated_at"]
    list_filter = ["blog", "published_at", "updated_at"]
    search_fields = ["title", "blog__title"]
    list_per_page = 25
    ordering = ["-published_at"]


admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
