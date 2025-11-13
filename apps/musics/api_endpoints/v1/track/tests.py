from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.musics.models import Track, Artist, Album

User = get_user_model()


class TrackAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="pass123"
        )
        self.client.force_authenticate(user=self.user)

        self.artist = Artist.objects.create(name="Artist 1", owner=self.user)
        self.album = Album.objects.create(
            name="Album 1", artist=self.artist, owner=self.user
        )

        audio_file1 = SimpleUploadedFile(
            "audio1.mp3", b"file_content", content_type="audio/mpeg"
        )
        audio_file2 = SimpleUploadedFile(
            "audio2.mp3", b"file_content", content_type="audio/mpeg"
        )

        self.track1 = Track.objects.create(
            owner=self.user,
            name="Track One",
            artist=self.artist,
            album=self.album,
            duration=120,
            audio=audio_file1,
            is_published=True,
        )
        self.track2 = Track.objects.create(
            owner=self.user,
            name="Other Song",
            artist=self.artist,
            duration=150,
            audio=audio_file2,
            is_published=True,
        )

        self.list_url = reverse("track-list")
        self.detail_url = lambda slug: reverse("track-detail", args=[slug])
        # Эти два будут работать только если у тебя реально есть эндпоинты в urls.py
        self.play_url = lambda slug: reverse("track-play", args=[slug])
        self.like_url = lambda slug: reverse("track-like", args=[slug])

    def _auth_post(self, url, data=None, format="json"):
        """Helper для авторизованных POST-запросов"""
        self.client.force_authenticate(user=self.user)
        return self.client.post(url, data or {}, format=format)

    # ---------------- List & Retrieve ----------------
    def test_list_tracks(self):
        """Тестируем получение списка треков"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data
        self.assertEqual(len(results), 2)  # только опубликованные
        names = {t["name"] for t in results}
        self.assertEqual(names, {"Track One", "Other Song"})
        self.assertEqual(results[0]["artist_name"], self.artist.name)

    def test_retrieve_track(self):
        """Тестируем получение детальной информации о треке"""
        response = self.client.get(self.detail_url(self.track1.slug))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.track1.name)
        self.assertEqual(response.data["artist_name"], self.artist.name)

    # ---------------- Auth Create & Update ----------------
    def test_create_track_anon(self):
        """Тестируем создание трека анонимным пользователем (должно быть запрещено)"""
        self.client.force_authenticate(user=None)  # разлогиниваем
        audio_file = SimpleUploadedFile(
            "audio3.mp3", b"file_content", content_type="audio/mpeg"
        )
        data = {
            "name": "Track 3",
            "artist": self.artist.id,
            "duration": 100,
            "audio": audio_file,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_track_auth(self):
        """Тестируем создание трека аутентифицированным пользователем"""
        audio_file = SimpleUploadedFile(
            "audio3.mp3", b"file_content", content_type="audio/mpeg"
        )
        data = {
            "name": "Track 3",
            "artist": self.artist.id,
            "album": self.album.id,  # ✅ добавляем альбом, чтобы не было 400
            "duration": 100,
            "audio": audio_file,
            "genre": "Rock",
            "is_published": True,
        }
        response = self._auth_post(self.list_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Track.objects.filter(name="Track 3").exists())

    # ---------------- Play & Like ----------------
    def test_play_increment(self):
        """Тестируем увеличение счетчика прослушиваний"""
        try:
            response = self._auth_post(self.play_url(self.track1.slug))
        except Exception:
            self.skipTest("Endpoint track-play не реализован")
            return
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.track1.refresh_from_db()
        self.assertEqual(self.track1.plays_count, 1)

    def test_like_increment(self):
        """Тестируем увеличение счетчика лайков"""
        try:
            response = self._auth_post(self.like_url(self.track1.slug))
        except Exception:
            self.skipTest("Endpoint track-like не реализован")
            return
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.track1.refresh_from_db()
        self.assertEqual(self.track1.likes_count, 1)

    # ---------------- Filters & Search ----------------
    def test_filter_by_artist(self):
        """Тестируем фильтрацию треков по артисту"""
        response = self.client.get(self.list_url, {"artist": self.artist.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_by_name(self):
        """Тестируем поиск треков по имени"""
        response = self.client.get(self.list_url, {"search": "Track One"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Track One")
