from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Authentication"],
    summary="Logout user",
    description="Logs out the authenticated user by blacklisting the provided refresh token.",
    responses={
        205: {"type": "object", "example": {"detail": "Successfully logged out."}},
        400: {"type": "object", "example": {"error": "Token is invalid or expired"}},
    },
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


__all__ = ("LogoutView",)
