from __future__ import annotations

from rest_framework import serializers

from .models import Category, MenuItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=Category.objects.all(), write_only=True)

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "category",
            "category_id",
            "name",
            "slug",
            "description",
            "price",
            "image_url",
            "is_promoted",
            "is_in_stock",
            "stock_qty",
        )

