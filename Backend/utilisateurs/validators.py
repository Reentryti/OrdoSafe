import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 12:
            raise ValidationError(
                _("Le mot de passe doit contenir au moins 12 caractères."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre majuscule."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre minuscule."),
                code='password_no_lower',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un chiffre."),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*()_+{}\[\]:;"\'<>,.?/~\\-]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un caractère spécial."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Le mot de passe doit contenir au moins 12 caractères, "
            "avec une majuscule, une minuscule, un chiffre et un caractère spécial (#, @, !, etc.)."
        )
