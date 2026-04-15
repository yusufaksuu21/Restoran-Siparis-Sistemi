# Django REST API - Restoran Sipariş Sistemi
# Özelliklerin Uygulanması ve Migration Adımları

## Özellikleri Kontrol Listesi

✓ 1. QR KOD SİSTEMİ (MASADA SİPARİŞ)
   - apps/tables/models.py: qr_code ImageField eklendi
   - QR kod otomatik üretimi: generate_qr_code() method
   - QR kod URL formatı: /menu/?table=<masa_no>
   - menu_view: masa numarasını session'a kaydedildi

✓ 2. ONLINE SİPARİŞ (PAKET SERVİS)
   - Order model: order_type (DINE_IN/TAKEAWAY/DELIVERY)
   - Order model: delivery_address, phone, estimated_time
   - checkout_view: yeni view eklendi
   - templates/web/checkout.html: dinamik form

✓ 3. GERÇEK ZAMANLI SİPARİŞ TAKİBİ
   - order_history.html: sipariş durumu progress bar
   - JavaScript setInterval: 30 saniye otomatik yenileme
   - Renkli durum göstergesi

✓ 4. MUTFAK PANELİ
   - kitchen_view: PENDING ve PREPARING siparişlerini gösterir
   - templates/web/admin/kitchen.html
   - Durum güncelleme butonları
   - 20 saniye otomatik yenileme

✓ 5. MENÜ GELİŞTİRME
   - MenuItem: preparation_time (dakika)
   - MenuItem: allergens (string)
   - MenuItem: calories (kcal)
   - templates/web/menu/detail.html: detay sayfası

✓ 6. STOK YÖNETİMİ
   - MenuItem.save(): stock_qty <= 0 iken is_in_stock = False
   - create_order_from_cart: sipariş verilince stock_qty azaltılıyor
   - admin_dashboard.html: stok uyarısı kartı

✓ 7. ADMIN PANEL GELİŞTİRME
   - admin_dashboard.html: KPI kartları, istatistikler, stok uyarısı
   - admin_orders.html: durum filtresi, table görüntüsü
   - templates/web/admin/kitchen.html

✓ 8. KULLANICI PROFİLİ
   - templates/web/profile.html: kullanıcı bilgileri, sipariş istatistikleri
   - Son 5 sipariş listesi

## Gerekli Migration Komutları

# 1. Model değişiklikleri için migration oluştur
python manage.py makemigrations

# 2. Menu uygulaması için migration (MenuItem yeni alanlar)
python manage.py makemigrations menu

# 3. Tables uygulaması için migration (Table qr_code field)
python manage.py makemigrations tables

# 4. Orders uygulaması için migration (Order yeni alanlar)
python manage.py makemigrations orders

# 5. Tüm migration'ları uygula
python manage.py migrate

# 6. Media klasörünü oluştur (QR kodlar için)
mkdir -p media/qr_codes

## Eklenmiş Dependencies

requirements.txt:
- qrcode[pil]==8.0
- Pillow==11.0.0

Kurulumu:
pip install -r requirements.txt

## .env Ayarları

Aşağıdaki ayarı .env dosyasına ekleyin:
SITE_URL=http://localhost:8000  # Production için domain adresini yazın

## Yapılan Değişiklikler - Detay

### 1. Models
- apps/menu/models.py: MenuItem modeline yeni alanlar ve save() override
- apps/tables/models.py: Table modeline qr_code ve generate_qr_code() method
- apps/orders/models.py: Order modeline order_type ve teslimat bilgileri

### 2. Services
- apps/orders/services.py: create_order_from_cart stok yönetimi eklendi

### 3. Views
- apps/web/views.py: 
  - menu_view: masa numarası session'a kaydedildi
  - checkout_view: yeni view
  - kitchen_view: mutfak paneli

### 4. URLs
- apps/web/urls.py: 
  - path("odenme/", checkout_view)
  - path("mutfak/", kitchen_view)

### 5. Templates (Yeni/Güncellenmiş)
- templates/web/menu/detail.html: Ürün detay (güncellendi)
- templates/web/checkout.html: Ödeme formu (yeni)
- templates/web/admin/kitchen.html: Mutfak paneli (yeni)
- templates/web/order_history.html: Sipariş takibi (güncellendi)
- templates/web/admin_dashboard.html: Admin dashboard (güncellendi)
- templates/web/admin_orders.html: Order yönetimi (güncellendi)
- templates/web/admin_tables.html: Masa yönetimi (güncellendi)
- templates/web/profile.html: Kullanıcı profili (güncellendi)

### 6. Settings
- config/settings/base.py: SITE_URL ayarı eklendi

## Test Adımları

1. **QR Kod Oluşturma Testi:**
   ```
   python manage.py shell
   from apps.tables.models import Table
   table = Table.objects.create(number=1, capacity=4)
   # QR kod otomatik oluşturulmalı
   ```

2. **Sipariş Oluşturma Testi:**
   ```
   # Admin panelinden: /yonetim/
   # Checkout'tan sipariş ver
   # İstatistikler güncellenmelidir
   ```

3. **Mutfak Paneli Testi:**
   ```
   # /mutfak/ adresine gidin (staff hesapla)
   # Siparişleri görüp durum güncelleyin
   ```

4. **QR Kod Oku Testi:**
   ```
   # Admin Masa Yönetimi'nden QR kodu indirin
   # QR kod okuyucu ile oku
   # /menu/?table=1 açılmalı
   # Masa numarası session'da kaydedilmeli
   ```

## Notlar

- Tüm yeni view'lar middleware ile korunmaktadır (login_required, user_passes_test)
- CSS class'ları mevcut app.css ile uyumludur
- Tüm template'ler responsive tasarım kullanmaktadır
- JavaScript auto-refresh özelliği browser tarafından uygulanmaktadır
