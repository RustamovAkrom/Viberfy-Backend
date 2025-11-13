from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(post=extend_schema(tags=["Authentication"]))
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(post=extend_schema(tags=["Authentication"]))
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema_view(post=extend_schema(tags=["Authentication"]))
class CustomTokenVerifyView(TokenVerifyView):
    pass
