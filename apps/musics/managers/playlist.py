from django.db import models


class PlayListManager(models.Manager):
    def public(self):
        return self.get_queryset().filter(is_public=True)

    def by_user(self, user):
        return self.get_queryset().filter(user=user)
