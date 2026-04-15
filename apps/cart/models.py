from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.menu.models import MenuItem
from apps.tables.models import Table


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name="carts")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart({self.user_id})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "menu_item"], name="uniq_cart_menu_item"),
        ]

    def __str__(self) -> str:
        return f"{self.menu_item} x{self.quantity}"

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity

