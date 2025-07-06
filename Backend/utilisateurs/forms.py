from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, BasicUser, Doctor, Pharmacist
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import datetime
from phonenumber_field.formfields import PhoneNumberField
from django.db import transaction
from django.forms import PasswordInput
from django.contrib.auth.password_validation import password_validators_help_text_html


# Forms Control (Patient input)
class PatientCreationForm(UserCreationForm):

    first_name = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    last_name = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    date_birth = forms.DateField(
        label="Date de naissance",
        required=True,
        widget=forms.DateInput(attrs={
            'class':'form-control',
            'type':'date',
            'max':datetime.date.today().strftime('%Y-%m-%d')
        })
    )
    email = forms.EmailField(
        label="Adresse email",
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class':'form-control'})
    )
    phone_number = PhoneNumberField(
        label="Numero de téléphone",
        region='SN',
        required=False,
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'77 777 77 77'
        })
    )
    two_factor_method = forms.ChoiceField(
        label="Méthode d'authentification à deux facteurs",
        choices=[('email', 'Email'), ('sms', 'SMS')],
        initial='email',
        widget=forms.Select(attrs={'class':'form-select'})
    )
    weight = forms.IntegerField(
        label="Poids(kg)",
        min_value=1,
        max_value=500,
        widget=forms.NumberInput(attrs={'class':'form-control'}))
    blood_type = forms.ChoiceField(
        label="Groupe sanguin",
        choices=[('A+', 'A+'),
                 ('A-', 'A-'),
                 ('B+', 'B+'),
                 ('B-', 'B-'),
                 ('O+', 'O+'),
                 ('O-', 'O-'),
                 ('AB+', 'AB+'),
                 ('AB-', 'AB-')
        ],
        widget=forms.Select(attrs={'class':'form-select'}))
    allergies = forms.CharField(
        label="Allergies",
        required=False,
        widget=forms.Textarea(attrs={
            'class':'form-control', 
            'rows':3, 
            'placeholder':'Renseignez les allergies connues séparées dune virgule'})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )

    class Meta:
        model = BasicUser
        fields = [
            'first_name', 'last_name', 'date_birth', 'email', 'phone_number', 'two_factor_method', 'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BasicUser.objects.filter(email=email).exists():
            raise ValidationError("Utilisateur deja existant")
        return email
    
    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    self.fields['password1'].help_text = password_validators_help_text_html()
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if BasicUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Utilisateur deja existant")
        return phone_number

    def clean_date_birth(self):
        date_birth = self.cleaned_data.get('date_birth')
        if date_birth:
            today = datetime.date.today()
            age = today.year - date_birth.year - ((today.month, today.day) < (date_birth.month, date_birth.day))
            if age < 0:
                raise ValidationError("La date de naissance ne peut pas être dans le futur")
            if age > 150:
                raise ValidationError("Âge invalide")
        return date_birth

    def save(self, commit=True):
        # Specific user field 
        # Debug
        
        #print("Date de naissance:", self.cleaned_data.get('date_birth'))
        #print("Type:", type(self.cleaned_data.get('date_birth')))
        #print("Est None?", self.cleaned_data.get('date_birth') is None)
        #print("Toutes les données:", self.cleaned_data)
        
        with transaction.atomic(): # Solve storing wrong forms   
            user = BasicUser.objects.create_user(
                #user_type= 'patient',
            email= self.cleaned_data['email'],
            password= self.cleaned_data['password1'],
            date_birth= self.cleaned_data['date_birth'])

            user.first_name= self.cleaned_data['first_name']
            user.last_name= self.cleaned_data['last_name']
            user.phone_number= self.cleaned_data['phone_number']
            user.two_factor_method= self.cleaned_data['two_factor_method']
            user.save()
                
            # Specific patient field (for integration btw them)
            patient = Patient.objects.create(
                user= user,
                weight= self.cleaned_data['weight'],
                blood_type= self.cleaned_data['blood_type'],
                allergies= self.cleaned_data['allergies']
            )
            return user
        

# Form Control (Doctor input)
class DoctorCreationForm(UserCreationForm):

    first_name = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    last_name = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    date_birth = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={
            'class':'form-control',
            'type':'date',
            'max':datetime.date.today().strftime('%Y-%m-%d')
        })
    )
    email = forms.EmailField(
        label="Adresse email",
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class':'form-control'})
    )
    phone_number = PhoneNumberField(
        label="Numero de téléphone",
        region='SN',
        required=True,
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'77 777 77 77'
        })
    )
    two_factor_method = forms.ChoiceField(
        label="Méthode d'authentification à deux facteurs",
        choices=[('email', 'Email'), ('sms', 'SMS')],
        initial='email',
        widget=forms.Select(attrs={'class':'form-select'})
    )
    licence_number = forms.CharField(
        label="Numéro de licence",
        max_length=30,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    specialisation = forms.CharField(
        label="Spécialisation",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )

    class Meta:
        model = BasicUser
        fields = [
            'first_name', 'last_name', 'date_birth', 'email', 'phone_number', 'two_factor_method', 'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BasicUser.objects.filter(email=email).exists():
            raise ValidationError("Utilisateur existant")
        return email
    
    def save(self, commit=True):
        with transaction.atomic():
            user = BasicUser.objects.create_user(
            #user_type= 'doctor',
                email= self.cleaned_data['email'],
                password= self.cleaned_data['password1'],
                date_birth= self.cleaned_data['date_birth'])

            user.first_name= self.cleaned_data['first_name']
            user.last_name= self.cleaned_data['last_name']
            user.phone_number= self.cleaned_data['phone_number']
            user.two_factor_method= self.cleaned_data['two_factor_method']
            user.save()

            doctor = Doctor.objects.create(
                user=user,
                licence_number= self.cleaned_data['licence_number'],
                specialisation= self.cleaned_data['specialisation']
            )
            return user
       

# Form Control (Pharmacist input)
class PharmacistCreationForm(UserCreationForm):

    first_name = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    last_name = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    date_birth = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={
            'class':'form-control',
            'type':'date',
            'max':datetime.date.today().strftime('%Y-%m-%d')
        })
    )
    email = forms.EmailField(
        label="Adresse email",
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class':'form-control'})
    )
    phone_number = PhoneNumberField(
        label="Numero de téléphone",
        region='SN',
        required=False,
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'77 777 77 77'
        })
    )
    two_factor_method = forms.ChoiceField(
        label="Méthode d'authentification à deux facteurs",
        choices=[('email', 'Email'), ('sms', 'SMS')],
        initial='email',
        widget=forms.Select(attrs={'class':'form-select'})
    )
    licence_number = forms.CharField(
        label="Numéro de licence",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    pharmacy_name = forms.CharField(
        label="Nom de la pharmacie",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )

    class Meta:
        model = BasicUser
        fields = [
            'first_name', 'last_name', 'date_birth', 'email', 'phone_number', 'two_factor_method', 'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BasicUser.objects.filter(email=email).exists():
            raise ValidationError("Utilisateur existant")
        return email

    def save(self, commit=True):
        
        with transaction.atomic():
            user = BasicUser.objects.create_user(
                    #user_type= 'pharmacist',
                email= self.cleaned_data['email'],
                password= self.cleaned_data['password1'],
                date_birth= self.cleaned_data['date_birth'])

            user.first_name= self.cleaned_data['first_name']
            user.last_name= self.cleaned_data['last_name']
            user.phone_number= self.cleaned_data['phone_number']
            user.two_factor_method= self.cleaned_data['two_factor_method']
            user.save()
                
            pharmacist = Pharmacist.objects.create(
                user=user, 
                licence_number= self.cleaned_data['licence_number'],
                pharmacy_name= self.cleaned_data['pharmacy_name']
            )
            return user
            
    
# Form Reset Password
class Reset2FAForm(forms.Form):
    password = forms.CharField(
        label="Confirmez avec votre mot de passe",
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe actuel'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Mot de passe incorrect")
        return password