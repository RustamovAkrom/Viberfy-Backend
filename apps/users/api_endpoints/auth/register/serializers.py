from rest_framework import serializers
from apps.users.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.users.services.tokens import create_token
from apps.users.services.email import send_verification_email


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.is_email_verified = False
        user.save()

        # Create activation token
        token_obj = create_token(user, token_type="verify")
        token_str = str(token_obj.token)
        # Send verification email
        send_verification_email(user, token_str)

        return user
