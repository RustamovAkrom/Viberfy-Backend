from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from apps.users.models import User
from apps.users.services.tokens import validate_token, mark_token_used


class VerifyEmailAPIView(APIView):
    """
    Подтверждение email пользователя через токен.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        token_obj = validate_token(token, token_type="verify")
        if not token_obj:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = token_obj.user
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        mark_token_used(token_obj)

        return Response(
            {"detail": "Email verified successfully"}, status=status.HTTP_200_OK
        )


__all__ = ("VerifyEmailAPIView",)
