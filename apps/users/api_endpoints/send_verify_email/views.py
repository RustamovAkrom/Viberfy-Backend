from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from apps.users.models import User
from apps.users.services.tokens import create_token
from apps.users.services.email import send_verification_email
from django.conf import settings


class SendVerifyEmailAPIView(APIView):
    """
    Отправка письма с подтверждением email через UserToken
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user: User = request.user

        if user.is_email_verified:
            return Response(
                {"detail": "Email уже подтверждён"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём токен через модель UserToken
        token_obj = create_token(user, token_type="verify")
        token_str = str(token_obj.token)

        # Отправка письма через Celery
        send_verification_email(user, token_str)

        return Response(
            {"detail": "Ссылка для подтверждения отправлена на вашу почту"},
            status=status.HTTP_200_OK,
        )


__all__ = ("SendVerifyEmailAPIView",)
