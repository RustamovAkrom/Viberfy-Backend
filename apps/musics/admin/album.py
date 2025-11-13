from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.musics.models import Album


@admin.register(Album)
class AlbumAdmin(UnfoldModelAdmin):
    list_display = ("id", "name", "artist", "release_date", "created_at")
    search_fields = ("name", "artist__name")
    list_filter = ("release_date",)
    date_hierarchy = "release_date"
    ordering = ("-release_date",)
    prepopulated_fields = {"slug": ("name",)}
