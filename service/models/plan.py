from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Plan'

    def __str__(self):
        return f'{self._meta.verbose_name} «{self.name}»'
