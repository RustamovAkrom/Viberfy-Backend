from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from django.db.models import Count
from apps.musics.models import Artist
from .serializers import (
    ArtistListSerializer,
    ArtistDetailSerializer,
    ArtistCreateUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Artists"],
        summary="Get all artists",
        description="Retrieve a list of all artists.",
        responses={200: ArtistListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Artists"],
        summary="Get artist details",
        description="Retrieve detailed information about a specific artist by ID.",
        responses={200: ArtistDetailSerializer},
    ),
    create=extend_schema(
        tags=["Artists"],
        summary="Create a new artist",
        description="Create and add a new artist to the system.",
        request=ArtistCreateUpdateSerializer,
        responses={201: ArtistDetailSerializer},
    ),
    update=extend_schema(
        tags=["Artists"],
        summary="Update artist",
        description="Update an existing artist by ID.",
        request=ArtistCreateUpdateSerializer,
        responses={200: ArtistDetailSerializer},
    ),
    partial_update=extend_schema(
        tags=["Artists"],
        summary="Partially update artist",
        description="Update some fields of an existing artist by ID.",
        request=ArtistCreateUpdateSerializer,
        responses={200: ArtistDetailSerializer},
    ),
    destroy=extend_schema(
        tags=["Artists"],
        summary="Delete artist",
        description="Delete an existing artist by ID.",
        responses={204: OpenApiResponse(description="Artist successfully deleted")},
    ),
)
class ArtistViewSet(viewsets.ModelViewSet):
    queryset = (
        Artist.objects.all()
        .annotate(albums_count=Count("albums"))
        .order_by("-created_at")
        .prefetch_related("albums__tracks")
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ArtistListSerializer
        elif self.action == "retrieve":
            return ArtistDetailSerializer
        return ArtistCreateUpdateSerializer

    def perform_create(self, serializer):
        """Привязываем владельца при создании"""
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Authentication required to create a playlist.")
        serializer.save(owner=self.request.user)


__all__ = ["ArtistViewSet"]
