from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count
from apps.musics.models import Playlist
from .serializers import (
    PlaylistListSerializer,
    PlaylistDetailSerializer,
    PlaylistCreateUpdateSerializer,
)
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from apps.shared.permissions import IsOwnerOrReadOnly


@extend_schema_view(
    list=extend_schema(
        tags=["Playlists"],
        summary="Get all playlists",
        description="Retrieve a list of all playlists.",
        responses={200: PlaylistListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Playlists"],
        summary="Get playlist details",
        description="Retrieve detailed information about a specific playlist by slug.",
        responses={200: PlaylistDetailSerializer},
    ),
    create=extend_schema(
        tags=["Playlists"],
        summary="Create a new playlist",
        description="Create and add a new playlist to the system.",
        request=PlaylistCreateUpdateSerializer,
        responses={201: PlaylistDetailSerializer},
    ),
    update=extend_schema(
        tags=["Playlists"],
        summary="Update playlist",
        description="Update an existing playlist by slug.",
        request=PlaylistCreateUpdateSerializer,
        responses={200: PlaylistDetailSerializer},
    ),
    partial_update=extend_schema(
        tags=["Playlists"],
        summary="Partially update playlist",
        description="Update some fields of an existing playlist by slug.",
        request=PlaylistCreateUpdateSerializer,
        responses={200: PlaylistDetailSerializer},
    ),
    destroy=extend_schema(
        tags=["Playlists"],
        summary="Delete playlist",
        description="Delete an existing playlist by slug.",
        responses={204: OpenApiResponse(description="Playlist successfully deleted")},
    ),
)
class PlaylistViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления плейлистами.
    Поддерживает CRUD, поиск, сортировку и очистку треков.
    """

    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "owner__username"]
    ordering_fields = ["created_at", "updated_at", "name"]

    def get_queryset(self):
        """Оптимизированный queryset с подсчётом треков"""

        qs = (
            Playlist.objects.all()
            .annotate(tracks_count=Count("playlisttrack"))
            .select_related("owner")
        )
        return qs.select_related("owner").prefetch_related("tracks")

    def get_serializer_class(self):
        """Выбор сериализатора по действию"""

        match self.action:
            case "list":
                return PlaylistListSerializer
            case "retrieve":
                return PlaylistDetailSerializer
            case "create" | "update" | "partial_update":
                return PlaylistCreateUpdateSerializer
            case _:
                return PlaylistDetailSerializer

    def perform_create(self, serializer):
        """Привязываем владельца при создании"""

        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Authentication required to create a playlist.")
        serializer.save(owner=self.request.user)

    @extend_schema(
        tags=["Playlists"],
        summary="Clear all tracks from a playlist",
        description="Remove all tracks from the specified playlist (owner only).",
        responses={200: OpenApiResponse(description="Tracks successfully cleared")},
    )
    @action(detail=True, methods=["post"], url_path="clear-tracks")
    def clear_tracks(self, request, slug=None):
        """Удаляет все треки из плейлиста (только владелец может очистить)"""

        playlist = self.get_object()

        # Проверка прав: только владелец
        if playlist.owner != request.user:
            return Response(
                {"detail": "You do not have permission to clear this playlist."},
                status=status.HTTP_403_FORBIDDEN,
            )

        deleted_count, _ = playlist.playlisttrack_set.all().delete()
        return Response(
            {"status": f"{deleted_count} tracks cleared"},
            status=status.HTTP_200_OK,
        )


__all__ = ["PlaylistViewSet"]
