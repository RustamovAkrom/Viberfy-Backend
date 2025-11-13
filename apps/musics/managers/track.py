from django.db import models
from django.db.models import Q
from django.utils import timezone


class TrackQuerySet(models.QuerySet):
    def popular(self, days=None):
        qs = self.order_by("-plays_count")
        if days:
            since = timezone.now() - timezone.timedelta(days=days)
            return qs.filter(created_at__gte=since)
        return qs

    def by_genre(self, genre):
        return self.filter(genres__name__iexact=genre)

    def search(self, q):
        return self.filter(
            Q(name__icontains=q) | Q(artist__name__icontains=q) | Q(album__icontains=q)
        )

    def with_artist_album(self):
        return self.select_related("artist", "album")


class TrackManager(models.Manager):
    def get_queryset(self):
        return TrackQuerySet(self.model, using=self._db)

    def popular(self, *args, **kwargs):
        return self.get_queryset().popular(*args, **kwargs)

    def search(self, q):
        return self.get_queryset().search(q)

    def get_similar_tracks(self, track, limit=10):
        """
        Возвращает похожие треки по жанру или артисту
        """
        return (
            self.get_queryset()
            .filter(
                Q(genres__in=track.genres.all()) | Q(artist=track.artist),
                is_published=True,
            )
            .exclude(pk=track.pk)
            .distinct()
            .order_by("-plays_count")[:limit]
        )

