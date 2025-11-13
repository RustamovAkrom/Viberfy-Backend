from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.musics.models import Genre


@admin.register(Genre)
class GenreAdmin(UnfoldModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
