from uuid import UUID

from django.db import transaction
from django.db.models import F

from service.exceptions import PromocodeNewUserRequiredError, PromocodeNotFoundError
from service.models import Promocode, PromocodeActivation, UserPromocodeUsage
from service.models.usage import UserFirstUsage

from .validate_promocode import validate_promocode


def activate_promocode(code: str, plan_id: int, user_id: UUID) -> PromocodeActivation:
    with transaction.atomic():
        try:
            promocode = (
                Promocode.objects.select_for_update().prefetch_related('plans').get(code=code)
            )
        except Promocode.DoesNotExist as ex:
            raise PromocodeNotFoundError() from ex

        user_promocode_usage, _ = UserPromocodeUsage.objects.select_for_update().get_or_create(
            promocode=promocode, user_id=user_id
        )
        is_new_user = not UserFirstUsage.objects.filter(user_id=user_id).exists()

        validate_promocode(
            promocode=promocode,
            plan_id=plan_id,
            user_id=user_id,
            is_new_user=is_new_user,
            user_promocode_usage=user_promocode_usage,
        )

        _, created = UserFirstUsage.objects.get_or_create(user_id=user_id)
        if promocode.is_for_new_users and not created:
            raise PromocodeNewUserRequiredError()

        UserPromocodeUsage.objects.filter(pk=user_promocode_usage.pk).update(
            activations_count=F('activations_count') + 1
        )

        Promocode.objects.filter(pk=promocode.pk).update(
            activations_count=F('activations_count') + 1
        )

        return PromocodeActivation.objects.create(
            promocode=promocode, user_id=user_id, plan_id=plan_id
        )
