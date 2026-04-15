from __future__ import annotations

from rest_framework import generics, permissions

from apps.accounts.permissions import IsStaffRole

from .models import Table
from .serializers import TableSerializer


class TableListCreateView(generics.ListCreateAPIView):
    serializer_class = TableSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffRole()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = Table.objects.all()
        active = (self.request.query_params.get("active") or "").strip().lower()
        if active in ("1", "true", "yes"):
            qs = qs.filter(is_active=True)
        return qs


class TableDetailView(generics.RetrieveUpdateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsStaffRole()]
        return [permissions.AllowAny()]

