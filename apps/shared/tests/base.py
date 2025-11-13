from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.admin_username = "Admin"
        self.admin_password = "admin"
        self.admin_email = "admin@example.com"
        self.client.headers = {}

    def create_user(self, username, email, passsword):
        user = User(
            username=username,
            email=email,
        )
        user.set_password(str(passsword))
        user.save()
        return user

    def get_token(self):
        user = self.create_user(
            username=self.admin_username,
            email=self.admin_email,
            passsword=self.admin_password,
        )
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return access_token

    def set_token_to_headers(self, token: str):
        self.client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"bearer {token}",
        }
