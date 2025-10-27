from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Blog, Post, Tag
from django.contrib.auth.models import User
from .utils import authenticate_user
from .exceptions import InvalidCredentialsError
from drf_spectacular.utils import extend_schema_serializer
from drf_spectacular.openapi import OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'User Example',
            summary='Ejemplo de usuario',
            description='Información básica del usuario',
            value={
                'id': 1,
                'username': 'usuario_ejemplo'
            }
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id']

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Register Example',
            summary='Ejemplo de registro',
            description='Datos necesarios para registrar un nuevo usuario',
            value={
                'username': 'nuevo_usuario',
                'password': 'contraseña123',
                'password_confirm': 'contraseña123'
            }
        )
    ]
)
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(**validated_data)
        return user

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Login Example',
            summary='Ejemplo de login',
            description='Credenciales para iniciar sesión',
            value={
                'username': 'usuario',
                'password': 'contraseña'
            }
        )
    ]
)
class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate_user(username, password)
            if not user:
                    raise InvalidCredentialsError()
            attrs['user'] = user
        else:
            raise ValidationError('Must provide username and password')
        return attrs

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Tag Example',
            summary='Ejemplo de etiqueta',
            description='Una etiqueta simple',
            value={
                'id': 1,
                'name': 'tecnología'
            }
        )
    ]
)
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["id", "name"]

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Post Example',
            summary='Ejemplo de post',
            description='Un post completo con etiquetas',
            value={
                'id': 1,
                'title': 'Mi Primer Post',
                'content': 'Contenido del post...',
                'published_at': '2025-01-27T10:00:00Z',
                'updated_at': '2025-01-27T10:00:00Z',
                'blog': 1,
                'tags': [1, 2]
            }
        )
    ]
)
class PostSerializer(serializers.ModelSerializer):
   
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    blog = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Post
        fields = ["id", "title", "content", "published_at", "updated_at", "blog", "tags"]
        read_only_fields = ["published_at", "updated_at", "blog"]

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Blog Example',
            summary='Ejemplo de blog',
            description='Un blog completo con información del usuario',
            value={
                'id': 1,
                'title': 'Mi Blog Personal',
                'description': 'Un blog sobre tecnología y programación',
                'created_at': '2025-01-27T10:00:00Z',
                'updated_at': '2025-01-27T10:00:00Z',
                'user': {
                    'id': 1,
                    'username': 'usuario'
                }
            }
        )
    ]
)
class BlogSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Blog
        fields = ["id", "title", "description", "created_at", "updated_at", "user"]
        read_only_fields = ["created_at", "updated_at"]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

