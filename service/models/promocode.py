from django.core.validators import RegexValidator
from django.db import models

from .plan import Plan

promocode_validator = RegexValidator(
    regex=r'^[A-Z0-9]{6,12}$',
    message='promocode must be 6–12 characters long and contain only uppercase letters and digits',
)


class Promocode(models.Model):
    code = models.CharField(max_length=32, unique=True, validators=[promocode_validator])

    class BonusTypeChoices(models.TextChoices):
        PERCENT_DISCOUNT = 'percent_discount'
        AMOUNT_DISCOUNT = 'amount_discount'
        DAYS = 'days'
        BALANCE = 'balance'

    bonus_type = models.CharField(max_length=32, choices=BonusTypeChoices.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(db_default=True)
    active_from = models.DateTimeField()
    active_to = models.DateTimeField()
    plans = models.ManyToManyField(to=Plan, blank=True, related_name='promocodes')

    activations_count = models.PositiveIntegerField(db_default=0, editable=False)
    max_activations = models.PositiveIntegerField(blank=True, null=True)
    max_user_activations = models.PositiveIntegerField(blank=True, null=True)

    personal_for_user_id = models.UUIDField(blank=True, null=True)
    is_for_new_users = models.BooleanField()

    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Promocode'

    def __str__(self):
        return f'{self._meta.verbose_name} {self.code}'
