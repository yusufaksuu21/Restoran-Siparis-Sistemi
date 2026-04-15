from __future__ import annotations

from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import os


class Table(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Boş"
        OCCUPIED = "OCCUPIED", "Dolu"
        RESERVED = "RESERVED", "Rezerve"
        OUT_OF_SERVICE = "OUT_OF_SERVICE", "Servis dışı"

    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=80, blank=True)
    capacity = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    is_active = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to="qr_codes/", null=True, blank=True)

    class Meta:
        ordering = ["number"]

    def __str__(self) -> str:
        label = f"Masa {self.number}"
        if self.name:
            label = f"{label} ({self.name})"
        return label
    
    def generate_qr_code(self):
        """Masa için QR kod üret"""
        # QR kodunun göstereceği URL
        qr_url = f"{settings.SITE_URL}/menu/?table={self.number}"
        
        # QR kod oluştur
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Dosya adı
        filename = f"table_{self.number}_qr.png"
        
        # BytesIO'ya kaydet
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        # Model'e kaydet
        self.qr_code.save(filename, ContentFile(img_io.getvalue()), save=False)
    
    def save(self, *args, **kwargs):
        # Yeni oluşturulan masa ise QR kod üret
        if not self.pk or not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

