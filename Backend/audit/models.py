from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Create your models here.

User = get_user_model()

class AuditLog(models.Model):
    class ActionTypes(models.TextChoices):
        #Auth Log
        LOGIN = 'login', _('Connexion')
        LOGIN_FAILED = 'login_failed', _('Échec de connexion')
        LOGOUT = 'logout', _('Déconnexion')
        TWO_FACTOR_SUCCESS = '2fa_success', _('2FA réussie')
        TWO_FACTOR_FAILED = '2fa_failed', _('2FA échouée')
        PASSWORD_CHANGE = 'password_change', _('Changement de mot de passe')
        USER_CREATION = 'user_creation', _('Création de compte')
        PROFILE_UPDATE = 'profile_update', _('Mise à jour du profil')
        SECURITY_SETTING_CHANGE = 'security_change', _('Modification de sécurité')
        #Ordo CRUD Log
        ORDONNANCE_CREATION = 'ordonnance_creation', _('Création ordonnance')
        ORDONNANCE_MODIFICATION = 'ordonnance_modification', _('Modification ordonnance')
        ORDONNANCE_VALIDATION = 'ordonnance_validation', _('Validation ordonnance')
        ORDONNANCE_ANNULATION = 'ordonnance_annulation', _('Annulation ordonnance')

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Utilisateur')
    )
    action = models.CharField(
        max_length=50,
        choices=ActionTypes.choices,
        verbose_name=_('Action')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Adresse IP')
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('User Agent')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Horodatage')
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Métadonnées')
    )

    class Meta:
        verbose_name = _('Entrée de journal')
        verbose_name_plural = _('Journal des audits')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.user or 'System'} - {self.timestamp}"