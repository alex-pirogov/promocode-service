from django.contrib import admin

from service.models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    pass
