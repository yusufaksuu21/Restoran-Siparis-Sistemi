from __future__ import annotations

from datetime import date

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView

from apps.accounts.permissions import IsStaffRole
from apps.cart.models import Cart

from .models import Order, OrderItem
from .serializers import (
    CreateOrderSerializer,
    OrderSerializer,
    UpdateOrderStatusSerializer,
)
from .services import create_order_from_cart


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("table")
            .prefetch_related("items__menu_item", "items")
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.select_related("table").prefetch_related("items__menu_item", "items")
        if getattr(self.request.user, "role", None) in ("ADMIN", "WAITER"):
            return qs
        return qs.filter(user=self.request.user)


class CreateOrderView(APIView):
    def post(self, request):
        ser = CreateOrderSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            order = create_order_from_cart(cart=cart, note=ser.validated_data.get("note", ""))
        except ValueError as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    """sipariş iptal özelliği (müşteri: sadece PENDING; staff: her zaman iptal edebilir)"""

    def post(self, request, pk: int):
        qs = Order.objects.all()
        if getattr(request.user, "role", None) not in ("ADMIN", "WAITER"):
            qs = qs.filter(user=request.user)
        try:
            order = qs.get(pk=pk)
        except Order.DoesNotExist:
            return response.Response({"detail": "Sipariş bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        is_staff_role = getattr(request.user, "role", None) in ("ADMIN", "WAITER")
        if not is_staff_role and order.status != Order.Status.PENDING:
            return response.Response({"detail": "Bu sipariş artık iptal edilemez."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        return response.Response(OrderSerializer(order).data)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsStaffRole]

    def post(self, request, pk: int):
        ser = UpdateOrderStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return response.Response({"detail": "Sipariş bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
        order.status = ser.validated_data["status"]
        order.save(update_fields=["status"])
        return response.Response(OrderSerializer(order).data)


class DailySalesReportView(APIView):
    permission_classes = [IsStaffRole]

    def get(self, request):
        # default: today
        today = now().date()
        start = request.query_params.get("date")
        report_date = today
        if start:
            try:
                report_date = date.fromisoformat(start)
            except ValueError:
                return response.Response({"detail": "Geçersiz tarih formatı. YYYY-MM-DD kullanın."}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(created_at__date=report_date, status__in=[Order.Status.CONFIRMED, Order.Status.PREPARING, Order.Status.SERVED])
        totals = orders.aggregate(revenue=Sum("subtotal"), count=Count("id"))
        return response.Response(
            {
                "date": report_date.isoformat(),
                "order_count": totals["count"] or 0,
                "revenue": str(totals["revenue"] or 0),
            }
        )


class TopSellersView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", "10") or "10")
        limit = max(1, min(limit, 50))
        qs = (
            OrderItem.objects.filter(order__status__in=[Order.Status.CONFIRMED, Order.Status.PREPARING, Order.Status.SERVED])
            .values("menu_item_id", "name_snapshot")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")[:limit]
        )
        return response.Response({"items": list(qs)})


class DashboardStatsView(APIView):
    permission_classes = [IsStaffRole]

    def get(self, request):
        today = now().date()
        by_status = (
            Order.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        revenue_today = (
            Order.objects.filter(created_at__date=today, status__in=[Order.Status.CONFIRMED, Order.Status.PREPARING, Order.Status.SERVED])
            .aggregate(revenue=Sum("subtotal"))
            .get("revenue")
            or 0
        )
        return response.Response(
            {
                "date": today.isoformat(),
                "orders_by_status": list(by_status),
                "revenue_today": str(revenue_today),
            }
        )

