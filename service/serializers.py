from rest_framework import serializers

from .models import Plan, Promocode, PromocodeActivation


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'


class ActivatedPromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = ('id', 'code', 'bonus_type', 'value')


class PromocodeActivationSerializer(serializers.ModelSerializer):
    promocode = ActivatedPromocodeSerializer(read_only=True)

    class Meta:
        model = PromocodeActivation
        fields = '__all__'


class CheckPromocodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)
    plan_id = serializers.IntegerField()
    user_id = serializers.UUIDField()

    def validate_code(self, value: str) -> str:
        return value.strip().upper()


ActivatePromocodeSerializer = CheckPromocodeSerializer


class CheckPromocodeResultSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
    error_code = serializers.CharField(required=False)
    promocode = ActivatedPromocodeSerializer(read_only=True)
