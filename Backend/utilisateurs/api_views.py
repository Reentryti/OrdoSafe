"""
API views for Vue.js frontend - session-based authentication.
"""
import json
import random
import hashlib
import base64
import qrcode
from io import BytesIO

from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Doctor, Patient, Pharmacist
from .forms import DoctorCreationForm, PharmacistCreationForm
from audit.utils import log_security_event

User = get_user_model()


def parse_json_body(request):
    """Parse JSON body from request, fallback to POST data."""
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return {}
    return request.POST


class CSRFTokenView(View):
    """Return CSRF token cookie for SPA."""
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return JsonResponse({'detail': 'CSRF cookie set'})


class APILoginView(View):
    """Unified login endpoint for all roles."""
    user_type = None

    def post(self, request):
        data = parse_json_body(request)
        email = data.get('email', '')
        password = data.get('password', '')

        user = authenticate(request, email=email, password=password)
        if user is None:
            return JsonResponse({'error': 'Identifiants incorrects'}, status=401)

        if not self._has_profile(user):
            return JsonResponse({'error': f'Ce compte n\'a pas de profil {self.user_type}'}, status=403)

        # Check account lock
        if user.is_account_locked():
            return JsonResponse({'error': 'Compte temporairement bloqué'}, status=423)

        # Check if 2FA is set up
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if device:
            request.session['2fa_user_id'] = user.id
            request.session['user_type'] = self.user_type
            return JsonResponse({'requires_2fa': True, 'user_type': self.user_type})

        # No 2FA configured - log in directly
        auth_login(request, user)
        return JsonResponse(self._user_data(user))

    def _has_profile(self, user):
        profile_map = {
            'doctor': 'doctor_profile',
            'patient': 'patient_profile',
            'pharmacist': 'pharmacist_profile',
        }
        attr = profile_map.get(self.user_type)
        return hasattr(user, attr) and getattr(user, attr, None) is not None

    def _user_data(self, user):
        data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'role': self.user_type,
        }
        if self.user_type == 'doctor' and hasattr(user, 'doctor_profile'):
            doc = user.doctor_profile
            data['specialisation'] = doc.specialisation
            data['licence_number'] = str(doc.licence_number)
        elif self.user_type == 'pharmacist' and hasattr(user, 'pharmacist_profile'):
            ph = user.pharmacist_profile
            data['pharmacy_name'] = ph.pharmacy_name
        return data


class DoctorAPILoginView(APILoginView):
    user_type = 'doctor'


class PharmacistAPILoginView(APILoginView):
    user_type = 'pharmacist'


class PatientAPILoginView(APILoginView):
    user_type = 'patient'


class APIVerify2FAView(View):
    """Verify 2FA token and complete login."""
    def post(self, request):
        data = parse_json_body(request)
        user_id = request.session.get('2fa_user_id')
        user_type = request.session.get('user_type')

        if not user_id:
            return JsonResponse({'error': 'Session 2FA expirée'}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur non trouvé'}, status=404)

        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        token = data.get('token', '')

        if not device or not device.verify_token(token):
            return JsonResponse({'error': 'Code 2FA invalide'}, status=401)

        auth_login(request, user)
        otp_login(request, device)
        del request.session['2fa_user_id']
        del request.session['user_type']

        # Build user data
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'role': user_type,
        }
        return JsonResponse(user_data)


class APISetup2FAView(LoginRequiredMixin, View):
    """Setup 2FA - returns QR code data."""
    def get(self, request):
        user = request.user
        device = TOTPDevice.objects.filter(user=user).first()

        if not device:
            device = TOTPDevice.objects.create(user=user, name='default')

        qr_code_url = device.config_url
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_image = base64.b64encode(buffer.getvalue()).decode()

        return JsonResponse({
            'qr_code_image': qr_code_image,
            'secret_key': device.key,
            'confirmed': device.confirmed,
        })

    def post(self, request):
        data = parse_json_body(request)
        user = request.user
        device = TOTPDevice.objects.filter(user=user).first()

        if not device:
            return JsonResponse({'error': 'Aucun dispositif trouvé'}, status=400)

        token = data.get('token', '')
        if not device.verify_token(token):
            return JsonResponse({'error': 'Code incorrect'}, status=400)

        device.confirmed = True
        device.save()

        # Generate backup codes
        backup_codes_plain = [str(random.randint(100000, 999999)) for _ in range(10)]
        hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes_plain]
        user.backup_codes = hashed_codes
        user.save()

        return JsonResponse({
            'success': True,
            'backup_codes': backup_codes_plain,
        })


class APISignupView(View):
    """Unified signup endpoint."""
    user_type = None
    form_class = None

    def post(self, request):
        data = parse_json_body(request)
        form = self.form_class(data)
        if form.is_valid():
            try:
                user = form.save()
                auth_login(request, user)
                return JsonResponse({
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'role': self.user_type,
                    'needs_2fa_setup': True,
                }, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'errors': form.errors}, status=400)


class DoctorAPISignupView(APISignupView):
    user_type = 'doctor'
    form_class = DoctorCreationForm


class PharmacistAPISignupView(APISignupView):
    user_type = 'pharmacist'
    form_class = PharmacistCreationForm


class APICurrentUserView(LoginRequiredMixin, View):
    """Get current authenticated user info."""
    def get(self, request):
        user = request.user
        role = None
        extra = {}

        if hasattr(user, 'doctor_profile') and user.doctor_profile:
            role = 'doctor'
            extra = {
                'specialisation': user.doctor_profile.specialisation,
            }
        elif hasattr(user, 'pharmacist_profile') and user.pharmacist_profile:
            role = 'pharmacist'
            extra = {
                'pharmacy_name': user.pharmacist_profile.pharmacy_name,
            }
        elif hasattr(user, 'patient_profile') and user.patient_profile:
            role = 'patient'

        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'phone_number': str(user.phone_number) if user.phone_number else None,
            'role': role,
            'has_2fa': TOTPDevice.objects.filter(user=user, confirmed=True).exists(),
            **extra,
        })


class APILogoutView(View):
    """Logout and clear session."""
    def post(self, request):
        auth_logout(request)
        return JsonResponse({'detail': 'Déconnecté avec succès'})
