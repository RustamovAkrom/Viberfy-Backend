import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.users.models import UserToken
from .serializers import ResetPasswordSerializer


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not token or not new_password:
            return Response(
                {"detail": "Token and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if token is a valid UUID
        try:
            uuid.UUID(str(token))
        except (ValueError, TypeError, AttributeError):
            return Response(
                {"detail": f'"{token}" Your UUID is not valid.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate token and get associated user
        try:
            user_token = UserToken.objects.get(token=token, token_type="reset")
        except UserToken.DoesNotExist:
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user_token.is_expired() or user_token.is_used:
            return Response(
                {"detail": "Token expired or already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = user_token.user
        user.set_password(new_password)
        user.save()

        user_token.is_used = True
        user_token.save()

        return Response(
            {"detail": "Password has been reset successfully"},
            status=status.HTTP_200_OK,
        )


__all__ = ["ResetPasswordAPIView"]
