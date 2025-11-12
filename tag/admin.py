from django.contrib import admin
from .models import Tag
from import_export.admin import ImportExportModelAdmin


class TagAdmin(ImportExportModelAdmin):
    list_display = ["name", "get_posts_count"]
    search_fields = ["name"]
    list_per_page = 50
    ordering = ["name"]

    def get_posts_count(self, obj):
        return obj.posts.count()

    get_posts_count.short_description = "Posts counter"


admin.site.register(Tag, TagAdmin)
