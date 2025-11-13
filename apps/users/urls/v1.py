from django.urls import path, include


from apps.users.api_endpoints.auth import (
    LogoutView,
    RegisterView,
    MeView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)
from apps.users.api_endpoints.social_auth import (
    GoogleLoginView,
    GoogleCallbackView,
)
from apps.users.api_endpoints.auth.security import (
    ResetPasswordAPIView,
    ForgotPasswordAPIView,
    VerifyEmailAPIView,
)
from apps.users.api_endpoints.send_verify_email import SendVerifyEmailAPIView
from apps.users.api_endpoints.profile import ProfileView

app_name = "users"

auth_patterns = [
    path("jwt/create/", CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", CustomTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", CustomTokenVerifyView.as_view(), name="jwt-verify"),
    path("jwt/logout/", LogoutView.as_view(), name="jwt-logout"),
    path("signup/", RegisterView.as_view(), name="signup"),
]

social_auth_patterns = [
    path("auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path("auth/google/callback/", GoogleCallbackView.as_view(), name="google-callback"),
]

password_confirmation_patterns = [
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
]

urlpatterns = [
    path(
        "send-verify-email/", SendVerifyEmailAPIView.as_view(), name="send-verify-email"
    ),
    path("auth/", include(auth_patterns)),
    path("social-auth/", include(social_auth_patterns)),
    path("passwords/", include(password_confirmation_patterns)),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
