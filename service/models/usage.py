from django.db import models

from .promocode import Promocode


class UserPromocodeUsage(models.Model):
    promocode = models.ForeignKey(to=Promocode, on_delete=models.CASCADE)
    user_id = models.UUIDField()
    activations_count = models.PositiveIntegerField(db_default=0, editable=False)

    class Meta:
        unique_together = [('promocode', 'user_id')]


class UserFirstUsage(models.Model):
    user_id = models.UUIDField(unique=True)
