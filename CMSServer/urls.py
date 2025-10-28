from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"blogs", views.BlogViewSet)
router.register(r"posts", views.PostViewSet)
router.register(r"tags", views.TagViewSet)
router.register(r"auth", views.AuthViewSet, basename="auth")

urlpatterns = [
    path("api/", include(router.urls)),
]
