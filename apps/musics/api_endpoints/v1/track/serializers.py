from rest_framework import serializers
from apps.musics.models import Track, Like as TrackLike, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track.artist.field.related_model  # это Artist
        fields = ["id", "name", "slug"]


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track.album.field.related_model  # это Album
        fields = ["id", "name", "slug", "cover", "release_date"]


class TrackListSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "release_date",
            "artist",
            "album",
            "audio",
            "cover",
            "duration",
            "genres",
            "is_published",
            "is_liked",
            "plays_count",
            "likes_count",
        ]

    def get_is_liked(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return TrackLike.objects.filter(user=user, track=obj).exists()


class TrackDetailSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = "__all__"


class TrackCreateUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)

    class Meta:
        model = Track
        fields = [
            "name",
            "artist",
            "album",
            "duration",
            "audio",
            "cover",
            "genres",
            "owner",
            "is_published",
        ]
