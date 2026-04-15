from __future__ import annotations

from rest_framework import generics, permissions

from apps.accounts.permissions import IsStaffRole

from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer


class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class MenuItemListView(generics.ListCreateAPIView):
    """
    Public list supports:
    - ürün arama: ?q=
    - kategori filtreleme: ?category=<slug>
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffRole()]
        return [permissions.AllowAny()]

    serializer_class = MenuItemSerializer

    def get_queryset(self):
        qs = MenuItem.objects.select_related("category").filter(is_active=True, category__is_active=True)
        q = (self.request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        category_slug = (self.request.query_params.get("category") or "").strip()
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        promoted = (self.request.query_params.get("promoted") or "").strip().lower()
        if promoted in ("1", "true", "yes"):
            qs = qs.filter(is_promoted=True)
        in_stock = (self.request.query_params.get("in_stock") or "").strip().lower()
        if in_stock in ("0", "false", "no"):
            qs = qs.filter(is_in_stock=False)
        elif in_stock in ("1", "true", "yes"):
            qs = qs.filter(is_in_stock=True)
        return qs


class MenuItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsStaffRole()]
        return [permissions.AllowAny()]

