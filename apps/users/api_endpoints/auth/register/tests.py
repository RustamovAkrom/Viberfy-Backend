from rest_framework.test import APITestCase
from apps.users.models import User


class RegisterAPITestCase(APITestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:8000/api/v1/users/auth/signup/"
        self.data = {
            "username": "TestUser",
            "email": "testuser@test.com",
            "password": "testpassword",
            "password2": "testpassword",
        }
        return super().setUp()

    def test_register(self):
        response = self.client.post(self.url, data=self.data)

        self.assertEqual(response.status_code, 201)
        data = response.json()

        # Test data with response data
        self.assertEqual(data["username"], self.data["username"])
        self.assertEqual(data["email"], self.data["email"])

        # Test user is exist in database
        user = User.objects.filter(id=data["id"]).first()

        self.assertIsNotNone(user, "User not found!")
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.email, data["email"])

        # Check user attributes
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        self.data["username"] = "TestUser"
        self.data["email"] = "testuser@test.com"
        self.data["password"] = "testpassword"
        self.data["password2"] = "testpassword"

        response = self.client.post(self.url, data=self.data)
        data = response.json()
        self.assertEqual(response.status_code, 400)

        self.data["username"] = "UniqueUsername"
        self.data["email"] = "uniqueemail@example.com"
        self.data["password"] = "password-fake-1"
        self.data["password"] = "password-fake-2"

        response = self.client.post(self.url, data=self.data)
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["password"][0], "Passwords do not match.")
