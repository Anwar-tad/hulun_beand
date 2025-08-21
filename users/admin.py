from django.contrib import admin
from .models import Product,Category # Product ሞዴልን እናስገባለን
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'category', 'created_at')
    list_filter = ('category', 'created_at', 'seller')
    search_fields = ('name', 'description')

admin.site.register(Product, ProductAdmin) # ProductAdminን ተጠቀም
admin.site.register(Category)
# Product ሞዴልን በአስተዳደር ገጹ ላይ እንመዘግባለን
