from django.contrib import admin

from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "capacity", "status", "is_active")
    list_filter = ("status", "is_active")
    search_fields = ("number", "name")
    ordering = ("number",)

