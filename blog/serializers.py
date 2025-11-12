from rest_framework import serializers
from .models import Blog, Post
from tag.models import Tag
from user.serializers import UserSerializer
from drf_spectacular.utils import extend_schema_serializer
from drf_spectacular.openapi import OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Post Example",
            summary="Ejemplo de post",
            description="Un post completo con etiquetas",
            value={
                "id": 1,
                "title": "Mi Primer Post",
                "content": "Contenido del post...",
                "published_at": "2025-01-27T10:00:00Z",
                "updated_at": "2025-01-27T10:00:00Z",
                "blog": 1,
                "tags": [1, 2],
            },
        )
    ]
)
class PostSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    blog = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "published_at",
            "updated_at",
            "blog",
            "tags",
        ]
        read_only_fields = ["published_at", "updated_at", "blog"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Blog Example",
            summary="Ejemplo de blog",
            description="Un blog completo con información del usuario",
            value={
                "id": 1,
                "title": "Mi Blog Personal",
                "description": "Un blog sobre tecnología y programación",
                "created_at": "2025-01-27T10:00:00Z",
                "updated_at": "2025-01-27T10:00:00Z",
                "user": {"id": 1, "username": "usuario"},
            },
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
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
