from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("giris/", views.WebLoginView.as_view(), name="login"),
    path("cikis/", views.WebLogoutView.as_view(), name="logout"),
    path("kayit/", views.register_view, name="register"),
    path("menu/", views.menu_view, name="menu_list"),
    path("menu/<int:pk>/", views.menu_detail_view, name="menu_detail"),
    path("sepet/", views.cart_view, name="cart"),
    path("odenme/", views.checkout_view, name="checkout"),
    path("siparisler/", views.order_history_view, name="order_history"),
    path("siparisler/<int:pk>/iptal/", views.cancel_order_view, name="cancel_order"),
    path("profil/", views.profile_view, name="profile"),
    path("yonetim/", views.admin_dashboard_view, name="admin_dashboard"),
    path("yonetim/siparisler/", views.order_management_view, name="admin_orders"),
    path("yonetim/masalar/", views.table_management_view, name="admin_tables"),
    path("mutfak/", views.kitchen_view, name="kitchen"),
]