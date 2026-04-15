# Restoran Sipariş Sistemi

Bu proje, bir restoran için Django tabanlı tam işlevsel bir sipariş uygulamasıdır. İçinde:

- Kullanıcı kayıt/giriş ve yönetici rolleri
- Menü, sepet, ödeme ve sipariş geçmişi
- Yönetici paneli ve mutfak sipariş takibi
- Masa ve QR kod destekli masada sipariş
- `config/settings/` içinde `base`, `dev`, `prod` yapılandırması

## Gereksinimler

- Python 3.11 veya 3.13
- `pip` ve `virtualenv`

## Kurulum

1. Proje klasörüne girin:

```bash
cd "Restoran Sipariş Sistemi"
```

2. Sanal ortam oluşturun ve aktif edin:

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Paketleri yükleyin:

```bash
pip install -r requirements.txt
```

4. Ortam dosyasını oluşturun:

```bash
copy .env.example .env
```

5. Veritabanı ayarlarını `.env` içinde gerektiği şekilde güncelleyin.

6. Migration çalıştırın:

```bash
python manage.py migrate
```

7. Yönetici hesabı oluşturun:

```bash
python manage.py createsuperuser
```

8. Geliştirme sunucusunu başlatın:

```bash
python manage.py runserver
```

## Proje kullanımı

- `http://127.0.0.1:8000/` — site ana sayfası
- `http://127.0.0.1:8000/giris/` — kullanıcı girişi
- `http://127.0.0.1:8000/yonetim/` — yönetim paneli
- `http://127.0.0.1:8000/admin/` — Django admin paneli

## GitHub'a yükleme

Yeni bir GitHub deposu oluşturduktan sonra şu adımları izleyin:

```bash
git init
git add .
git commit -m "Initial commit"
```

GitHub üzerinde boş bir repo oluşturduktan sonra uzak bağlantıyı ekleyin:

```bash
git remote add origin https://github.com/<kullaniciadi>/<repo-ismi>.git
```

Ana dalı gönderin:

```bash
git branch -M main
git push -u origin main
```

> Not: `.env` dosyası `.gitignore` içinde listelenmiştir. Bu yüzden gizli bilgileri GitHub'a göndermeyin.

## Öneriler

- Projeyi GitHub'a göndermeden önce `git status` ile değişiklikleri kontrol edin.
- Eğer farklı bir dal kullanmak isterseniz `main` yerine başka bir dal adı seçebilirsiniz.
- Yerel olarak her şey çalıştığında GitHub sayfasındaki `Actions` veya `Settings` ek yapılandırmaya gerek yok.

