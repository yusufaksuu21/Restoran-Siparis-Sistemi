from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.MyOrdersView.as_view(), name="my_orders"),
    path("create/", views.CreateOrderView.as_view(), name="create"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
    path("<int:pk>/cancel/", views.CancelOrderView.as_view(), name="cancel"),
    path("<int:pk>/status/", views.UpdateOrderStatusView.as_view(), name="status_update"),
    path("reports/daily-sales/", views.DailySalesReportView.as_view(), name="daily_sales_report"),
    path("reports/top-sellers/", views.TopSellersView.as_view(), name="top_sellers"),
    path("reports/dashboard-stats/", views.DashboardStatsView.as_view(), name="dashboard_stats"),
]

