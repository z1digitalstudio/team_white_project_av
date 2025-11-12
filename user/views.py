from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth import login, logout
from user.serializers import LoginSerializer, UserSerializer, RegisterSerializer
from user.mixins import AuthenticationMixin
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
