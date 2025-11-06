from rest_framework import viewsets
from .models import Blog, Post
from .serializers import (
    BlogSerializer,
    PostSerializer,
)
from user.serializers import UserSerializer
from .mixins import (
    PublicReadOnlyMixin,
    BlogOwnerPermissionMixin,
    PostEditorMixin,
    LimitBlogChoicesToOwnerMixin,
    PostOwnerQuerysetViewSetMixin,
    FilterPostsByBlogViewSetMixin,
)
from blog.exceptions import AuthenticationError
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(
        summary="Listar blogs",
        description="Obtiene una lista de todos los blogs disponibles. Los blogs son públicos para lectura.",
        tags=["Blogs"],
    ),
    create=extend_schema(
        summary="Crear blog",
        description="Crea un nuevo blog para el usuario autenticado. Requiere autenticación.",
        tags=["Blogs"],
    ),
    retrieve=extend_schema(
        summary="Obtener blog",
        description="Obtiene los detalles de un blog específico por ID.",
        tags=["Blogs"],
    ),
    update=extend_schema(
        summary="Actualizar blog",
        description="Actualiza un blog existente. Solo el propietario puede actualizar.",
        tags=["Blogs"],
    ),
    destroy=extend_schema(
        summary="Eliminar blog",
        description="Elimina un blog. Solo el propietario puede eliminar.",
        tags=["Blogs"],
    ),
)
class BlogViewSet(
    BlogOwnerPermissionMixin,
    PublicReadOnlyMixin,
    viewsets.ModelViewSet,
    LimitBlogChoicesToOwnerMixin,
):

    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="Listar posts",
        description="Obtiene una lista de posts. Se pueden filtrar por blog.",
        tags=["Posts"],
    ),
    create=extend_schema(
        summary="Crear post",
        description="Crea un nuevo post en un blog. Requiere autenticación.",
        tags=["Posts"],
    ),
    retrieve=extend_schema(
        summary="Obtener post",
        description="Obtiene los detalles de un post específico.",
        tags=["Posts"],
    ),
    update=extend_schema(
        summary="Actualizar post",
        description="Actualiza un post existente. Solo el propietario puede actualizar.",
        tags=["Posts"],
    ),
    destroy=extend_schema(
        summary="Eliminar post",
        description="Elimina un post. Solo el propietario puede eliminar.",
        tags=["Posts"],
    ),
)
class PostViewSet(
    BlogOwnerPermissionMixin,
    PublicReadOnlyMixin,
    FilterPostsByBlogViewSetMixin,
    PostOwnerQuerysetViewSetMixin,
    PostEditorMixin,
    viewsets.ModelViewSet,
):

    queryset = Post.objects.all()
    serializer_class = PostSerializer


