"""
URL configuration for ySEal project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from apps.core.views import home, browse, contributors, yoel_story

urlpatterns = [
    # Home page
    path('', home, name='home'),
    path('browse/', browse, name='browse'),
    path('contributors/', contributors, name='contributors'),
    path('about/yoel/', yoel_story, name='yoel-story'),
    
    # Admin Dashboard
    path('dashboard/', include('apps.admin_dashboard.urls', namespace='admin_dashboard')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 (UI endpoints)
    path('api/_ui/v1/', include('apps.api.v1.urls', namespace='api-ui-v1')),
    
    # API v3 (Main API for CLI)
    path('api/v3/', include('apps.api.v3.urls', namespace='api-v3')),
    
    # Authentication
    path('api/auth/', include('apps.accounts.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
