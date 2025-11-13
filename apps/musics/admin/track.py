from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.musics.models import Track


@admin.register(Track)
class TrackAdmin(UnfoldModelAdmin):
    list_display = ("id", "name", "album", "duration", "created_at")
    search_fields = ("name", "album__name", "album__artist__name")
    list_filter = ("album__artist", "album")
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("name",)}
