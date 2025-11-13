from ..models.tokens import UserToken


def create_token(user, token_type):
    return UserToken.objects.create(user=user, token_type=token_type)


def validate_token(token_str, token_type):
    try:
        token_obj = UserToken.objects.get(
            token=token_str, token_type=token_type, is_used=False
        )
        if token_obj.is_expired():
            return None
        return token_obj
    except UserToken.DoesNotExist:
        return None


def mark_token_used(token_obj):
    token_obj.is_used = True
    token_obj.save()
