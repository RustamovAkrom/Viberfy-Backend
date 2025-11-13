from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100, unique=True)
    slug = models.SlugField(
        verbose_name=_("Slug"), max_length=120, unique=True, blank=True
    )
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)

    class Meta:
        db_table = "musics_genres"
        indexes = [models.Index(fields=["name"])]
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
