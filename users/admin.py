from django.contrib import admin
from .models import Product,Category,Profile, Conversation, Message 
from .models import FAQ  
from .models import UserTier

@admin.register(UserTier)
class UserTierAdmin(admin.ModelAdmin):
    """
    Custom admin view for the UserTier model.
    """
    # This line FIXES the problem by making the 'user' field selectable.
    fields = ('user', 'tier', 'is_paid', 'paid_until')

    # These lines configure the list view in the admin.
    list_display = ('user', 'tier', 'is_paid', 'paid_until')
    list_filter = ('tier', 'is_paid')
    search_fields = ('user__username',) # Search for users by their username


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

