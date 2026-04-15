from __future__ import annotations

from django.db import transaction
from rest_framework import generics, response, status
from rest_framework.views import APIView

from apps.menu.models import MenuItem

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


def _get_or_create_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class MyCartView(APIView):
    def get(self, request):
        cart = _get_or_create_cart(request.user)
        return response.Response(CartSerializer(cart).data)

    def patch(self, request):
        cart = _get_or_create_cart(request.user)
        ser = CartSerializer(instance=cart, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(CartSerializer(cart).data)

    def delete(self, request):
        cart = _get_or_create_cart(request.user)
        cart.items.all().delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class CartItemAddView(APIView):
    @transaction.atomic
    def post(self, request):
        cart = _get_or_create_cart(request.user)
        ser = CartItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        menu_item: MenuItem = ser.validated_data["menu_item"]
        qty = ser.validated_data["quantity"]

        if not menu_item.is_active or not menu_item.is_in_stock:
            return response.Response({"detail": "Ürün stokta yok veya aktif değil."}, status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item, defaults={"quantity": qty})
        if not created:
            item.quantity += qty
            item.save(update_fields=["quantity"])
        return response.Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemUpdateDeleteView(APIView):
    def patch(self, request, pk: int):
        cart = _get_or_create_cart(request.user)
        try:
            item = cart.items.get(pk=pk)
        except CartItem.DoesNotExist:
            return response.Response({"detail": "Sepet öğesi bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        ser = CartItemSerializer(instance=item, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        # only quantity is meaningful for patch
        qty = ser.validated_data.get("quantity", item.quantity)
        item.quantity = qty
        item.save(update_fields=["quantity"])
        return response.Response(CartSerializer(cart).data)

    def delete(self, request, pk: int):
        cart = _get_or_create_cart(request.user)
        deleted, _ = cart.items.filter(pk=pk).delete()
        if not deleted:
            return response.Response({"detail": "Sepet öğesi bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

