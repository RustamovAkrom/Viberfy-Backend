from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from apps.musics.models import Album
from .serializers import *  # noqa
from apps.shared.permissions import IsOwnerOrReadOnly
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse


@extend_schema_view(
    list=extend_schema(
        tags=["Albums"],
        summary="Get all albums",
        description="Retrieve a list of all albums.",
        responses={200: AlbumListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Albums"],
        summary="Get album details",
        description="Retrieve detailed information about a specific album by ID.",
        responses={200: AlbumDetailSerializer},
    ),
    create=extend_schema(
        tags=["Albums"],
        summary="Create a new album",
        description="Create and add a new album to the system.",
        request=AlbumCreateUpdateSerializer,
        responses={201: AlbumDetailSerializer},
    ),
    update=extend_schema(
        tags=["Albums"],
        summary="Update album",
        description="Update an existing album by ID.",
        request=AlbumCreateUpdateSerializer,
        responses={200: AlbumDetailSerializer},
    ),
    partial_update=extend_schema(
        tags=["Albums"],
        summary="Partially update album",
        description="Update some fields of an existing album by ID.",
        request=AlbumCreateUpdateSerializer,
        responses={200: AlbumDetailSerializer},
    ),
    destroy=extend_schema(
        tags=["Albums"],
        summary="Delete album",
        description="Delete an existing album by ID.",
        responses={204: OpenApiResponse(description="Album successfully deleted")},
    ),
)
class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "artist__name"]
    ordering_fields = ["release_date", "name"]

    def get_queryset(self):
        return (
            Album.objects.filter(is_published=True)
            .select_related("artist")
            .prefetch_related("tracks")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AlbumListSerializer
        if self.action in ["create", "update"]:
            return AlbumCreateUpdateSerializer
        return AlbumDetailSerializer

    def perform_create(self, serializer):
        """Привязываем владельца при создании"""
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Authentication required to create a playlist.")
        serializer.save(owner=self.request.user)


__all__ = ["AlbumViewSet"]
