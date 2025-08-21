from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('product/create/', views.create_product, name='create_product'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    
    path('profile/<str:username>/', views.profile, name='profile'),
]
