from django.utils.translation import gettext_lazy as _
from django.db import models


class TimeStempedModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=("Updated At"), auto_now=True)

    class Meta:
        abstract = True


class NamedModel(TimeStempedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=255, db_index=True)
    slug = models.SlugField(
        verbose_name=_("Slug"), max_length=255, blank=True, null=True, unique=True
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
