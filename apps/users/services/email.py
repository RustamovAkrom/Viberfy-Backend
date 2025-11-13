from django.core.mail import send_mail
from django.conf import settings
from apps.users.tasks import (
    send_verification_email_task,
    send_password_reset_email_task,
)


def send_verification_email(user, token):
    link = f"{settings.FRONTEND_URL}/verify-email?token={str(token)}/"
    try:
        send_verification_email_task.delay(user.email, link)
    except Exception as e:
        print(f"[Task]: Failed to send verification email: {e}")
        print("Sending Email with Django's send_mail function as a fallback.")
        send_mail(
            "Verify your email",
            f"Click the link to verify your email: {link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )


def send_password_reset_email(user, token):
    link = f"{settings.FRONTEND_URL}/reset-password/?token={str(token)}/"
    try:
        send_password_reset_email_task.delay(user.email, link)
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"[Task]: Failed to send password reset email: {e}")
        print("Sending Email with Django's send_mail function as a fallback.")
        send_mail(
            "Reset your password",
            f"Click the link to reset your password: {link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )


__all__ = (
    "send_verification_email",
    "send_password_reset_email",
)
