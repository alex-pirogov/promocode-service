from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, status, viewsets
from rest_framework.request import Request

from service.services import activate_promocode, check_promocode

from .exceptions import PromocodeError
from .models import Plan, Promocode, PromocodeActivation
from .serializers import (
    ActivatePromocodeSerializer,
    CheckPromocodeResultSerializer,
    CheckPromocodeSerializer,
    PlanSerializer,
    PromocodeActivationSerializer,
    PromocodeSerializer,
)


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class PromocodeViewSet(viewsets.ModelViewSet):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer


class PromocodeActivationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = PromocodeActivation.objects.all()
    serializer_class = PromocodeActivationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['promocode', 'user_id']


class CheckPromocodeView(generics.GenericAPIView):
    serializer_class = CheckPromocodeSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            promocode = check_promocode(
                code=serializer.validated_data['code'],
                plan_id=serializer.validated_data['plan_id'],
                user_id=serializer.validated_data['user_id'],
            )
            data = CheckPromocodeResultSerializer({'valid': True, 'promocode': promocode}).data
            return JsonResponse(data)
        except PromocodeError as ex:
            data = CheckPromocodeResultSerializer({'valid': False, 'error_code': ex.code}).data
            return JsonResponse(data, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ActivatePromocodeView(generics.GenericAPIView):
    serializer_class = ActivatePromocodeSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            activation = activate_promocode(
                code=serializer.validated_data['code'],
                plan_id=serializer.validated_data['plan_id'],
                user_id=serializer.validated_data['user_id'],
            )
            return JsonResponse(PromocodeActivationSerializer(activation).data)
        except PromocodeError as ex:
            return JsonResponse(
                {'error': True, 'error_code': ex.code}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
