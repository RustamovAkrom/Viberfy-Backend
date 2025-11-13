from rest_framework import serializers
from apps.musics.models import Artist, Album, Track, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]


class ArtistTrackSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = (
            "id",
            "name",
            "duration",
            "audio",
            "cover",
            "plays_count",
            "likes_count",
            "genres",
            "is_published",
        )


class AlbumWithTracksSerializer(serializers.ModelSerializer):
    tracks = ArtistTrackSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = (
            "id",
            "name",
            "slug",
            "cover",
            "release_date",
            "is_published",
            "tracks",
        )


class ArtistListSerializer(serializers.ModelSerializer):
    albums_count = serializers.SerializerMethodField()
    tracks_count = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = (
            "id",
            "name",
            "slug",
            "avatar",
            "followers_count",
            "total_plays",
            "total_likes",
            "is_verified",
            "albums_count",
            "tracks_count",
            "created_at",
            "updated_at",
        )

    def get_albums_count(self, obj):
        return obj.albums.filter(is_published=True).count()

    def get_tracks_count(self, obj):
        return obj.tracks.filter(is_published=True).count()


class ArtistDetailSerializer(serializers.ModelSerializer):
    albums = AlbumWithTracksSerializer(many=True, read_only=True)
    tracks = ArtistTrackSerializer(many=True, read_only=True)
    albums_count = serializers.SerializerMethodField()
    tracks_count = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = (
            "id",
            "name",
            "slug",
            "owner",
            "bio",
            "avatar",
            "meta",
            "followers_count",
            "total_plays",
            "total_likes",
            "is_verified",
            "albums",
            "tracks",
            "albums_count",
            "tracks_count",
            "created_at",
            "updated_at",
        )

    def get_albums_count(self, obj):
        return obj.albums.filter(is_published=True).count()

    def get_tracks_count(self, obj):
        return obj.tracks.filter(is_published=True).count()


class ArtistCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ("name", "bio", "avatar", "meta", "is_verified")
        read_only_fields = ("slug", "followers_count", "total_plays", "total_likes")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["owner"] = request.user
        return super().create(validated_data)
