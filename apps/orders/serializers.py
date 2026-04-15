from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from apps.menu.models import MenuItem
from apps.menu.serializers import MenuItemSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(source="menu_item", queryset=MenuItem.objects.all(), write_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "menu_item",
            "menu_item_id",
            "name_snapshot",
            "unit_price",
            "quantity",
            "line_total",
        )
        read_only_fields = ("name_snapshot", "unit_price", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "table", "status", "note", "subtotal", "items", "created_at")
        read_only_fields = ("status", "subtotal", "items", "created_at")


class CreateOrderSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)

