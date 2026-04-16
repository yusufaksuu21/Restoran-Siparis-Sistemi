from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from apps.web import views as web_views

urlpatterns = [
    path("", include(("apps.web.urls", "web"), namespace="web")),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/menu/", include("apps.menu.urls")),
    path("api/tables/", include("apps.tables.urls")),
    path("api/cart/", include("apps.cart.urls")),
    path("api/orders/", include("apps.orders.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)