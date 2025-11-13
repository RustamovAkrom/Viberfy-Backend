# views.py
from rest_framework import generics, permissions, parsers
from drf_spectacular.utils import extend_schema
from .serializers import ProfileSerializer


@extend_schema(
    tags=["Profile"],
    summary="Get or update profile",
    description="Возвращает и обновляет данные профиля текущего пользователя.",
    responses=ProfileSerializer,
)
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def get_object(self):
        return self.request.user


__all__ = ["ProfileView"]
