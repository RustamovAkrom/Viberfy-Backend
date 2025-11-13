from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.shared.models.base import TimeStempedModel
from apps.users.managers.user import UserManager


class User(AbstractUser, TimeStempedModel):
    class SubscriptionTypeChoices(models.TextChoices):
        FREE = "free", _("Free")
        PREMIUM = "premium", _("Premium")

    username = models.CharField(
        verbose_name=_("Username"), max_length=250, unique=True, db_index=True
    )
    email = models.EmailField(
        verbose_name=_("Email adress"), unique=True, db_index=True
    )
    avatar = models.ImageField(
        upload_to="avatars/%Y/%M/%d",
        default="/default/default-avatar.jpg",
        blank=True,
        null=True,
    )
    subscription_type = models.CharField(
        max_length=20,
        choices=SubscriptionTypeChoices.choices,
        default=SubscriptionTypeChoices.FREE.value,
        db_index=True,
    )
    is_email_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)

    objects = UserManager()

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email
