from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    
    # Premium URLs
    path('premium/upgrade/', views.premium_upgrade, name='premium_upgrade'),
    path('premium/success/', views.premium_success, name='premium_success'),
    
    # Wholesale URLs
    
    path('wholesale/orders/', views.wholesale_orders, name='wholesale_orders'),
    path('Wholesale/suppliers/', views.wholesale_suppliers, name='wholesale_suppliers'),
    path('wholesale/dashboard/', views.wholesale_dashboard, name='wholesale_dashboard'),
    path('wholesale/products/', views.wholesale_products, name='wholesale_products'),

    path('register/', views.register, name='register'),
    path('product/create/', views.create_product, name='create_product'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('profile/<str:username>/', views.profile, name='profile'),
     path('update/', views.profile_update, name='profile_update'),
    path('product/<int:pk>/like/', views.like_product, name='like_product'),
    path('product/<int:pk>/dislike/', views.dislike_product, name='dislike_product'),
    
    # --- አዲስ የምንጨምራቸው የ Chat ዩአርኤሎች ---
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/start/<int:product_pk>/', views.start_conversation, name='start_conversation'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    # ... ሌሎች url patterns
    path('help/', TemplateView.as_view(template_name='help.html'), name='help'),

    path('help/', views.help_page, name='help'),
    path('wholesale/', views.wholesale_view, name='wholesale'),
    path('payment-required/', views.payment_required_view, name='payment_required'),
    
    #... ሌሎች URLዎች
    path('post/retail/', views.create_retail_product, name='post_retail_product'),
    path('switch-to-wholesale/', views.switch_to_wholesale, name='switch_to_wholesale'),
    # Premium wholesale URLs
    path('premium/wholesale/', views.premium_wholesale, name='premium_wholesale'),
    
  
    path('business-verification/', views.business_verification, name='business_verification'),
    path('verification-success/', views.verification_success, name='verification_success'),
    path('api/premium-status/', views.check_premium_status, name='check_premium_status'),

    path('upgrade/', views.upgrade_account, name='upgrade_account'),
    
    path('post/wholesale/', views.create_wholesale_product, name='post_wholesale_product'),
    path('wholesale/', views.wholesale_home, name='wholesale_home'),
    path('jobs/', views.job_listings, name='job_listings'),
    path('tenders/', views.tenders, name='tenders'),
    path('real-estate/', views.real_estate, name='real_estate'),
    path('vehicles/', views.vehicles, name='vehicles'),
    path('services/', views.services, name='services'),
    path('healthcare/', views.healthcare, name='healthcare'),
]

