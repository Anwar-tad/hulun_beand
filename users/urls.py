from django.urls import path
from . import views

urlpatterns = [
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
]
