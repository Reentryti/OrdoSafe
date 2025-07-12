from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login
import random, qrcode, base64, hashlib
from .forms import PatientCreationForm, DoctorCreationForm, PharmacistCreationForm, Reset2FAForm
from rest_framework.views import View
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth import logout as auth_logout
from .models import Doctor, Patient, Pharmacist
from django.urls import reverse


from audit.utils import log_security_event

# Create your views here.
User = get_user_model()



## Common Configuration view

# 2FA Configuration View
@login_required
def setup_2fa(request):
    user = request.user
    device = TOTPDevice.objects.filter(user=user).first()

    if request.method == 'POST':
        if not device:
            messages.error(request, "Aucun dispositif trouvé")
            return redirect('setup_2fa')
        
        token = request.POST.get('token')

        if device.verify_token(token):
            device.confirmed = True
            device.save()
            #Plain text backup code generation
            backup_codes_plain = [str(random.randint(100000, 999999)) for _ in range(10)]
            #Hashed the backup codes
            hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes_plain]
            user.backup_codes = hashed_codes
            user.save()

            request.session['backup_codes'] = backup_codes_plain
            messages.success(request, "2FA activée avec succés")
            return redirect('backup_codes')
        else:
            messages.error(request, "Code incorrect")

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

    context = {
        'qr_code_url': qr_code_url,
        'qr_code_image': qr_code_image,
        'device':  device,
        'secret_key': device.key
    }

    return render(request, 'auth/setup_2fa.html', context)

# 2FA Backup Code
@login_required
def backup_codes(request):
    backup_codes = request.session.get('backup_codes')
    if not backup_codes:
        backup_codes = request.user.backup_codes
        if not backup_codes:
            messages.error(request, "Aucun code de sauvegarde disponible")
            return redirect('setup_2fa')
    
    
    if hasattr(request.user, 'doctor_profile'):
        dashboard_url = reverse('doctor_dash')
    elif hasattr(request.user, 'pharmacist_profile'):
        dashboard_url = reverse('pharmacist_dash')
    else:
        dashboard_url = reverse('pharmacist_dash')
    
    return render(request, 'auth/backup_codes.html', {
        'backup_codes': backup_codes,
        'dashboard_url': dashboard_url
    })



###############################
# Common Authentification Views

class BaseAuthView(View):
    #common paramaters define, help selecting role
    user_type = None
    template_login = None
    template_login_2fa = None
    template_signup = None
    form_class = None
    dashboard_url = None

    def get_user_profile_attr(self):
        return f"{self.user_type}_profile"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile_attr = self.get_user_profile_attr()
            profile = getattr(request.user, profile_attr, None)

            print(f"[DEBUG] Utilisateur connecté: {request.user.email}")
            print(f"[DEBUG] Rôle attendu: {self.user_type}, profil détecté: {type(profile).__name__ if profile else 'Aucun'}")

            if profile:
                print("[DEBUG] Rôle correct, redirection vers dashboard.")
                return redirect(self.dashboard_url)
            else:
                print("[DEBUG] Rôle incorrect, déconnexion et redirection vers login.")
                auth_logout(request)
                messages.warning(
                    request,
                    "Vous avez été déconnecté : vous ne pouvez pas accéder à cette page avec votre rôle actuel."
                )
                return redirect(f'{self.user_type}_login')

        return super().dispatch(request, *args, **kwargs)

    

# Common Login View
#@check_account_lock
class BaseLoginView(BaseAuthView):
    def get(self, request):
        return render(request, self.template_login)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        #print(f"Utilisateur authentifié: {user}")

        if user is not None:
            print(f"[DEBUG] Authentification réussie pour : {user.email}")
            if self.has_profile(user):
                print(f"[DEBUG] Rôle {self.user_type} confirmé pour : {user.email}")
                request.session['2fa_user_id'] = user.id
                request.session['user_type'] = self.user_type
                return redirect(f'{self.user_type}_login_2fa')
            else:
                print(f"[DEBUG] Mauvais rôle pour : {user.email}, accès refusé au rôle {self.user_type}")
        else:
            print(f"[DEBUG] Authentification échouée pour : {email}")

        messages.error(request, "Identifiants incorrects")
        return render(request, self.template_login)
    
    def has_profile(self, user):
        profile_attr = self.get_user_profile_attr()
        profile = getattr(user, profile_attr, None)
        
        if profile is None:
            return False

        expected_model = {
            'doctor_profile': Doctor,
            'patient_profile': Patient,
            'pharmacist_profile': Pharmacist
        }.get(profile_attr)

        return isinstance(profile, expected_model)

# Common 2FA View
class BaseLogin2faView(BaseAuthView):
    def get(self, request):
        user_id = request.session.get('2fa_user_id')
        if not user_id or request.session.get('user_type') != self.user_type:
            return  redirect(f'{self.user_type}_login')
        return render(request, self.template_login_2fa)

    def post(self, request):
        user_id = request.session.get('2fa_user_id')
        if not user_id or request.session.get('user_type') != self.user_type:
            return redirect(f'{self.user_type}_login')

        try:
            user = User.objects.get(id=user_id)
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

            token = request.POST.get('otp_token')
            if token and device.verify_token(token):
                auth_login(request, user)
                otp_login(request, device)
                del request.session['2fa_user_id']
                del request.session['user_type']
                return redirect(self.dashboard_url)

            messages.error(request, "Code 2fa invalide")
            return render(request, self.template_login_2fa)

        except User.DoesNotExist:
            messages.error(request, "Utilisateur non existant")
            return redirect(f'{self.user_type}_login')

# Common Sign Up View
class BaseSignupView(BaseAuthView):
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_signup, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                auth_login(request, user)
                messages.success(request, "Inscription Réussie")
                return redirect('setup_2fa')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
                
        return render(request, self.template_signup, {'form':form})

# Common Reset Password View
class Reset2FAView(LoginRequiredMixin, FormView):
    template_name = 'auth/reset_2fa.html'
    form_class = Reset2FAForm
    success_url = reverse_lazy('setup_2fa')

    def form_valid(self, form):
        user = self.request.user
        
        # 1. Supprimer les devices existants
        TOTPDevice.objects.filter(user=user).delete()
        
        # 2. Envoyer un email de confirmation
        send_mail(
            "Réinitialisation de votre 2FA",
            f"Votre authentification à deux facteurs a été réinitialisée.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        # 3. Déconnecter l'utilisateur
        auth_logout(self.request)
        
        messages.success(
            self.request,
            "La 2FA a été réinitialisée. Veuillez vous reconnecter et configurer une nouvelle authentification."
        )
        return super().form_valid(form)

#Common Logout view
class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        
        auth_logout(request)
        
        # Session clear
        if '2fa_user_id' in request.session:
            del request.session['2fa_user_id']
        if 'user_type' in request.session:
            del request.session['user_type']
        
        messages.success(request, "Vous avez été déconnecté avec succès.")
        
        # Redirection
        return redirect('home')  

#######################################
####### PATIENT VIEW ##################
#######################################
class PatientLoginView(BaseLoginView):
    user_type = 'patient'
    template_login = 'patients/login.html'
    dashboard_url = 'patient_dash'

class PatientLogin2faView(BaseLogin2faView):
    user_type = 'patient'
    template_login_2fa = 'auth/login_2fa.html'
    dashboard_url = 'patient_dash'

class PatientSignUpView(BaseSignupView):
    user_type = 'patient'
    template_signup = 'patients/signup.html'
    form_class = PatientCreationForm
    dashboard_url = 'patient_dash'

@login_required
def patient_dash(request):
    if not hasattr(request.user, 'patient_profile') or request.user.patient_profile is None:
        messages.error(request, "Acces non autorisé")
        return redirect('patient_login')
    return render(request, 'patients/dash.html')


########################################
####### DOCTOR VIEW  ###################
#######              ###################
class DoctorLoginView(BaseLoginView):
    user_type = 'doctor'
    template_login = 'doctors/login.html'
    dashboard_url = 'doctor_dash'

class DoctorLogin2faView(BaseLogin2faView):
    user_type = 'doctor'
    template_login_2fa = 'auth/login_2fa.html'
    dashboard_url = 'doctor_dash'

class DoctorSignUpView(BaseSignupView):
    user_type = 'doctor'
    template_signup = 'doctors/signup.html'
    form_class = DoctorCreationForm
    dashboard_url = 'doctor_dash'
    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object

        doctor, _ = Doctor.objects.get_or_create(user=user)

        if not doctor.private_key:
            doctor.generate_key_pair()
            doctor.save(update_fields=['private_key', 'public_key'])

        return response

@login_required
def doctor_dash(request):
    if not hasattr(request.user, 'doctor_profile') or request.user.doctor_profile is None:
        messages.error(request, "Acces non autorisé")
        return redirect('doctor_login')
    return render(request, 'doctors/dash.html')


########################################
####### PHARMACIST VIEW ################
#######                 ################
class PharmacistLoginView(BaseLoginView):
    user_type = 'pharmacist'
    template_login = 'pharmacist/login.html'
    dashboard_url = 'pharmacist_dash'

class PharmacistLogin2faView(BaseLogin2faView):
    user_type = 'pharmacist'
    template_login_2fa = 'auth/login_2fa.html'
    dashboard_url = 'pharmacist_dash'

class PharmacistSignUpView(BaseSignupView):
    user_type = 'pharmacist'
    template_signup = 'pharmacist/signup.html'
    form_class = PharmacistCreationForm
    dashboard_url = 'pharmacist_dash'

@login_required
def pharmacist_dash(request):
    if not hasattr(request.user, 'pharmacist_profile') or request.user.pharmacist_profile is None:
        messages.error(request, "Acces non autorisé")
        return redirect('pharmacist_login')
    return render(request, 'pharmacist/dash.html')