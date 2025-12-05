"""
URL Configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API URL patterns (authenticated endpoints)
api_urlpatterns = [
    # Authentication endpoints
    path('auth/', include('auths.urls')),

    # HostMail SaaS endpoints
    path('subscriptions/', include('subscriptions.urls')),
    path('websites/', include('websites.urls')),
    path('contacts/', include('contacts.urls')),
    path('projects/', include('projects.urls')),
    path('analytics/', include('analytics.urls')),
    path('webhooks/', include('webhooks.urls')),
    path('payments/', include('payments.urls')),
]

# Public API URL patterns (require API key)
public_api_urlpatterns = [
    path('', include('core.public_urls')),
]

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API routes (versioned - authenticated)
    path('api/v1/', include(api_urlpatterns)),

    # Public API routes (require API key)
    path('api/public/', include(public_api_urlpatterns)),

    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar (optionnel)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom admin site configuration
admin.site.site_header = "HostMail Administration"
admin.site.site_title = "HostMail Admin"
admin.site.index_title = "Bienvenue sur le portail d'administration HostMail"