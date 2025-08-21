from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This path is for the homepage (e.g., http://127.0.0.1:8000/)
    path('', user_views.home, name='home'),
    
    # This includes all URLs from the 'users' app (like /register/)
    path('accounts/', include('users.urls')),
    
    # This includes Django's built-in URLs (like /login/, /logout/)
    path('accounts/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)