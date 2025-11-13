from rest_framework.serializers import Serializer, EmailField


class ForgotPasswordSerializer(Serializer):
    email = EmailField(required=True)
