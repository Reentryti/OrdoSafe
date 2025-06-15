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

        if device.verity_token(token):
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
    qr_code_image = base64.b64decode(buffer.getValue()).decode()

    context = {
        'qr_code_url': qr_code_url,
        'qr_code_image': qr_code_image,
        'device':  device,
        'secret_key': device.key
    }

    return render(request, 'utilisateurs/setup_2fa.html', context)

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

# Create your views here.
#######################################
####### PATIENT VIEW ##################
#######################################

# Standard Login View
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.session['2fa_user_id'] = user.id
            return redirect('login_2fa')
        else:
            messages.error(request, "Identifiants incorrects")
    return render(request, 'utilisateurs/login.html')

# 2FA Login View
def login_2fa(request):
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user = User.objects.get(id=user_id)
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if not device:
            messages.error(request, "Aucun dispositif pour la 2FA")
            return redirect('login')

        if request.method == 'POST':
            token =  request.POST.get('otp_token')
            backup_code = request.POST.get('backup_codes')

            if token and device.verify_token(token):
                auth_login(request, user)
                otp_login(request, device)
                del request.session['2fa_user_id']
                messages.success(request, "Connexion réussie")
                return redirect('home')
            elif backup_code and user.backup_codes:
                if backup_code in user.backup_codes:
                    user.backup_codes.remove(backup_code)
                    user.save()
                    auth_login(request, user)
                    otp_login(request, device)
                    del request.session['2fa_user_id']
                    messages.error(request, "Connexion réussie avec code de sauvegarde")
                    return redirect('home')
                else:
                    messages.error(request, "Code de sauvegarde incorrect")
            else :
                messages.error(request, "Code 2fa incorrect")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable")
        return redirect('login')
    
    return render(request, 'utilisateurs/login_2fa.html')

# Registration class
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie")
            return redirect('setup_2fa')
    else:
        form = UserCreationForm()

    return render(request, 'utilisateurs/signup.html', {'form': form})


########################################
####### DOCTOR VIEW  ###################
#######              ###################

# Login View
def doctor_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None and hassattr(user, 'doctor_profile'):
            request.session['2fa_user_id'] = user.id
            return redirect('doctor_login_2fa')
        else:
            messages.error(reqest,'Identifiants incorrects')
    return render(request, 'doctors/login.html')

# 2fa View
def doctor_login_2fa(request):
    user_id = request.sesssion.get('2fa_user_id')
    if not user_id:
        return redirect('doctor_login')

    try:
        user = User.objects.get(id=user_id)
        if not hasattr(user, 'doctor_profile'):
            messages.error(request, "No access")
            return redirect('doctor_login')

        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if request.method == 'POST':
            token = request.POST.get('otp_token')
            if token and device.verify_token(token):
                auth_login(request, user)
                otp_login(request, device)
                del request.session['2fa_user_id']
                return redirect('dash')
            else:
                messages.error(request, "Code 2fa incorrect")
    except User.DoesNotExist:
        messages.error(request, "utilisateur introuvable")

    return render(request, 'doctors/login_2fa.html')

# Signup View
def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorCreationForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            auth_login(request, doctor.user)
            messages.success(request, "Inscription du médecin réussie")
            return redirect('setup_2fa')
    else:
        form = DoctorCreationForm()
    
    return render(request, 'doctors/signup.html', {'form':form})

# Dashboard redirection view
@login_required
def doctor_dash(request):
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    return render(request, 'doctors/dashboard.html')
    
########################################
####### PHARMACIST VIEW ################
#######                 ################

# Login View
def pharmacist_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None and hasattr(user, 'pharmacist_profile'):
            request.session['2fa_user_id'] = user.id
            return redirect('pharmacist_login_2fa')
        else:
            messages.error(request, 'Identifiants incorrects')
    return render(request, 'pharmacist/login.html')

# 2fa View
def pharmacist_login_2fa(request):
    user_id = request.sesssion.get('2fa_user_id')
    if not user_id:
        return redirect('pharmacist_login')

    try:
        user = User.objects.get(id=user_id)
        if not hasattr(user, 'pharmacist_profile'):
            messages.error(request, "No access")
            return redirect('pharmacist_login')

        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if request.method == 'POST':
            token = request.POST.get('otp_token')
            if token and device.verify_token(token):
                auth_login(request, user)
                otp_login(request, device)
                del request.session['2fa_user_id']
                return redirect('dash')
            else:
                messages.error(request, "Code 2fa incorrect")
    except User.DoesNotExist:
        messages.error(request, "utilisateur introuvable")

    return render(request, 'pharmacist/login_2fa.html')

# Signup view
def pharmacist_signup(request):
    if request.method == 'POST':
        form = PharmacistCreationForm(request.POST)
        if form.is_valid():
            pharmacist = form.save()
            auth_login(request, pharmacist.user)
            messages.success(request, "Inscription du pharmacien réussie")
            return redirect('setup_2fa')
    else:
        form = PharmacistCreationForm()

    return render(resquest, 'pharmacist/signup.html', {'form':form})

# Dashboard redirection view
@login_required
def pharmacist_dash(request):
    if not hasattr(request.user, 'pharmacist_profile'):
        return redirect('home')
    return render(request, 'pharmacist/dashboard.html')