from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from user.utils import authenticate_user
from user.exceptions import InvalidCredentialsError
from drf_spectacular.utils import extend_schema_serializer
from drf_spectacular.openapi import OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "User Example",
            summary="Ejemplo de usuario",
            description="Información básica del usuario",
            value={"id": 1, "username": "usuario_ejemplo"},
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username"]
        read_only_fields = ["id"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Register Example",
            summary="Ejemplo de registro",
            description="Datos necesarios para registrar un nuevo usuario",
            value={
                "username": "nuevo_usuario",
                "password": "contraseña123",
                "password_confirm": "contraseña123",
            },
        )
    ]
)
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")
        if password != password_confirm:
            raise ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        user = User.objects.create_user(**validated_data)
        return user


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Login Example",
            summary="Ejemplo de login",
            description="Credenciales para iniciar sesión",
            value={"username": "usuario", "password": "contraseña"},
        )
    ]
)
class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate_user(username, password)
            if not user:
                raise ValidationError({"non_field_errors": ["Invalid credentials"]})
            attrs["user"] = user
        else:
            raise ValidationError("Must provide username and password")
        return attrs

