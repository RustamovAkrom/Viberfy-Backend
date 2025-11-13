from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.conf import settings
from django.core.cache import cache
from apps.shared.models.base import NamedModel
from .artist import Artist


class Album(NamedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="albums"
    )
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name="albums"
    )
    release_date = models.DateField(
        verbose_name=_("Release date"),
        blank=True,
        null=True,
        db_index=True
    )
    cover = models.ImageField(
        verbose_name=_("Cover"),
        upload_to="albums/covers/",
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True
    )
    is_published = models.BooleanField(
        verbose_name=_("Is published"),
        default=False,
        db_index=True
    )

    # новые поля
    plays_count = models.BigIntegerField(default=0, db_index=True)
    likes_count = models.BigIntegerField(default=0, db_index=True)
    listens_last_week = models.BigIntegerField(default=0)
    listens_last_month = models.BigIntegerField(default=0)

    class Meta:
        db_table = "musics_albums"
        indexes = [
            models.Index(fields=["release_date"]),
            models.Index(fields=["artist"]),
            models.Index(fields=["-plays_count"]),
            models.Index(fields=["-likes_count"]),
        ]
        verbose_name = _("Album")
        verbose_name_plural = _("Albums")

    # --- Уникальный slug (если есть альбомы с одинаковыми именами у разных артистов) ---
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Album.objects.filter(slug=slug, artist=self.artist).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # --- Количество треков ---
    @property
    def tracks_count(self):
        cache_key = f"album_{self.id}_tracks_count"
        count = cache.get(cache_key)
        if count is None:
            count = self.tracks.filter(is_published=True).count()
            cache.set(cache_key, count, timeout=60)
        return count

    # --- Оптимизированный список треков ---
    def get_tracks(self):
        return self.tracks.filter(is_published=True).select_related("artist", "album").prefetch_related("genres")

    # --- Топовые альбомы по прослушиваниям ---
    @classmethod
    def get_top_albums(cls, limit=10):
        key = f"top_albums_{limit}"
        albums = cache.get(key)
        if albums is None:
            albums = list(cls.objects.filter(is_published=True).order_by("-plays_count")[:limit])
            cache.set(key, albums, timeout=60)
        return albums

    def __str__(self):
        return f"{self.name} — {self.artist.name}"
