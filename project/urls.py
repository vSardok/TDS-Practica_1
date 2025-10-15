"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from courses_api import urls as courses_urls

schema_view = get_schema_view(
    openapi.Info(
        title="Courses API Documentation",
        default_version='v1',
        description="A comprehensive Learning Management System API built with Django REST Framework. "
        "Supports multi-role users (instructors and students) with full CRUD operations "
        "for courses, lessons, enrollments, and more.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@courses_api.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=courses_urls.urlpatterns,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses_api.urls')),
    # path('courses/', include('courses_api.urls')),

    # DRF browsable API login
    path('api-auth/', include('rest_framework.urls')),

    # Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('accounts/', include('allauth.urls')),
]
