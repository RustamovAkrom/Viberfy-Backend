from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.cache import cache
from django.db.models import F
from django.db import transaction
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from apps.musics.models import Track, Like as TrackLike
from apps.musics.models.stats import ListeningHistory
from .serializers import (
    TrackListSerializer,
    TrackDetailSerializer,
    TrackCreateUpdateSerializer,
)
from apps.shared.paginations.base import SmallResultsSetPagination
from apps.shared.permissions.base import IsOwnerOrReadOnly


@extend_schema_view(
    list=extend_schema(
        tags=["Tracks"],
        summary="Get all tracks",
        description="Retrieve a list of all published tracks.",
        responses={200: TrackListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Tracks"],
        summary="Get track details",
        description="Retrieve detailed information about a specific track by ID.",
        responses={200: TrackDetailSerializer},
    ),
    create=extend_schema(
        tags=["Tracks"],
        summary="Create a new track",
        description="Create and add a new track to the system.",
        request=TrackCreateUpdateSerializer,
        responses={201: TrackDetailSerializer},
    ),
    update=extend_schema(
        tags=["Tracks"],
        summary="Update track",
        description="Update an existing track by ID.",
        request=TrackCreateUpdateSerializer,
        responses={200: TrackDetailSerializer},
    ),
    partial_update=extend_schema(
        tags=["Tracks"],
        summary="Partially update track",
        description="Update some fields of an existing track by ID.",
        request=TrackCreateUpdateSerializer,
        responses={200: TrackDetailSerializer},
    ),
    destroy=extend_schema(
        tags=["Tracks"],
        summary="Delete track",
        description="Delete an existing track by ID.",
        responses={204: OpenApiResponse(description="Track successfully deleted")},
    ),
)
class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    lookup_field = "slug"
    filterset_fields = ["genres", "artist", "album"]
    search_fields = ["name", "artist__name", "album__name"]
    ordering_fields = ["plays_count", "likes_count", "duration"]
    ordering = ["-plays_count"]

    def get_queryset(self):
        qs = Track.objects.filter(is_published=True)
        return qs.select_related("artist", "album").order_by("-plays_count")

    def get_serializer_class(self):
        if self.action == "list":
            return TrackListSerializer
        if self.action == "retrieve":
            return TrackDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return TrackCreateUpdateSerializer
        return TrackDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        track = self.get_object()

        # Сохраняем историю прослушивания, если пользователь аутентифицирован
        if request.user.is_authenticated:
            ListeningHistory.objects.update_or_create(
                user=request.user,
                track=track,
                defaults={
                    "listened_at": timezone.now(),
                    # Можно передать duration или дополнительные поля
                    # "duration": request.data.get("duration"),
                    # "additional_info": {"device": "web", "source": "track_page"}
                },
            )

        serializer = self.get_serializer(track)
        return Response(serializer.data)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())

    #     user = request.user
    #     liked_tracks = set()
    #     if user.is_authenticated:
    #         liked_tracks = set(TrackLike.objects.filter(user=user, track__in=queryset).values_list("track_id", flat=True))

    #     page = self.paginate_queryset(queryset)
    #     serializer = self.get_serializer(page or queryset, many=True, context={"user": user, "liked_tracks": liked_tracks})
    #     return self.get_paginated_response(serializer.data) if page else Response(serializer.data)
    
    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="play", permission_classes=[IsAuthenticated])
    def play(self, request, slug=None):
        track = self.get_object()
        track.plays_count = F('plays_count') + 1
        track.save(update_fields=["plays_count"])
        track.refresh_from_db()
        serializer = self.get_serializer(track)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="like", permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        track = self.get_object()
        like_obj, created = TrackLike.objects.select_for_update().get_or_create(
            user=request.user, track=track
        )

        if created:
            track.likes_count = F('likes_count') + 1
            is_liked = True
        else:
            like_obj.delete()
            track.likes_count = F('likes_count') - 1
            is_liked = False

        track.save(update_fields=['likes_count'])
        track.refresh_from_db()

        serializer = self.get_serializer(track)
        data = serializer.data
        data["is_liked"] = is_liked
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="similar", permission_classes=[IsAuthenticated])
    def similar(self, request, slug=None):
        track = self.get_object()
        cache_key = f"similar_{track.id}"
        similar_tracks = cache.get(cache_key)
        if not similar_tracks:
            similar_tracks = Track.objects.get_similar_tracks(track, limit=10)
            cache.set(cache_key, similar_tracks, 60*5)
        serializer = self.get_serializer(similar_tracks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = ["TrackViewSet"]
