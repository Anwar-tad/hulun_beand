from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns 
urlpatterns = [
     path('i18n/', include('django.conf.urls.i18n')),
    # የአስተዳደር ገጹ ከቋንቋ ለውጥ ውጪ እንዲሆን
    path('admin/', admin.site.urls),
]
urlpatterns += i18n_patterns(
    # ሁሉም ሌሎች ዩአርኤሎች እዚህ ውስጥ ይገባሉ
    
    # This path is for the homepage (e.g., http://127.0.0.1:8000/)
    path('', user_views.home, name='home'),
    
    # This includes all URLs from the 'users' app (like /register/)
    path('accounts/', include('users.urls')),
    
    # This includes Django's built-in URLs (like /login/, /logout/)
    path('accounts/', include('django.contrib.auth.urls')),

    # ... (prefix='accounts' የሚለውን ከ users.urls ላይ ማንሳት ሊያስፈልግ ይችላል)
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)