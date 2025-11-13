# apps/musics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.musics.api_endpoints.v1 import (
    AlbumViewSet,
    ArtistViewSet,
    PlaylistViewSet,
    LikeViewSet,
    ListeningHistoryViewSet,
    TrackViewSet,
)

router = DefaultRouter()

# Регистрация всех ViewSet
router.register(r"albums", AlbumViewSet, basename="album")
router.register(r"artists", ArtistViewSet, basename="artist")
router.register(r"playlists", PlaylistViewSet, basename="playlist")
router.register(r"tracks", TrackViewSet, basename="track")
router.register(r"likes", LikeViewSet, basename="like")
router.register(r"history", ListeningHistoryViewSet, basename="history")

urlpatterns = [
    path("", include(router.urls)),  # /musics/...
]
