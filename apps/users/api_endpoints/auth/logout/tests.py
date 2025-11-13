from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User


class LogoutAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.refresh_token = str(RefreshToken.for_user(self.user))
        self.access_token = str(RefreshToken(self.refresh_token).access_token)

        self.logout_url = reverse("users:jwt-logout")

    def test_logout_success(self):
        """
        Проверка успешного логаута с черным списком refresh token
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(
            self.logout_url, {"refresh": self.refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data["detail"], "Successfully logged out.")

    def test_logout_invalid_token(self):
        """
        Попытка логаута с неверным refresh token
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(
            self.logout_url, {"refresh": "wrongtoken"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token", response.data["error"])
