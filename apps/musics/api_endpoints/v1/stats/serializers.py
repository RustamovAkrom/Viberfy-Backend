from rest_framework import serializers
from apps.musics.models import Like, ListeningHistory
from apps.musics.models.track import Track


class TrackMiniSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    album_name = serializers.CharField(source="album.name", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            "id",
            "name",
            "slug",
            "cover",
            "duration",
            "plays_count",
            "likes_count",
            "artist_name",
            "album_name",
            "is_liked",
        ]

    def get_is_liked(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return obj.likes.filter(user=user).exists()


class LikeSerializer(serializers.ModelSerializer):
    track = TrackMiniSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "track"]
        read_only_fields = ["id", "track"]


class ListeningHistorySerializer(serializers.ModelSerializer):
    track = TrackMiniSerializer(read_only=True)

    class Meta:
        model = ListeningHistory
        fields = ["id", "track", "listened_at", "duration", "additional_info"]
        read_only_fields = ["id", "track", "listened_at"]
