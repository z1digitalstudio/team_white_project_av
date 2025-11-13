from rest_framework import serializers
from .models import Tag
from drf_spectacular.utils import extend_schema_serializer
from drf_spectacular.openapi import OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Tag Example",
            summary="Ejemplo de etiqueta",
            description="Una etiqueta simple",
            value={"id": 1, "name": "tecnología"},
        )
    ]
)
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["id", "name"]

