from rest_framework import serializers
from django.db import transaction
from apps.musics.models import Playlist, PlaylistTrack, Track


class TrackInPlaylistSerializer(serializers.ModelSerializer):
    """Упрощённый трек внутри плейлиста (для деталей)"""

    class Meta:
        model = Track
        fields = ("id", "name", "duration")


class PlaylistTrackSerializer(serializers.ModelSerializer):
    """Трек в плейлисте с порядком"""

    track = TrackInPlaylistSerializer(read_only=True)

    class Meta:
        model = PlaylistTrack
        fields = ("id", "track", "order")


class PlaylistListSerializer(serializers.ModelSerializer):
    """Список плейлистов (краткая информация)"""

    owner = serializers.StringRelatedField()
    tracks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Playlist
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_public",
            "owner",
            "tracks_count",
            "created_at",
            "updated_at",
        )


class PlaylistDetailSerializer(serializers.ModelSerializer):
    """Детальная информация о плейлисте"""

    tracks = PlaylistTrackSerializer(
        source="playlisttrack_set",
        many=True,
        read_only=True,
    )
    owner = serializers.StringRelatedField()

    class Meta:
        model = Playlist
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_public",
            "owner",
            "tracks",
            "created_at",
            "updated_at",
        )


class PlaylistCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление плейлиста с поддержкой треков"""

    track_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Список ID треков для добавления в плейлист",
    )

    class Meta:
        model = Playlist
        fields = ("id", "name", "description", "is_public", "track_ids")

    def validate_track_ids(self, value):
        """Проверяем существование треков (один SQL-запрос)"""
        if not value:
            return []
        found_ids = set(
            Track.objects.filter(id__in=value).only("id").values_list("id", flat=True)
        )
        missing = set(value) - found_ids
        if missing:
            raise serializers.ValidationError(
                f"Некоторые треки не найдены: {sorted(missing)}"
            )
        return list(found_ids)

    @transaction.atomic
    def create(self, validated_data):
        """Создание плейлиста и добавление треков (оптимизировано)"""
        track_ids = validated_data.pop("track_ids", [])
        playlist = Playlist.objects.create(**validated_data)

        if track_ids:
            PlaylistTrack.objects.bulk_create(
                [
                    PlaylistTrack(playlist=playlist, track_id=tid, order=i)
                    for i, tid in enumerate(track_ids)
                ],
                batch_size=100,  # ⚡ ускоряет вставку при большом количестве треков
            )

        return playlist

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляем плейлист и треки, если нужно"""
        track_ids = validated_data.pop("track_ids", None)
        instance = super().update(instance, validated_data)

        if track_ids is not None:
            # Удаляем только старые связи без пересоздания самого объекта
            instance.playlisttrack_set.all().delete()
            if track_ids:
                PlaylistTrack.objects.bulk_create(
                    [
                        PlaylistTrack(playlist=instance, track_id=tid, order=i)
                        for i, tid in enumerate(track_ids)
                    ],
                    batch_size=100,
                )

        return instance


__all__ = [
    "PlaylistListSerializer",
    "PlaylistDetailSerializer",
    "PlaylistCreateUpdateSerializer",
]
