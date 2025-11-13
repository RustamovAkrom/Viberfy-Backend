# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .serializers import MeSerializer


@extend_schema(
    tags=["Authentication"],
    summary="Get current user (lightweight)",
    description="Возвращает минимальную информацию о текущем пользователе.",
    responses=MeSerializer,
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


__all__ = ("MeView",)
