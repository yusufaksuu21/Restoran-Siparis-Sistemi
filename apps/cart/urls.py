from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.MyCartView.as_view(), name="my_cart"),
    path("items/", views.CartItemAddView.as_view(), name="item_add"),
    path("items/<int:pk>/", views.CartItemUpdateDeleteView.as_view(), name="item_update_delete"),
]

