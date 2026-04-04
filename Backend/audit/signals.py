from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
)
from audit.models import AuditLog
from audit.utils import get_client_ip

User = get_user_model()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ActionTypes.LOGIN,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        metadata={
            'via': 'form',
            'user_type': getattr(user, 'user_type', 'unknown'),
            'session_id': request.session.session_key
        }
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        user=User.objects.filter(email=credentials.get('email')).first(),
        action=AuditLog.ActionTypes.LOGIN_FAILED,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        metadata={
            'email_attempt': credentials.get('email'),
            'session_id': request.session.session_key if hasattr(request, 'session') else None
        }
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ActionTypes.LOGOUT,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        metadata={
            'session_id': request.session.session_key
        }
    )

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance,
            action=AuditLog.ActionTypes.USER_CREATION,
            metadata={
                'created_by': getattr(instance, 'created_by', 'system'),
                'user_type': getattr(instance, 'user_type', 'unknown')
            }
        )