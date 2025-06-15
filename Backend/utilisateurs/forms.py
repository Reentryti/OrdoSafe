from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, BasicUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import datetime
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widget import PhoneNumberPrefixWidget


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
        widget=forms.DateInput(attrs={
            'class':'form-control',
            'type':'date',
            'max':datetime.date.today().strftime('%d-%m-%Y')
        })
    )
    email = forms.EmailField(
        label="Adresse email",
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class':'form-control'})
    )
    phone_number = forms.PhoneNumberField(
        label="Numero de téléphone",
        region='SN',
        required=False,
        widget=PhoneNumberPrefixWidget(attrs={
            'class':'form-contrl',
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
            'row':3, 
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
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_birth', 'email', 'phone_number', 'two_factor_method', 'weight', 'blood_type', 'allergies', 'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BasicUser.objects.filter(email=email).exists():
            raise ValidationError("Utilisateur deja existant")
        return email

    def save(self, commit=True):
        # Specific user field 
        user = BasicUser.objects.create_user(
            user_type= 'patient',
            email= self.cleaned_data['email'],
            password= self.cleaned_data['password'],
            first_name= self.cleaned_data['first_name'],
            last_name= self.cleaned_data['last_name'],
            date_birth= self.cleaned_data['date_birth'],
            phone_number= self.cleaned_data['phone_number'],
            two_factor_method= self.cleaned_data['two_factor_method']
        )
        # Specific patient field (for integration btw them)
        patient = Patient.objets.create(
            user= user,
            weight= self.cleaned_data['weight'],
            blood_type= self.cleaned_data['blood_type'],
            allergies= self.cleaned_data['allergies']
        )
        return patient


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
            'max':datetime.date.today().strftime('%d-%m-%Y')
        })
    )
    email = forms.EmailField(
        label="Adresse email",
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class':'form-control'})
    )
    phone_number = forms.PhoneNumberField(
        label="Numero de téléphone",
        region='SN',
        required=False,
        widget=PhoneNumberPrefixWidget(attrs={
            'class':'form-contrl',
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
        model = Doctor
        fields = [
            'first_name', 'last_name', 'date_birth', 'email', 'phone_number', 'two_factor_method', 'licence_number', 'specialisation', 'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if BasicUser.objects.filter(email=email).exists():
            raise ValidationError("Utilisateur existant")
        return email
    
    def save(self, commit=True):
        user = BasicUser.objects.create_user(
            user_type= 'doctor',
            email= self.cleaned_data['email'],
            password= self.cleaned_data['password'],
            first_name= self.cleaned_data['first_name'],
            last_name= self.cleaned_data['last_name'],
            date_birth= self.cleaned_data['date_birth'],
            phone_number= self.cleaned_data['phone_number'],
            two_factor_method= self.cleaned_data['two_factor_method']
        )
        doctor = Doctor.objects.create(
            user=user,
            licence_number= self.cleaned_data['licence_number'],
            specialisation= self.cleaned_data['specialisation']
        )
    return doctor


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
            'max':datetime.date.today().strftime('%d-%m-%Y')
        })
    )
    email = forms.EmailField(
        label="Adresse email",
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class':'form-control'})
    )
    phone_number = forms.PhoneNumberField(
        label="Numero de téléphone",
        region='SN',
        required=False,
        widget=PhoneNumberPrefixWidget(attrs={
            'class':'form-contrl',
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
        model = Pharmacist
        fields = [
            'first_name', 'last_name', 'date_birth', 'email', 'phone_number', 'two_factor_method', 'licence_number', 'pharmacy_name', 'password1', 'password2'
        ]
    
    def clear_email(self):
        email = self.cleaned_data.get('email')
        if BasicUser.objects.filter(email=email).exists():
            raise ValidationError("Utilisateur existant")
        return email

    def save(self, commit=True):
        user = BasicUser.objects.create_user(
            user_type= 'pharmacist',
            email= self.cleaned_data['email'],
            password= self.cleaned_data['password'],
            first_name= self.cleaned_data['first_name'],
            last_name= self.cleaned_data['last_name'],
            date_birth= self.cleaned_data['date_birth'],
            phone_number= self.cleaned_data['phone_number'],
            two_factor_method= self.cleaned_data['two_factor_method']
        )
        pharmacist = Pharmacist.objects.create(
            user=user, 
            licence_number= self.cleaned_data['licence_number'],
            pharmacy_name= self.cleaned_data['pharmacy_name']
        )
    return pharmacist