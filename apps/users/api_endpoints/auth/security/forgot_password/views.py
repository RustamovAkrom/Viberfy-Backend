# views.py
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import UserToken
from apps.users.services.email import send_password_reset_email
from .serializers import ForgotPasswordSerializer
from apps.users.models import User


class ForgotPasswordAPIView(APIView):
    """
    Отправка ссылки для сброса пароля пользователю по email.
    """

    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Creating a password reset token
        token = UserToken.objects.create(user=user, token_type="reset")

        # Sending password reset email
        send_password_reset_email(user, token.token)

        return Response(
            {"detail": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


__all__ = ("ForgotPasswordAPIView",)
