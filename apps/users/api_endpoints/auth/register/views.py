from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from apps.users.models import User
from .serializers import UserRegisterSerializer


@extend_schema(
    tags=["Authentication"],
    summary="User registration",
    description="Create a new user account by providing username, email and password.",
    request=UserRegisterSerializer,
    responses=UserRegisterSerializer,
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


__all__ = ("RegisterView",)
