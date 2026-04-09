from uuid import UUID

from service.exceptions import PromocodeNotFoundError
from service.models import Promocode, UserFirstUsage, UserPromocodeUsage

from .validate_promocode import validate_promocode


def check_promocode(code: str, plan_id: int, user_id: UUID) -> Promocode:
    try:
        promocode = Promocode.objects.prefetch_related('plans').get(code=code)
    except Promocode.DoesNotExist as ex:
        raise PromocodeNotFoundError() from ex

    user_promocode_usage = UserPromocodeUsage.objects.filter(
        promocode=promocode, user_id=user_id
    ).first()
    is_new_user = not UserFirstUsage.objects.filter(user_id=user_id).exists()

    validate_promocode(
        promocode=promocode,
        plan_id=plan_id,
        user_id=user_id,
        is_new_user=is_new_user,
        user_promocode_usage=user_promocode_usage,
    )

    return promocode
