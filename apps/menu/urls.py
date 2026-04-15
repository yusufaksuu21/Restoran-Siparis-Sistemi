from django.urls import path

from . import views

app_name = "menu"

urlpatterns = [
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("items/", views.MenuItemListView.as_view(), name="item_list"),
    path("items/<int:pk>/", views.MenuItemDetailView.as_view(), name="item_detail"),
]

