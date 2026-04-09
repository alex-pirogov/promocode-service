from django.urls import include, path
from rest_framework import routers

from .views import (
    ActivatePromocodeView,
    CheckPromocodeView,
    PlanViewSet,
    PromocodeActivationViewSet,
    PromocodeViewSet,
)

router = routers.DefaultRouter()
router.register(r'promocodes', PromocodeViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'activations', PromocodeActivationViewSet)


urlpatterns = [
    path('promocodes/check/', CheckPromocodeView.as_view()),
    path('promocodes/activate/', ActivatePromocodeView.as_view()),
    path('', include(router.urls)),
]
