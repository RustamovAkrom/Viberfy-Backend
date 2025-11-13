from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.conf import settings
from django.db import models
from django.core.cache import cache
from apps.shared.models.base import NamedModel


class Artist(NamedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artists"
    )
    bio = models.TextField(
        verbose_name=_("Bio"),
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="artists/avatars/",
        blank=True,
        null=True
    )
    meta = models.JSONField(
        verbose_name=_("Meta data"),
        default=dict,
        blank=True,
        help_text=_("Additional data such as social links, country, etc.")
    )

    # Дополнительные поля
    followers_count = models.PositiveIntegerField(default=0, db_index=True)
    total_plays = models.BigIntegerField(default=0, db_index=True)
    total_likes = models.BigIntegerField(default=0, db_index=True)

    is_verified = models.BooleanField(default=False, verbose_name=_("Verified artist"))
    
    class Meta:
        db_table = "musics_artists"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["-followers_count"]),
            models.Index(fields=["-total_plays"]),
        ]
        verbose_name = _("Artist")
        verbose_name_plural = _("Artists")

    # --- Уникальный slug ---
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Artist.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # --- Кэш популярных артистов ---
    @classmethod
    def get_top_artists(cls, limit=10):
        cache_key = f"top_artists_{limit}"
        artists = cache.get(cache_key)
        if artists is None:
            artists = list(
                cls.objects.filter(is_verified=True)
                .order_by("-total_plays", "-followers_count")[:limit]
            )
            cache.set(cache_key, artists, timeout=60)
        return artists

    def __str__(self):
        return self.name
