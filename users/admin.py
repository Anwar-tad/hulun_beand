from django.contrib import admin
from .models import Product,Category,Profile, Conversation, Message # Product ሞዴልን እናስገባለን
from .models import FAQ  # Make sure to import the new model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'category', 'created_at')
    list_filter = ('category', 'created_at', 'seller')
    search_fields = ('name', 'description')

admin.site.register(Product, ProductAdmin) # ProductAdminን ተጠቀም
admin.site.register(Category)
admin.site.register(Profile)
# Product ሞዴልን በአስተዳደር ገጹ ላይ እንመዘግባለን

admin.site.register(Conversation)
admin.site.register(Message)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    list_editable = ('order',)

