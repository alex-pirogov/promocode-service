from uuid import UUID

from django.utils import timezone

from service.exceptions import (
    PromocodeExpiredError,
    PromocodeInactiveError,
    PromocodeInsufficientPlanError,
    PromocodeMaxActivationsError,
    PromocodeMaxUserActivationsError,
    PromocodeNewUserRequiredError,
    PromocodeSpecificUserRequiredError,
)
from service.models import Promocode, UserPromocodeUsage


def validate_promocode(
    promocode: Promocode,
    plan_id: int,
    user_id: UUID,
    is_new_user: bool,
    user_promocode_usage: UserPromocodeUsage | None = None,
) -> None:
    """
    `user_promocode_usage is None` when promocode has not been used by the user
    """

    if not promocode.is_active:
        raise PromocodeInactiveError()

    now = timezone.now()
    if now < promocode.active_from or now > promocode.active_to:
        raise PromocodeExpiredError()

    if (
        promocode.max_activations is not None
        and promocode.activations_count >= promocode.max_activations
    ):
        raise PromocodeMaxActivationsError()

    for p in promocode.plans.all():
        if p.pk == plan_id:
            break
    else:
        raise PromocodeInsufficientPlanError()

    if (
        promocode.max_user_activations is not None
        and user_promocode_usage
        and user_promocode_usage.activations_count >= promocode.max_user_activations
    ):
        raise PromocodeMaxUserActivationsError()

    if promocode.personal_for_user_id and user_id != promocode.personal_for_user_id:
        raise PromocodeSpecificUserRequiredError()

    if promocode.is_for_new_users and not is_new_user:
        raise PromocodeNewUserRequiredError()
