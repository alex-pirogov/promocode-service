from django.contrib import admin

from service.models import Promocode


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    pass
