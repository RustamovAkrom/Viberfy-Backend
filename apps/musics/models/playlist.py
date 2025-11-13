from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.shared.models.base import NamedModel
from .track import Track
from apps.musics.managers.playlist import PlayListManager


class Playlist(NamedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="playlists",
        verbose_name=_("Owner"),
    )
    is_public = models.BooleanField(
        verbose_name=_("Is public?"), default=True, db_index=True
    )
    description = models.TextField(
        verbose_name=_("Description"), blank=True, null=True
    )
    cover = models.ImageField(
        verbose_name=_("Cover Image"),
        upload_to="playlists/covers/",
        blank=True,
        null=True,
    )
    tracks = models.ManyToManyField(
        Track,
        through="PlaylistTrack",
        related_name="in_playlists",
        verbose_name=_("Tracks"),
    )

    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="followed_playlists",
        blank=True,
        verbose_name=_("Followers"),
    )
    total_duration = models.PositiveIntegerField(
        verbose_name=_("Total Duration (seconds)"),
        default=0,
        help_text=_("Calculated automatically based on tracks duration."),
    )
    
    objects = PlayListManager()

    class Meta:
        db_table = "musics_playlists"
        indexes = [
            models.Index(fields=["owner", "is_public"]),
            models.Index(fields=["slug"]),
        ]
        verbose_name = _("Playlist")
        verbose_name_plural = _("Playlists")
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Playlist.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def update_total_duration(self):
        """Рассчитать и обновить общую длительность треков."""
        duration = (
            self.tracks.filter(is_published=True)
            .aggregate(models.Sum("duration"))
            .get("duration__sum")
            or 0
        )
        self.total_duration = duration
        self.save(update_fields=["total_duration"])

    @property
    def tracks_count(self):
        """Количество треков в плейлисте."""
        return self.tracks.count()

    @property
    def followers_count(self):
        """Количество подписчиков."""
        return self.followers.count()

    @property
    def is_empty(self):
        """Проверка, пуст ли плейлист."""
        return not self.tracks.exists()

    def __str__(self):
        return f"{self.name} — {self.owner.username}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("musics:playlist-detail", kwargs={"slug": self.slug})


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name="playlist_tracks"
    )
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        verbose_name=_("Order"), default=0, db_index=True
    )
    added_at = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_tracks",
    )

    class Meta:
        db_table = "musics_playlist_tracks"
        unique_together = (("playlist", "track"),)
        ordering = ["order"]
        verbose_name = _("Playlist Track")
        verbose_name_plural = _("Playlist Tracks")

    def __str__(self):
        return f"{self.order}. {self.track.name}"

__all__ = ["Playlist", "PlaylistTrack"]
