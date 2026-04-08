from datetime import timedelta
from typing import Any
from uuid import uuid4

from django.test import TestCase
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
from service.models import Plan, Promocode, UserPromocodeUsage

from .validate_promocode import validate_promocode

PLAN_ID = 1
PROMOCODE_ID = 1
USER_ID = uuid4()


class PromocodeTestCase(TestCase):
    def create_plan(self, **overrides: Any):
        self.plan = Plan.objects.create(**{'id': PLAN_ID, 'name': 'Lite', **overrides})
        return self.plan

    def create_promocode(self, **overrides: Any):
        now = timezone.now()
        plans = overrides.pop('plans', None)
        promocode = Promocode.objects.create(
            **{
                'id': PROMOCODE_ID,
                'code': 'PROMO1',
                'bonus_type': Promocode.BonusTypeChoices.PERCENT_DISCOUNT,
                'value': 3,
                'is_active': True,
                'active_from': now - timedelta(days=1),
                'active_to': now + timedelta(days=1),
                'activations_count': 0,
                'max_activations': None,
                'max_user_activations': None,
                'personal_for_user_id': None,
                'is_for_new_users': False,
                **overrides,
            }
        )
        promocode.plans.set(plans if plans is not None else [self.plan])
        self.promocode = Promocode.objects.prefetch_related('plans').get(pk=promocode.pk)
        return self.promocode

    user_promocode_usage = None

    def create_user_promocode_usage(self, **overrides: Any):
        self.user_promocode_usage = UserPromocodeUsage.objects.create(
            **{'promocode': self.promocode, 'user_id': USER_ID, **overrides}
        )
        return self.user_promocode_usage

    def call_validate_promocode(self, **overrides: Any):
        validate_promocode(
            **{
                'promocode': self.promocode,
                'plan_id': self.plan.pk,
                'user_id': USER_ID,
                'is_new_user': True,
                'user_promocode_usage': self.user_promocode_usage,
                **overrides,
            }
        )


class TestValidatePromocodeActive(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_inactive_raises(self):
        self.create_promocode(is_active=False)
        with self.assertRaises(PromocodeInactiveError):
            self.call_validate_promocode()

    def test_active_passes(self):
        self.create_promocode(is_active=True)
        self.call_validate_promocode()


class TestValidatePromocodeExpiry(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_not_started_raises(self):
        now = timezone.now()
        self.create_promocode(active_from=now + timedelta(seconds=1))
        with self.assertRaises(PromocodeExpiredError):
            self.call_validate_promocode()

    def test_already_expired_raises(self):
        now = timezone.now()
        self.create_promocode(active_to=now - timedelta(seconds=1))
        with self.assertRaises(PromocodeExpiredError):
            self.call_validate_promocode()

    def test_within_range_passes(self):
        now = timezone.now()
        self.create_promocode(
            active_from=now - timedelta(hours=1),
            active_to=now + timedelta(hours=1),
        )
        self.call_validate_promocode()


class TestValidatePromocodeMaxActivations(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_limit_reached_raises(self):
        self.create_promocode(max_activations=10, activations_count=10)
        with self.assertRaises(PromocodeMaxActivationsError):
            self.call_validate_promocode()

    def test_over_limit_raises(self):
        self.create_promocode(max_activations=10, activations_count=11)
        with self.assertRaises(PromocodeMaxActivationsError):
            self.call_validate_promocode()

    def test_under_limit_passes(self):
        self.create_promocode(max_activations=10, activations_count=9)
        self.call_validate_promocode()

    def test_no_limit_passes(self):
        self.create_promocode(max_activations=None, activations_count=999)
        self.call_validate_promocode()


class TestValidatePromocodePlan(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_wrong_plan_raises(self):
        self.create_promocode(plans=[self.plan])
        with self.assertRaises(PromocodeInsufficientPlanError):
            self.call_validate_promocode(plan_id=PLAN_ID + 1)

    def test_correct_plan_passes(self):
        self.create_promocode(plans=[self.plan])
        self.call_validate_promocode(plan_id=PLAN_ID)

    def test_correct_plan_among_many_passes(self):
        plan1 = self.plan
        plan2 = self.create_plan(id=2)

        self.create_promocode(plans=[plan1, plan2])
        self.call_validate_promocode(plan_id=plan1.pk)

    def test_empty_plans_raises(self):
        self.create_promocode(plans=[])
        with self.assertRaises(PromocodeInsufficientPlanError):
            self.call_validate_promocode()


class TestValidatePromocodeMaxUserActivations(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_limit_reached_raises(self):
        self.create_promocode(max_user_activations=3)
        self.create_user_promocode_usage(activations_count=3)
        with self.assertRaises(PromocodeMaxUserActivationsError):
            self.call_validate_promocode()

    def test_under_limit_passes(self):
        self.create_promocode(max_user_activations=3)
        self.create_user_promocode_usage(activations_count=2)
        self.call_validate_promocode()

    def test_no_prior_usage_passes(self):
        self.create_promocode(max_user_activations=1)
        self.call_validate_promocode()

    def test_no_limit_passes(self):
        self.create_promocode(max_user_activations=None)
        self.create_user_promocode_usage(activations_count=9999)
        self.call_validate_promocode()


class TestValidatePromocodePersonal(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_different_user_raises(self):
        owner = uuid4()
        self.create_promocode(personal_for_user_id=owner)
        with self.assertRaises(PromocodeSpecificUserRequiredError):
            self.call_validate_promocode(user_id=uuid4())

    def test_correct_user_passes(self):
        owner = uuid4()
        self.create_promocode(personal_for_user_id=owner)
        self.call_validate_promocode(user_id=owner)

    def test_not_personal_any_user_passes(self):
        self.create_promocode(personal_for_user_id=None)
        self.call_validate_promocode(user_id=uuid4())


class TestValidatePromocodeNewUsers(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_existing_user_raises(self):
        self.create_promocode(is_for_new_users=True)
        with self.assertRaises(PromocodeNewUserRequiredError):
            self.call_validate_promocode(is_new_user=False)

    def test_new_user_passes(self):
        self.create_promocode(is_for_new_users=True)
        self.call_validate_promocode(is_new_user=True)

    def test_not_restricted_existing_user_passes(self):
        self.create_promocode(is_for_new_users=False)
        self.call_validate_promocode(is_new_user=False)


class TestValidatePromocodeHappyPath(PromocodeTestCase):
    def setUp(self):
        self.create_plan()

    def test_all_constraints_satisfied_passes(self):
        owner = uuid4()
        self.create_promocode(
            max_activations=100,
            activations_count=50,
            max_user_activations=5,
            personal_for_user_id=owner,
            is_for_new_users=True,
        )
        self.create_user_promocode_usage(user_id=owner, activations_count=2)
        self.call_validate_promocode(user_id=owner, is_new_user=True)
