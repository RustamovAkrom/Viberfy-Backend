from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.musics.models import Artist


@admin.register(Artist)
class ArtistAdmin(UnfoldModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("name",)}
