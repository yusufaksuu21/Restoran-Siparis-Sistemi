from __future__ import annotations

from rest_framework import serializers

from apps.menu.models import MenuItem
from apps.menu.serializers import MenuItemSerializer
from apps.tables.models import Table

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(source="menu_item", queryset=MenuItem.objects.all(), write_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "menu_item", "menu_item_id", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    table_id = serializers.PrimaryKeyRelatedField(source="table", queryset=Table.objects.all(), allow_null=True, required=False, write_only=True)
    table = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "table", "table_id", "items", "updated_at")

    def get_table(self, obj):
        if not obj.table_id:
            return None
        return {"id": obj.table_id, "number": obj.table.number, "status": obj.table.status}

