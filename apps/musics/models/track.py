from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.db.models import F
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.shared.models.base import NamedModel
from .artist import Artist
from .album import Album
from .genres import Genre
from apps.musics.managers.track import TrackManager
from django.core.cache import cache
 

class Track(NamedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="tracks",
        verbose_name=_("Owner"),
    )
    artist = models.ForeignKey(
        Artist, 
        on_delete=models.CASCADE, 
        related_name="tracks",
        verbose_name=_("Artist"),
    )
    album = models.ForeignKey(
        Album, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="tracks",
        verbose_name=_("Album"),
    )
    featured_artists = models.ManyToManyField(
        Artist, 
        related_name="featured_tracks", 
        blank=True,
        verbose_name=_("Featured Artists"),
    )
    duration = models.PositiveIntegerField(
        verbose_name=_("Duration"),
        help_text="seconds",
        validators=[MinValueValidator(1)],
    )
    audio = models.FileField(verbose_name=_("Audio File"), upload_to="tracks/audio/")
    cover = models.ImageField(
        verbose_name=_("Cover Image"), upload_to="tracks/covers/", blank=True, null=True
    )
    genres = models.ManyToManyField(Genre, related_name="tracks", blank=True, verbose_name=_("Genres"))

    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    release_date = models.DateField(verbose_name=_("Release Date"), blank=True, null=True)
    language = models.CharField(
        verbose_name=_("Language"), max_length=50, blank=True, null=True
    )

    plays_count = models.BigIntegerField(
        verbose_name=_("Plays Count"), default=0, db_index=True
    )
    likes_count = models.BigIntegerField(
        verbose_name=_("Likes count"), default=0, db_index=True
    )
    download_count = models.BigIntegerField(
        verbose_name=_("Download Count"), default=0
    )

    is_explicit = models.BooleanField(verbose_name=_("Explicit Content"), default=False)
    lyrics = models.TextField(verbose_name=_("Lyrics"), blank=True, null=True)
    youtube_url = models.URLField(verbose_name=_("YouTube URL"), blank=True, null=True)
    bpm = models.PositiveIntegerField(blank=True, null=True, help_text="Beats per minute")
    bitrate = models.PositiveIntegerField(
        verbose_name=_("Bitrate (kbps)"), blank=True, null=True
    )

    mood = models.CharField(
        verbose_name=_("Mood / Vibe"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("e.g. Chill, Energetic, Sad, Romantic"),
    )

    is_published = models.BooleanField(verbose_name=_("Is published"), default=True, db_index=True)

    objects = TrackManager()

    class Meta:
        db_table = "musics_tracks"
        indexes = [
            models.Index(fields=["-plays_count", "is_published"]),
            models.Index(fields=["-likes_count", "is_published"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "artist"], name="unique_track_per_artist"
            )
        ]
        verbose_name = _("Track")
        verbose_name_plural = _("Tracks")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.artist.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Track.objects.filter(slug=slug, artist=self.artist).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def increment_play(self):
        Track.objects.filter(id=self.id).update(plays_count=F("plays_count") + 1)
        cache.delete(f"track_{self.id}_stats")

    def increment_like(self):
        Track.objects.filter(id=self.id).update(likes_count=F("likes_count") + 1)
        cache.delete(f"track_{self.id}_stats")
    
    def increment_download(self):
        Track.objects.filter(id=self.id).update(download_count=F("download_count") + 1)

    @property
    def stats(self):
        """Возвращает данные о треке с кэшем."""
        key = f"track_{self.id}_stats"
        data = cache.get(key)
        if data is None:
            data = {
                "plays": self.plays_count,
                "likes": self.likes_count,
                "downloads": self.download_count,
                "duration": self.duration,
                "album": self.album_name,
            }
            cache.set(key, data, timeout=30)
        return data
    
    # --- Кэш топ треков ---
    @classmethod
    def get_top_tracks(cls, limit=10):
        """Кэшированный список популярных треков."""
        key = f"top_tracks_{limit}"
        top_tracks = cache.get(key)
        if top_tracks is None:
            top_tracks = list(
                cls.objects.filter(is_published=True)
                .order_by("-plays_count")[:limit]
            )
            cache.set(key, top_tracks, timeout=60)
        return top_tracks

    # --- Свойства для сериализатора ---
    @property
    def artist_name(self):
        return self.artist.name if self.artist else None

    @property
    def album_name(self):
        return self.album.name if self.album else None

    @property
    def genres_list(self):
        return [genre.name for genre in self.genres.all()]


    @property
    def readable_duration(self):
        minutes, seconds = divmod(self.duration, 60)
        return f"{minutes}:{seconds:02d}"
    
    @property
    def cover_url(self):
        if self.cover:
            return self.cover.url
        return None

    @property
    def audio_url(self):
        if self.audio:
            return self.audio.url
        return None
    @property
    def featured_artists_names(self):
        return [artist.name for artist in self.featured_artists.all()]
