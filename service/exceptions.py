class PromocodeError(Exception):
    code = 'promocode_error'


class PromocodeNotFoundError(PromocodeError):
    code = 'not_found'


class PromocodeInactiveError(PromocodeError):
    code = 'inactive'


class PromocodeExpiredError(PromocodeError):
    code = 'expired'


class PromocodeMaxActivationsError(PromocodeError):
    code = 'max_activations_reached'


class PromocodeInsufficientPlanError(PromocodeError):
    code = 'plan_insufficient'


class PromocodeMaxUserActivationsError(PromocodeError):
    code = 'max_user_activations_reached'


class PromocodeSpecificUserRequiredError(PromocodeError):
    code = 'specific_user_required'


class PromocodeNewUserRequiredError(PromocodeError):
    code = 'new_user_required'
