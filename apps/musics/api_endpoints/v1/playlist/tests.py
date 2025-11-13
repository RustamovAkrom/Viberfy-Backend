from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.musics.models import Playlist, Track, Artist

User = get_user_model()


class PlaylistAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )

        self.artist = Artist.objects.create(name="Artist 1", owner=self.user)

        self.track1 = Track.objects.create(
            name="Track 1", owner=self.user, duration=120, artist=self.artist
        )
        self.track2 = Track.objects.create(
            name="Track 2", owner=self.user, duration=150, artist=self.artist
        )

        self.playlist = Playlist.objects.create(name="My Playlist", owner=self.user)
        self.playlist.tracks.add(self.track1, self.track2)

        self.list_url = reverse("playlist-list")
        self.detail_url = reverse(
            "playlist-detail", args=[self.playlist.slug]
        )  # если lookup_field = "slug"
        self.clear_tracks_url = reverse(
            "playlist-clear-tracks", args=[self.playlist.slug]
        )

    def test_playlist_list_anon(self):
        """Тестируем получение списка плейлистов анонимным пользователем
        Плейлисты должны быть видны всем, но создание/редактирование только авторизованным
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = (
            response.data["results"] if "results" in response.data else response.data
        )
        self.assertTrue(len(items) > 0)

    def test_playlist_retrieve(self):
        """Тестируем получение детальной информации о плейлисте"""

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.playlist.name)
        self.assertEqual(len(response.data["tracks"]), 2)

    def test_playlist_create_auth(self):
        """Тестируем создание плейлиста авторизованным пользователем"""

        self.client.force_authenticate(user=self.user)
        data = {"name": "New Playlist", "track_ids": [self.track1.id, self.track2.id]}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Playlist.objects.count(), 2)

    def test_playlist_create_anon(self):
        """Тестируем создание плейлиста анонимным пользователем - должно быть запрещено"""
        data = {"name": "New Playlist"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_playlist_update_auth_owner(self):
        """Тестируем обновление плейлиста авторизованным владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Playlist", "track_ids": [self.track2.id]}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.name, "Updated Playlist")
        self.assertEqual(self.playlist.tracks.count(), 1)

    def test_playlist_update_not_owner(self):
        """Тестируем обновление плейлиста авторизованным, но не владельцем - должно быть запрещено"""
        self.client.force_authenticate(user=self.other_user)
        data = {"name": "Hacked Playlist"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_playlist_partial_update_auth_owner(self):
        """Тестируем частичное обновление плейлиста авторизованным владельцем"""
        self.client.force_authenticate(user=self.user)
        data = {"description": "Updated description"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.description, "Updated description")

    def test_playlist_delete_auth_owner(self):
        """Тестируем удаление плейлиста авторизованным владельцем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Playlist.objects.filter(id=self.playlist.id).exists())

    def test_playlist_delete_not_owner(self):
        """Тестируем удаление плейлиста авторизованным, но не владельцем - должно быть запрещено"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_clear_tracks(self):
        """Тестируем очистку треков из плейлиста владельцем"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.clear_tracks_url)
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.tracks.count(), 0)
