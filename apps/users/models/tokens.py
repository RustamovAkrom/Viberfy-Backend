from django.db import models
from datetime import timedelta
from django.utils import timezone
from apps.users.models import User
import uuid


def default_expiry():
    return timezone.now() + timedelta(hours=2)


class UserToken(models.Model):
    TOKEN_TYPE_CHOICES = (
        ("verify", "Email Verification"),
        ("reset", "Password Reset"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at or self.is_used

    def __str__(self):
        return f"{self.user.email} - {self.token_type}"
