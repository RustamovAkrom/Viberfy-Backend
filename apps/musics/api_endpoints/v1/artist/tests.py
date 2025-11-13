from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.musics.models import Artist, Album, Track

User = get_user_model()


class ArtistAPITestCase(APITestCase):
    """Тесты для Artist API (полный CRUD + доступы + вложенные данные)."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )

        self.artist = Artist.objects.create(name="Test Artist", owner=self.admin)

        self.album = Album.objects.create(
            name="Test Album", artist=self.artist, owner=self.admin
        )
        self.track = Track.objects.create(
            owner=self.admin,
            name="Test Track",
            album=self.album,
            artist=self.artist,
            duration=180,
        )
        self.list_url = reverse("artist-list")
        self.detail_url = reverse("artist-detail", args=[self.artist.slug])

    def test_artist_list_anon(self):
        """Аноним может видеть список артистов"""

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data[0])
        self.assertIn("albums_count", response.data[0])

    def test_artist_list_search(self):
        """Поиск артистов по имени"""

        response = self.client.get(self.list_url, {"search": "Test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_artist_retrieve(self):
        """Аноним может видеть детали артиста с альбомами и треками"""

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.artist.name)
        self.assertIn("albums", response.data)
        self.assertEqual(len(response.data["albums"]), 1)
        self.assertEqual(response.data["albums"][0]["tracks"][0]["name"], "Test Track")

    def test_artist_create_admin(self):
        """Админ может создать артиста"""

        self.client.force_authenticate(user=self.admin)
        data = {"name": "New Artist"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artist.objects.count(), 2)

    def test_artist_create_anon(self):
        """Аноним не может создать артиста"""

        data = {"name": "New Artist"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_artist_update_admin(self):
        """Админ может полностью обновить артиста"""

        self.client.force_authenticate(user=self.admin)
        data = {"name": "Updated Artist"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.artist.refresh_from_db()
        self.assertEqual(self.artist.name, "Updated Artist")

    def test_artist_partial_update_admin(self):
        """Админ может частично обновить артиста"""

        self.client.force_authenticate(user=self.admin)
        data = {"bio": "New bio"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.artist.refresh_from_db()
        self.assertEqual(self.artist.bio, "New bio")

    def test_artist_update_anon(self):
        """Аноним не может обновлять артиста"""

        data = {"name": "Hacker Artist"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_artist_delete_admin(self):
        """Админ может удалить артиста"""

        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Artist.objects.filter(id=self.artist.id).exists())

    def test_artist_delete_anon(self):
        """Аноним не может удалить артиста"""

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
