from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
# Add your Category, Product, and ProductImage models here.
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
    
    # --- New fields for wholesale functionality ---
    is_wholesale = models.BooleanField(default=False, verbose_name=_("Is this a wholesale product?"))
    minimum_order = models.PositiveIntegerField(default=1, verbose_name=_("Minimum Order Quantity"))




class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        try:
            return f"Image for {self.product.name}"
        except Product.DoesNotExist:
            return f"Orphan Image (ID: {self.id})"