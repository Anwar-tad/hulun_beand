# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from django.utils.translation import gettext_lazy as _

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
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Seller")) # Corrected verbose_name
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        try:
            return f'{self.user.username} Profile'
        except User.DoesNotExist:
            return f'Orphan Profile (ID: {self.id})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)
        except (FileNotFoundError, ValueError):
            pass

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