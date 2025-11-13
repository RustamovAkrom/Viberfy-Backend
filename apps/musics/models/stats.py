from django.db import models
from django.conf import settings
from .track import Track


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "musics_likes"
        unique_together = (("user", "track"),)
        indexes = [
            models.Index(fields=["track", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} likes {self.track}"


class ListeningHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listening_history",
    )
    track = models.ForeignKey(
        Track, on_delete=models.CASCADE, related_name="listened_by"
    )
    listened_at = models.DateTimeField(auto_now=True)
    duration = models.PositiveIntegerField(
        null=True, blank=True, help_text="how many seconds listened"
    )
    additional_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the listening session",
    )

    class Meta:
        db_table = "musics_listening_history"
        unique_together = (("user", "track"),)
        indexes = [
            models.Index(fields=["user", "listened_at"]),
            models.Index(fields=["track", "listened_at"]),
        ]

    def __str__(self):
        return f"{self.user} listened to {self.track} at {self.listened_at}"
