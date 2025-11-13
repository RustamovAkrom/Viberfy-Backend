from rest_framework.serializers import Serializer, CharField, UUIDField


class ResetPasswordSerializer(Serializer):
    token = UUIDField()
    new_password = CharField(
        write_only=True, min_length=8, max_length=128, required=True
    )
