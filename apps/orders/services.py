from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(*, cart: Cart, note: str = "", order_type: str = "DINE_IN", 
                            delivery_address: str = "", phone: str = "") -> Order:
    cart = Cart.objects.select_for_update().select_related("table", "user").prefetch_related("items__menu_item").get(pk=cart.pk)
    items = list(cart.items.all())
    if not items:
        raise ValueError("Cart is empty")

    order = Order.objects.create(
        user=cart.user,
        table=cart.table,
        note=(note or "").strip(),
        status=Order.Status.PENDING,
        subtotal=Decimal("0.00"),
        order_type=order_type,
        delivery_address=delivery_address,
        phone=phone,
    )

    subtotal = Decimal("0.00")
    for ci in items:
        mi = ci.menu_item
        if not mi.is_active or not mi.is_in_stock:
            raise ValueError(f"Item not available: {mi.name}")
        
        oi = OrderItem.objects.create(
            order=order,
            menu_item=mi,
            name_snapshot=mi.name,
            unit_price=mi.price,
            quantity=ci.quantity,
        )
        subtotal += oi.line_total
        
        # Stok azalt
        if mi.stock_qty is not None:
            mi.stock_qty -= ci.quantity
            mi.save()

    order.subtotal = subtotal
    order.save(update_fields=["subtotal"])

    # clear cart
    cart.items.all().delete()
    return order

