from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from apps.musics.models import Like, ListeningHistory
from .paginations import StatsPagination
from .serializers import LikeSerializer, ListeningHistorySerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Likes"],
        summary="Get user likes",
        description="Retrieve a list of all tracks the authenticated user has liked (most recent first).",
        responses={200: LikeSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Likes"],
        summary="Like a track",
        description="Add a track to the authenticated user's likes.",
        responses={201: LikeSerializer},
    ),
    destroy=extend_schema(
        tags=["Likes"],
        summary="Unlike a track",
        description="Remove a track from the authenticated user's likes.",
        responses={204: OpenApiResponse(description="No Content")},
    ),
)
class LikeViewSet(ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StatsPagination

    def get_queryset(self):
        qs = Like.objects.filter(user=self.request.user)
        return (
            qs.select_related("track", "user")
            .prefetch_related("track__likes")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        tags=["Listening History"],
        summary="Get listening history",
        description="Retrieve a list of all tracks the authenticated user has listened to (most recent first).",
        responses={200: ListeningHistorySerializer(many=True)},
    ),
)
class ListeningHistoryViewSet(ModelViewSet):
    serializer_class = ListeningHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StatsPagination
    lookup_field = "slug"

    def get_queryset(self):
        qs = ListeningHistory.objects.filter(user=self.request.user).order_by(
            "-listened_at"
        )[:50]
        return qs.select_related("track", "user").prefetch_related("track__likes")

    # create можно оставить, но обычно записи создаются автоматически при play()
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="clear", url_name="clear")
    @extend_schema(
        tags=["Listening History"],
        summary="Clear listening history",
        description="Delete all listening history records for the authenticated user.",
        responses={204: OpenApiResponse(description="No Content")},
    )
    def clear(self, request, *args, **kwargs):
        user = request.user
        deleted_count, _ = ListeningHistory.objects.filter(user=user).delete()
        return Response(
            {"message": f"Cleared {deleted_count} listening history records."},
            status=204,
        )


__all__ = ["LikeViewSet", "ListeningHistoryViewSet"]
