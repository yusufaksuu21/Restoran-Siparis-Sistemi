from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    image_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)  # kampanyalı ürün etiketi

    is_in_stock = models.BooleanField(default=True)  # stokta yok durumu
    stock_qty = models.PositiveIntegerField(null=True, blank=True)
    
    preparation_time = models.PositiveIntegerField(default=15)  # dakika cinsinden
    allergens = models.CharField(max_length=300, blank=True)  # örn: "Gluten, Fıstık"
    calories = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["category", "slug"], name="uniq_menuitem_category_slug"),
        ]
        ordering = ["category__sort_order", "category__name", "name"]

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        # Stok 0 oluğunda is_in_stock otomatik False yap
        if self.stock_qty is not None and self.stock_qty <= 0:
            self.is_in_stock = False
        elif self.stock_qty is not None and self.stock_qty > 0:
            self.is_in_stock = True
        super().save(*args, **kwargs)

