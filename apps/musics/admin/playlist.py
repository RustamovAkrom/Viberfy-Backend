from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.musics.models import Playlist, PlaylistTrack


class PlaylistTrackInline(admin.TabularInline):
    model = PlaylistTrack
    extra = 1


@admin.register(Playlist)
class PlaylistAdmin(UnfoldModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("title", "owner__username")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    inlines = [PlaylistTrackInline]
    prepopulated_fields = {"slug": ("name",)}
