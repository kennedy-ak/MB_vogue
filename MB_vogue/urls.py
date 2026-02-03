from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Django default admin (optional)
    path('panel/', include('admin_panel.urls')),  # Custom admin panel
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('payments/', include('payments.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
