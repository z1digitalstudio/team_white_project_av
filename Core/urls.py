from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def root_view(request):
    """Root endpoint that returns API information."""
    return JsonResponse({
        "status": "ok",
        "message": "CMS Server API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "api_docs": "/api/docs/",
            "api_redoc": "/api/redoc/",
            "api_schema": "/api/schema/",
            "authentication": "/cms/api/auth/",
            "blogs": "/cms/api/blogs/",
            "posts": "/cms/api/posts/",
            "tags": "/cms/api/tags/",
        },
        "documentation": "See /api/docs/ for interactive API documentation"
    })


urlpatterns = [
    path("", root_view, name="root"),
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("cms/", include("user.urls")),
    path("cms/", include("tag.urls")),
    path("cms/", include("blog.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
