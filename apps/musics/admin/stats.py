from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from apps.musics.models import Like, ListeningHistory


@admin.register(Like)
class LikeAdmin(UnfoldModelAdmin):
    list_display = ("id", "user", "track", "created_at")
    search_fields = ("user__username", "track__name", "track__artist__name")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(ListeningHistory)
class ListeningHistoryAdmin(UnfoldModelAdmin):
    list_display = ("id", "user", "track", "listened_at", "duration")
    search_fields = ("user__username", "track__name", "track__artist__name")
    list_filter = ("listened_at",)
    date_hierarchy = "listened_at"
    ordering = ("-listened_at",)
