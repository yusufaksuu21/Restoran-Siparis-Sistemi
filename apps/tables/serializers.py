from __future__ import annotations

from rest_framework import serializers

from .models import Table


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ("id", "number", "name", "capacity", "status", "is_active")

