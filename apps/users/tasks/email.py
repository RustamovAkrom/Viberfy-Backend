from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_verification_email_task(email, link):
    send_mail(
        "Verify your email",
        f"Click to verify your email: {link}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


@shared_task
def send_password_reset_email_task(email, link):
    send_mail(
        "Reset your password",
        f"Click to reset your password: {link}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
