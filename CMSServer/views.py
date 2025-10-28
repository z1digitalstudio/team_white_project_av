from rest_framework import viewsets
from .models import Blog, Post, Tag
from .serializers import (
    BlogSerializer,
    PostSerializer,
    TagSerializer,
    LoginSerializer,
    UserSerializer,
    RegisterSerializer,
)
from .mixins import (
    PublicReadOnlyMixin,
    BlogOwnerPermissionMixin,
    PostEditorMixin,
    LimitBlogChoicesToOwnerMixin,
    PostOwnerQuerysetViewSetMixin,
    FilterPostsByBlogViewSetMixin,
    AuthenticationMixin,
)
from django.contrib.auth import login, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    login=extend_schema(
        summary="Iniciar sesión",
        description="Autentica un usuario y devuelve un token de acceso.",
        tags=["Authentication"],
        request=LoginSerializer,
        responses={
            200: {
                "description": "Login exitoso",
                "content": {
                    "application/json": {
                        "example": {
                            "token": "abc123...",
                            "user": {
                                "id": 1,
                                "username": "usuario",
                                "email": "usuario@ejemplo.com",
                            },
                            "message": "Logged in successfully",
                        }
                    }
                },
            },
            400: {"description": "Credenciales inválidas"},
        },
    ),
    logout=extend_schema(
        summary="Cerrar sesión",
        description="Cierra la sesión del usuario y elimina el token.",
        tags=["Authentication"],
    ),
    me=extend_schema(
        summary="Información del usuario",
        description="Obtiene la información del usuario autenticado actual.",
        tags=["Authentication"],
    ),
    register=extend_schema(
        summary="Registrar usuario",
        description="Crea una nueva cuenta de usuario.",
        tags=["Authentication"],
        request=RegisterSerializer,
        responses={
            201: {
                "description": "Usuario registrado exitosamente",
                "content": {
                    "application/json": {
                        "example": {
                            "token": "abc123...",
                            "user": {
                                "id": 1,
                                "username": "nuevo_usuario",
                                "email": "nuevo@ejemplo.com",
                            },
                            "message": "User registered successfully",
                        }
                    }
                },
            },
            400: {"description": "Datos de registro inválidos"},
        },
    ),
)
class AuthViewSet(viewsets.ViewSet, AuthenticationMixin):

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = self.create_user_token(user)
            login(request, user)
            return Response(
                {
                    "token": token,
                    "user": UserSerializer(user).data,
                    "message": "Logged in successfully",
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        self.delete_user_token(request.user)
        logout(request)
        return Response({"message": "Logged out successfully"})

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = self.create_user_token(user)
            login(request, user)
            return Response(
                {
                    "token": token,
                    "user": UserSerializer(user).data,
                    "message": "User registered successfully",
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@extend_schema_view(
    list=extend_schema(
        summary="Listar tags",
        description="Obtiene una lista de todas las etiquetas disponibles.",
        tags=["Tags"],
    ),
    create=extend_schema(
        summary="Crear tag",
        description="Crea una nueva etiqueta. Requiere autenticación.",
        tags=["Tags"],
    ),
    retrieve=extend_schema(
        summary="Obtener tag",
        description="Obtiene los detalles de una etiqueta específica.",
        tags=["Tags"],
    ),
    update=extend_schema(
        summary="Actualizar tag",
        description="Actualiza una etiqueta existente.",
        tags=["Tags"],
    ),
    destroy=extend_schema(
        summary="Eliminar tag", description="Elimina una etiqueta.", tags=["Tags"]
    ),
)
class TagViewSet(BlogOwnerPermissionMixin, PublicReadOnlyMixin, viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
