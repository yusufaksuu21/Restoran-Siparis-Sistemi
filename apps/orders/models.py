from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.menu.models import MenuItem
from apps.tables.models import Table


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Beklemede"
        CONFIRMED = "CONFIRMED", "Onaylandı"
        PREPARING = "PREPARING", "Hazırlanıyor"
        SERVED = "SERVED", "Servis edildi"
        CANCELLED = "CANCELLED", "İptal"
    
    class OrderType(models.TextChoices):
        DINE_IN = "DINE_IN", "Masada"
        TAKEAWAY = "TAKEAWAY", "Paket Servis"
        DELIVERY = "DELIVERY", "Adrese Sipariş"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    note = models.CharField(max_length=500, blank=True)  # sipariş notu
    
    # Online sipariş alanları
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.DINE_IN)
    delivery_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    estimated_time = models.PositiveIntegerField(null=True, blank=True)  # dakika cinsinden

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name="order_items")
    name_snapshot = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "menu_item"], name="uniq_order_menu_item"),
        ]

    def save(self, *args, **kwargs):
        self.line_total = (self.unit_price or Decimal("0.00")) * Decimal(self.quantity or 0)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name_snapshot} x{self.quantity}"

