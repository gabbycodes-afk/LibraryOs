from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # We REMOVED the token paths from here because 
    # they are already inside api/urls.py
    
    path('api-auth/', include('rest_framework.urls')),
    
    # This includes EVERYTHING from api/urls.py 
    # (Registration, Books, AND your fixed Token View)
    path('api/', include('api.urls')), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)