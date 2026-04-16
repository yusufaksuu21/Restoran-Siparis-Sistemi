from __future__ import annotations
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from apps.cart.models import Cart, CartItem
from apps.menu.models import Category
from apps.tables.models import Table
from .forms import LoginForm, RegisterForm


class HomeView(TemplateView):
    template_name = "web/home.html"

    def get(self, request, *args, **kwargs):
        request.session.pop("guest_mode", None)
        if request.user.is_authenticated:
            return redirect("web:menu_list")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        context['register_form'] = RegisterForm()
        return context


class WebLoginView(LoginView):
    template_name = "web/auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class WebLogoutView(LogoutView):
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("web:home")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("web:home")
    next_url = request.POST.get("next") or request.GET.get("next")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Hesabınız oluşturuldu.")
            return redirect(next_url or "web:menu_list")
    else:
        form = RegisterForm()
    return render(request, "web/auth/register.html", {"form": form, "next": next_url})


def menu_view(request):
    if request.GET.get("guest") == "1":
        request.session["guest_mode"] = True

    table_id = request.GET.get("table")
    if table_id:
        request.session["table_id"] = int(table_id)

    is_guest_mode = request.session.get("guest_mode", False)
    if not request.user.is_authenticated and not is_guest_mode:
        tables = Table.objects.all().order_by("number")
        return render(request, "web/menu/entry.html", {"tables": tables})


    categories = Category.objects.filter(is_active=True).prefetch_related("items")

    if not categories.exists():
        from apps.menu.models import MenuItem
        from apps.menu.models import Category as MenuCategory
        demo_menu = {
            "Kebaplar": [
                {"name": "Adana Kebap", "description": "Zırh kıyması ile özel Adana.", "price": 350.00},
                {"name": "Urfa Kebap", "description": "Acısız, yumuşak lezzet.", "price": 340.00},
                {"name": "Beyti Sarma", "description": "Özel sos ve yoğurt eşliğinde.", "price": 390.00},
            ],
            "Yemekler": [
                {"name": "Pilav", "description": "Sade pilav.", "price": 150.00},
                {"name": "Kısır", "description": "Bulgur ve sebzelerle.", "price": 130.00},
                {"name": "Mercimek Köftesi", "description": "Mercimek ve bulgurla.", "price": 120.00},
                {"name": "Patates Kızartması", "description": "Kızarmış patates.", "price": 70.00},
                {"name": "Mevsim Salata", "description": "Taze sebzelerle.", "price": 100.00},
            ],
            "Çorbalar": [
                {"name": "Mercimek Çorbası", "description": "Süzme mercimek.", "price": 100.00},
                {"name": "Kelle Paça Çorbası", "description": "Bol sarımsaklı.", "price": 120.00},
            ],
            "Tatlılar": [
                {"name": "Sütlaç", "description": "Geleneksel sütlaç.", "price": 100.00},
                {"name": "Künefe", "description": "Kadayıf ve peynir ile.", "price": 120.00},
                {"name": "Baklava", "description": "Cevizli baklava.", "price": 110.00},
                {"name": "Trileçe", "description": "Üç katlı tatlı.", "price": 105.00},
            ],
            "İçecekler": [
                {"name": "Ayran", "description": "Bol köpüklü yayık ayran.", "price": 50.00},
                {"name": "Kola", "description": "Soğuk kutu içecek.", "price": 70.00},
                {"name": "Limonata", "description": "Taze sıkım limonata.", "price": 60.00},
                {"name": "Soda", "description": "Soğuk maden suyu.", "price": 40.00},
                {"name": "Çay", "description": "Sıcak çay.", "price": 0.00},
            ],
        }
        for cat_name, items in demo_menu.items():
            category, _ = MenuCategory.objects.get_or_create(
                name=cat_name, slug=cat_name.lower().replace(' ', '-')
            )
            for item_data in items:
                MenuItem.objects.get_or_create(
                    category=category,
                    slug=item_data['name'].lower().replace(' ', '-'),
                    defaults={
                        'name': item_data['name'],
                        'description': item_data['description'],
                        'price': item_data['price'],
                        'is_active': True,
                        'is_in_stock': True,
                        'stock_qty': 50,
                    }
                )
        categories = Category.objects.filter(is_active=True).prefetch_related("items")

    return render(request, "web/menu/list.html", {
        "is_authenticated": request.user.is_authenticated,
        "categories": categories,
    })


def menu_detail_view(request, pk: int):
    return render(request, "web/menu/detail.html", {"pk": pk})


def cart_view(request):
    from apps.menu.models import MenuItem
    if not request.user.is_authenticated:
        return redirect(f"/giris/?next=/sepet/")

    if request.method == "POST":
        action = request.POST.get("action")

        # Tek ürün sil
        if action == "remove":
            item_id = request.POST.get("item_id")
            CartItem.objects.filter(pk=item_id, cart__user=request.user).delete()
            messages.success(request, "Ürün sepetten kaldırıldı.")
            return redirect("web:cart")

        # Sepeti iptal et / temizle
        if action == "clear":
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart.items.all().delete()
            messages.success(request, "Sipariş iptal edildi.")
            return redirect("web:menu_list")

        # Ürün ekle
        menu_item_id = request.POST.get("menu_item_id")
        quantity = int(request.POST.get("quantity", 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        menu_item = MenuItem.objects.filter(pk=menu_item_id, is_active=True).first()
        if menu_item:
            item, created = CartItem.objects.get_or_create(
                cart=cart, menu_item=menu_item, defaults={"quantity": quantity}
            )
            if not created:
                item.quantity += quantity
                item.save()
            messages.success(request, f"✓ {menu_item.name} sepete eklendi!")
        else:
            messages.error(request, "Ürün bulunamadı!")
        # Menüde kal, sepete gitme
        return redirect("web:menu_list")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("menu_item").all()
    total = sum(item.menu_item.price * item.quantity for item in items)
    return render(request, "web/cart.html", {"cart_items": items, "total": total})


@login_required
def order_history_view(request):
    from apps.orders.models import Order
    orders = Order.objects.filter(user=request.user).prefetch_related("items__menu_item").order_by("-created_at")
    return render(request, "web/order_history.html", {"orders": orders})


@login_required
def cancel_order_view(request, pk: int):
    """Kullanıcı kendi PENDING siparişini iptal eder"""
    from apps.orders.models import Order
    if request.method == "POST":
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status == Order.Status.PENDING:
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])
            messages.success(request, f"Sipariş #{order.pk} iptal edildi.")
        else:
            messages.error(request, "Bu sipariş artık iptal edilemez.")
    return redirect("web:order_history")


@login_required
def profile_view(request):
    return render(request, "web/profile.html")


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    from apps.orders.models import Order
    pending_count = Order.objects.filter(status=Order.Status.PENDING).count()
    return render(request, "web/admin_dashboard.html", {"pending_count": pending_count})


@user_passes_test(lambda u: u.is_staff)
def order_management_view(request):
    from apps.orders.models import Order

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        
        if order_id and new_status:
            order = Order.objects.filter(id=order_id).first()
            if order and new_status in [Order.Status.CONFIRMED, Order.Status.PREPARING, Order.Status.SERVED]:
                if order.status not in [Order.Status.SERVED, Order.Status.CANCELLED]:
                    order.status = new_status
                    order.save(update_fields=["status"])
                    
                    # Sipariş onaylandığında/hazırlanıyor olursa ve masaya atanmışsa, masayı DOLU yap
                    if new_status in [Order.Status.CONFIRMED, Order.Status.PREPARING] and order.table:
                        if order.table.status != Table.Status.OCCUPIED:
                            order.table.status = Table.Status.OCCUPIED
                            order.table.save(update_fields=["status"])
                            messages.success(request, f"Sipariş #{order.pk} Masa {order.table.number} olarak işaretlendi.")
                    
                    # Sipariş servis edildiğinde masa durumunu kontrol et
                    if new_status == Order.Status.SERVED and order.table:
                        # Masanın başka aktif siparişi var mı kontrol et
                        active_orders = order.table.orders.filter(
                            status__in=[Order.Status.PENDING, Order.Status.CONFIRMED, Order.Status.PREPARING]
                        ).exclude(id=order.id)
                        if not active_orders.exists():
                            order.table.status = Table.Status.AVAILABLE
                            order.table.save(update_fields=["status"])
                    
                    if new_status != Order.Status.SERVED or not order.table:
                        messages.success(request, f"Sipariş #{order.pk} güncellendi.")
                else:
                    messages.error(request, "Bu siparişin durumu değiştirilemiyor.")
            else:
                messages.error(request, "Geçersiz durum.")
        return redirect("web:admin_orders")

    orders = Order.objects.all().prefetch_related("items__menu_item").order_by("-created_at")
    return render(request, "web/admin_orders.html", {"orders": orders})



@user_passes_test(lambda u: u.is_staff)
def table_management_view(request):
    from apps.orders.models import Order

    tables = Table.objects.prefetch_related('orders').all()
    for table in tables:
        active_orders = table.orders.filter(
            status__in=[
                Order.Status.PENDING,
                Order.Status.CONFIRMED,
                Order.Status.PREPARING,
            ]
        )
        table.active_orders = active_orders
        table.has_active_orders = active_orders.exists()

    return render(request, "web/admin_tables.html", {"tables": tables})


@user_passes_test(lambda u: u.is_staff)
def table_detail_view(request, table_id):
    from apps.orders.models import Order

    table = get_object_or_404(Table, id=table_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in [Table.Status.AVAILABLE, Table.Status.OCCUPIED, Table.Status.RESERVED, Table.Status.OUT_OF_SERVICE]:
            # Masayı boş yaparken siparişleri de temizle
            if new_status == Table.Status.AVAILABLE:
                orders = table.orders.all()
                order_count = orders.count()
                orders.delete()
                table.status = new_status
                table.save(update_fields=["status"])
                messages.success(request, f"Masa boşaltıldı. {order_count} sipariş silindi.")
            else:
                table.status = new_status
                table.save(update_fields=["status"])
                messages.success(request, f"Masa durumu '{table.get_status_display()}' olarak güncellendi.")
        return redirect("web:admin_table_detail", table_id=table_id)

    orders = table.orders.select_related('table').prefetch_related('items__menu_item').order_by('-created_at')
    return render(request, "web/admin_table_detail.html", {"table": table, "orders": orders})


@user_passes_test(lambda u: u.is_staff)
def table_clear_view(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    if request.method == "POST":
        table.status = Table.Status.AVAILABLE
        table.save(update_fields=["status"])
        messages.success(request, f"Masa {table.number} boşaltıldı.")
    return redirect("web:admin_tables")


@login_required
def checkout_view(request):
    from apps.orders.services import create_order_from_cart

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("menu_item").all()

    if not items.exists():
        return redirect("web:cart")

    table_id = request.session.get("table_id")
    table = None
    if table_id:
        from apps.tables.models import Table
        table = Table.objects.filter(id=table_id).first()

    if request.method == "POST":
        note = request.POST.get("note", "")
        order_type = request.POST.get("order_type", "DINE_IN")
        delivery_address = request.POST.get("delivery_address", "").strip()
        phone = request.POST.get("phone", "").strip()
        try:
            order = create_order_from_cart(
                cart=cart,
                note=note,
                order_type=order_type,
                delivery_address=delivery_address,
                phone=phone,
            )
            if table:
                order.table = table
                order.save(update_fields=["table"])
                # Masa durumunu dolu olarak işaretle
                if table.status == Table.Status.AVAILABLE:
                    table.status = Table.Status.OCCUPIED
                    table.save(update_fields=["status"])
            messages.success(request, "Siparişiniz alındı!")
            return redirect("web:order_history")
        except ValueError as e:
            messages.error(request, str(e))

    total = sum(item.menu_item.price * item.quantity for item in items)
    return render(request, "web/checkout.html", {"items": items, "total": total, "table": table})


@user_passes_test(lambda u: u.is_staff)
def kitchen_view(request):
    from apps.orders.models import Order
    from apps.tables.models import Table

    orders = Order.objects.filter(
        status__in=[Order.Status.PENDING, Order.Status.CONFIRMED, Order.Status.PREPARING]
    ).prefetch_related("items__menu_item").order_by("created_at")

    # Masa bazlı sipariş gruplandırması
    table_orders = {}
    other_orders = []

    for order in orders:
        if order.table:
            table_id = order.table.id
            if table_id not in table_orders:
                table_orders[table_id] = {
                    'table': order.table,
                    'orders': []
                }
            table_orders[table_id]['orders'].append(order)
        else:
            other_orders.append(order)

    # Tüm masaları al (sipariş olsun olmasın)
    all_tables = Table.objects.prefetch_related('orders').all()

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        table_id = request.POST.get("table_id")
        
        if order_id and new_status:
            order = Order.objects.filter(id=order_id).first()
            if order and new_status in [Order.Status.CONFIRMED, Order.Status.PREPARING, Order.Status.SERVED]:
                # Eğer masası yoksa ve masa seçildiyse, masayı ata
                if not order.table and table_id:
                    table = Table.objects.filter(id=table_id).first()
                    if table:
                        order.table = table
                        order.save(update_fields=["table"])
                        if table.status != Table.Status.OCCUPIED:
                            table.status = Table.Status.OCCUPIED
                            table.save(update_fields=["status"])
                        messages.success(request, f"Sipariş #{order.pk} → Masa {table.number}")
                
                order.status = new_status
                order.save(update_fields=["status"])
                messages.success(request, f"Sipariş #{order.pk} → {order.get_status_display()}")
        return redirect("web:kitchen")

    return render(request, "web/admin/kitchen.html", {
        "table_orders": table_orders,
        "other_orders": other_orders,
        "all_tables": all_tables,
        "orders": orders
    })