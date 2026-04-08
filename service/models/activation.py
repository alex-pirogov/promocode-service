from django.db import models
from django.db.models.functions import Now

from .plan import Plan
from .promocode import Promocode


class PromocodeActivation(models.Model):
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name='activations')
    user_id = models.UUIDField()
    created_at = models.DateTimeField(db_default=Now())
    plan = models.ForeignKey(
        to=Plan, on_delete=models.CASCADE, related_name='promocode_activations'
    )

    class Meta:
        verbose_name = 'Promocode activation'

    def __str__(self):
        return f'{self._meta.verbose_name} #{self.pk}'
