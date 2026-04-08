from django.contrib import admin

from service.models import PromocodeActivation


@admin.register(PromocodeActivation)
class PromocodeActivationAdmin(admin.ModelAdmin):
    pass
