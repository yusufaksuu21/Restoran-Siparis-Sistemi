from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "table", "status", "subtotal", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "user__email", "note")
    inlines = [OrderItemInline]

