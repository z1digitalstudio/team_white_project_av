from rest_framework import viewsets
from .models import Tag
from .serializers import TagSerializer
from blog.mixins import PublicReadOnlyMixin
from drf_spectacular.utils import extend_schema, extend_schema_view


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
class TagViewSet(PublicReadOnlyMixin, viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
