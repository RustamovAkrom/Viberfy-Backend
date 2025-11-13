from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from apps.users.models import User, UserToken


class AuthAPITestCase(APITestCase):
    """Тесты для API авторизации и безопасности"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword",
            is_active=True,
            is_email_verified=False,
        )

        self.forgot_url = reverse("users:forgot-password")
        self.reset_url = reverse("users:reset-password")
        self.verify_url = reverse("users:verify-email")

    @patch(
        "apps.users.api_endpoints.auth.security.forgot_password.views.send_password_reset_email"
    )
    def test_forgot_password_success(self, mock_send_mail):
        """Успешная отправка ссылки для сброса пароля"""

        response = self.client.post(
            self.forgot_url, {"email": self.user.email}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password reset link sent", response.data["detail"])
        mock_send_mail.assert_called_once()  # Check that email sending function was called

    def test_forgot_password_invalid_email(self):
        """Ошибка при несуществующем email"""

        response = self.client.post(
            self.forgot_url, {"email": "wrong@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("does not exist", response.data["detail"])

    def test_reset_password_success(self):
        """Успешный сброс пароля"""

        user_token = UserToken.objects.create(user=self.user, token_type="reset")
        new_password = "newsecurepassword"

        response = self.client.post(
            self.reset_url,
            {"token": str(user_token.token), "new_password": new_password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password has been reset successfully", response.data["detail"])

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

        user_token.refresh_from_db()
        self.assertTrue(user_token.is_used)

    def test_reset_password_invalid_token(self):
        """Ошибка при некорректном UUID токене"""

        response = self.client.post(
            self.reset_url,
            {"token": "invalidtoken", "new_password": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('invalidtoken" Your UUID is not valid.', response.data["detail"])

    def test_reset_password_expired_token(self):
        """Ошибка при истекшем токене"""
        user_token = UserToken.objects.create(
            user=self.user, token_type="reset", is_used=False
        )
        user_token.is_used = True
        user_token.save()

        response = self.client.post(
            self.reset_url,
            {"token": str(user_token.token), "new_password": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token expired or already used", response.data["detail"])

    def test_verify_email_success(self):
        """Успешная верификация email"""

        token = str(RefreshToken.for_user(self.user).access_token)
        response = self.client.get(f"{self.verify_url}?token={token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_email_verified)

    def test_verify_email_invalid_token(self):
        """Ошибка при неверном токене"""

        response = self.client.get(f"{self.verify_url}?token=wrongtoken")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or expired token", response.data["detail"])

    def test_verify_email_missing_token(self):
        """Ошибка при отсутствии токена"""

        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token is required", response.data["detail"])
