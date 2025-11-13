import requests

from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.text import slugify
from urllib.parse import urlencode

from apps.users.models import User


def _unique_username(base_name: str) -> str:
    """Генерация уникального username, если уже существует"""

    base = slugify(base_name) or "user"
    username = base
    i = 0

    while User.objects.filter(username=username).exists():
        i += 1
        username = f"{base}{i}"
    return username


class GoogleLoginView(APIView):
    """Redirects to Google OAuth consent screen"""

    permission_classes = [AllowAny]

    def get(self, request):
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            "?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            "&scope=openid%20email%20profile"
        )
        return redirect(google_auth_url)


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        # 1. Upon receiving the code, exchange it for access token
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        ).json()

        access_token = token_resp.get("access_token")
        if not access_token:
            return Response(
                {"error": "Failed to fetch access_token", "details": token_resp},
                status=400,
            )

        # 2. Get user info
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        email = user_info.get("email")
        name = user_info.get("name")

        if not email:
            return Response({"error": "No email returned from Google"}, status=400)

        # 3. Create or get user
        user = User.objects.filter(email=email).first()
        if user:
            created = False
        else:
            username = _unique_username(name or email.split("@")[0])
            user = User.objects.create_user(
                username=username, email=email, first_name=name or "", password=None
            )
            created = True

        # 4. Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        FRONTEND_REDIRECT = f"{settings.FRONTEND_URL}/auth/callback"
        query_params = urlencode(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": email,
                "name": name,
                "created": str(created).lower(),
            }
        )

        return redirect(f"{FRONTEND_REDIRECT}?{query_params}")


__all__ = (
    "GoogleLoginView",
    "GoogleCallbackView",
)
