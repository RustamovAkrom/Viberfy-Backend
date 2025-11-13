# serializers.py
from rest_framework import serializers
from apps.users.models import User


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "subscription_type",
            "is_email_verified",
            "is_active",
        )
        read_only_fields = ("email", "username")
