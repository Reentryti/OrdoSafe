from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login
import random
import qrcode
import base64
from .forms import PatientCreationForm, DoctorCreationForm, PharmacistCreationForm
from rest_framework.views import View
from io import BytesIO
from django.http import HttpResponse

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

            backup_codes = [str(random.randint(100000, 999999)) for _ in range(10)]
            user.backup_codes = backup_codes
            user.save()

            request.session['backup_codes'] = backup_codes
            messages.success(request, "2FA activée avec succés")
            return redirect('backp_codes')
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
    
    return render(request, 'backup_codes.html', {'backup_codes': backup_codes})


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
        if hasattr(request.user, self.get_user_profile_attr()):
            return redirect(self.dash_url)
        return super().dispatch(request, *args, *kwargs)

# Common Login View
#@check_account_lock
class BaseLoginView(BaseAuthView):
    def get(self, request):
        return render(request, self.template_login)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None and hasattr(user, self.get_user_profile_attr()):
            request.session['2fa_user_id'] = user.id
            request.session['user_type'] = self.user_type
            return redirect(f'{self.user_type}_login_2fa')

        messages.error(request, "Identifiants incorrects")
        return render(request, self.template_login)

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
                return redirect(self.dash_url)

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



#######################################
####### PATIENT VIEW ##################
#######################################
class PatientLoginView(BaseLoginView):
    user_type = 'patient'
    template_login = 'patients/login.html'
    dash_url = 'patient_dash'

class PatientLogin2faView(BaseLogin2faView):
    user_type = 'patient'
    template_login_2fa = 'patients/login_2fa.html'
    dash_url = 'patient_dash'

class PatientSignUpView(BaseSignupView):
    user_type = 'patient'
    template_signup = 'patients/signup.html'
    form_class = PatientCreationForm
    dash_url = 'patient_dash'

@login_required
def patient_dash(request):
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    return render(request, 'patient/dashboard.html')


########################################
####### DOCTOR VIEW  ###################
#######              ###################
class DoctorLoginView(BaseLoginView):
    user_type = 'doctor'
    template_login = 'doctor/login.html'
    dash_url = 'doctor_dash'

class DoctorLogin2faView(BaseLogin2faView):
    user_type = 'doctor'
    template_login_2fa = 'doctor/login_2fa.html'
    dash_url = 'doctor_dash'

class DoctorSignUpView(BaseSignupView):
    user_type = 'doctor'
    template_signup = 'doctor/signup.html'
    form_class = DoctorCreationForm
    dash_url = 'doctor_dash'

@login_required
def doctor_dash(request):
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    return render(request, 'doctor/dashboard.html')


########################################
####### PHARMACIST VIEW ################
#######                 ################
class PharmacistLoginView(BaseLoginView):
    user_type = 'pharmacist'
    template_login = 'auth/login.html'
    dash_url = 'pharmacist_dash'

class PharmacistLogin2faView(BaseLogin2faView):
    user_type = 'pharmacist'
    template_login_2fa = 'auth/login_2fa.html'
    dash_url = 'pharmacist_dash'

class PharmacistSignUpView(BaseSignupView):
    user_type = 'pharmacist'
    template_signup = 'auth/signup.html'
    form_class = PharmacistCreationForm
    dash_url = 'pharmacist_dash'

@login_required
def pharmacist_dash(request):
    if not hasattr(request.user, 'pharmacist_profile'):
        return redirect('home')
    return render(request, 'pharmacist/dashboard.html')