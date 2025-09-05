from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone  # ← ADD 
import uuid
from django.contrib.auth import get_user_model
from django.contrib import admin
User = get_user_model()

class Payment(models.Model):
    KIND_CHOICES = [
        ("one_time", "One-time"),
        ("subscription", "Subscription"),
    ]
    GATEWAY_CHOICES = [
        ("chapa", "Chapa"),
        ("telebirr", "TeleBirr"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="ETB")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="one_time")
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)

    tx_ref = models.CharField(max_length=64, unique=True)  # idempotent key per attempt
    provider_txn_id = models.CharField(max_length=128, blank=True)  # returned by gateway

    purpose = models.CharField(max_length=64)  # e.g. "premium_monthly", "commission_order:123"
    meta = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    raw_init = models.JSONField(default=dict, blank=True)      # store init api response
    raw_webhook = models.JSONField(default=dict, blank=True)   # last webhook payload
    raw_verify = models.JSONField(default=dict, blank=True)    # last verify response

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["tx_ref"])]

    def __str__(self):
        return f"{self.gateway}:{self.tx_ref}:{self.status}:{self.amount}{self.currency}"
class UserTier(models.Model):
    TIER_CHOICES = (
        ('standard', 'Standard User'),
        ('wholesale', 'Wholesale User'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='standard')
    is_paid = models.BooleanField(default=False)
    paid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_tier_display()}"



# =======================
# ==== 1. Core Models ====
# =======================

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = _("Categories")
    
    def __str__(self):
        return self.name

class Product(models.Model):
    CONDITION_CHOICES = [
        ('New', _('Brand New')),
        ('Used', _('Used')),
        ('Refurbished', _('Refurbished')),
    ]
  
    name = models.CharField(max_length=200, verbose_name=_("Product Name"))
    description = models.TextField(verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price (in Birr)"))
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False, verbose_name=_("Category"))
    brand = models.CharField(max_length=100, blank=True, verbose_name=_("Brand"))
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, blank=True, verbose_name=_("Condition"))
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Seller"))
    created_at = models.DateTimeField(auto_now_add=True)

    # --- New fields for wholesale functionality ---
    is_wholesale = models.BooleanField(default=False, verbose_name=_("Is this a wholesale product?"))
    minimum_order = models.PositiveIntegerField(default=1, verbose_name=_("Minimum Order Quantity"))

    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_products', blank=True)

    def __str__(self):
        return self.name

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        try:
            return f"Image for {self.product.name}"
        except Product.DoesNotExist:
            return f"Orphan Image (ID: {self.id})"

# ==========================
# ==== 2. Profile Model ====
# ==========================

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='profile_pics/default_avatar.png', upload_to='profile_pics/')
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    is_wholesaler = models.BooleanField(default=False)
    
    # Premium membership fields
    is_premium_member = models.BooleanField(default=False)
    premium_since = models.DateTimeField(null=True, blank=True)
    premium_until = models.DateTimeField(null=True, blank=True)
    premium_type = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('annual', 'Annual'), ('lifetime', 'Lifetime')],
        null=True,
        blank=True
    )
    
    # Business verification fields
    business_verified = models.BooleanField(default=False)
    business_name = models.CharField(max_length=200, blank=True)
    business_license = models.FileField(upload_to='business_licenses/', null=True, blank=True)
    tax_clearance = models.FileField(upload_to='tax_documents/', null=True, blank=True)
    
    def is_premium_active(self):  # ← FIXED INDENTATION
        if self.premium_until:
            return self.is_premium_member and timezone.now() < self.premium_until
        return self.is_premium_member
    
    def __str__(self):  # ← FIXED INDENTATION
        try:
            return f'{self.user.username} Profile'
        except User.DoesNotExist:
            return f'Orphan Profile (ID: {self.id})'

    def save(self, *args, **kwargs):  # ← FIXED INDENTATION
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)
        except (FileNotFoundError, ValueError):
            pass
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

# =================================
# ==== 3. Chat & Message Models ====
# =================================

class Conversation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        try:
            participant_names = ", ".join([user.username for user in self.participants.all()])
            product_name = self.product.name if self.product else "Deleted Product"
            return f'Conversation about "{product_name}" between {participant_names}'
        except Exception:
            return f'Conversation (ID: {self.id})'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f'Message from {self.sender.username} at {self.timestamp.strftime("%Y-%m-%d %H:%M")}'

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order']

    def __str__(self):
        return self.question