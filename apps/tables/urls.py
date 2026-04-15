from django.urls import path

from . import views

app_name = "tables"

urlpatterns = [
    path("", views.TableListCreateView.as_view(), name="list_create"),
    path("<int:pk>/", views.TableDetailView.as_view(), name="detail"),
]

