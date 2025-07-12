from django import forms
from .models import Ordonnance
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError
from datetime import date

class OrdonnanceForm(forms.Form):
    # Patient informations
    patient_first_name = forms.CharField(
        label="Prénom du patient",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    patient_last_name = forms.CharField(
        label='Nom du patient',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    patient_date_birth = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    patient_email = forms.EmailField(
        label='Email du patient',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'})
    )
    patient_phone = PhoneNumberField(
        label="Numéro de téléphone du patient", 
        region='SN',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '77 777 77 77'})
    )
    medicaments = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Saisissez les médicaments séparés par des virgules ou en allant à la ligne'
        }),
        label="Médicaments"
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Instructions complémentaires...'
        }),
        required=False,
        label="Notes et instructions"
    )

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

    def clean_patient_date_birth(self):
        birth_date = self.cleaned_data.get('patient_date_birth')
        if birth_date:
            if birth_date > date.today():
                raise ValidationError("La date de naissance ne peut pas être dans le futur.")
            
            age = (date.today() - birth_date).days / 365.25
            if age > 100:
                raise ValidationError("Date de naissance non valide.")

    def clean_medicaments(self):
        raw_meds = self.cleaned_data['medicaments']
        if not raw_meds.strip():
            raise ValidationError("Veuillez saisir au moins un médicament.")
        
        meds = []
        for line in raw_meds.split('\n'):
            line_meds = [m.strip() for m in line.split(',') if m.strip()]
            meds.extend(line_meds)
        
        if not meds:
            raise ValidationError("Format des médicaments invalide.")
        
        return [
            {"nom": med, "posologie": "", "duree": ""} 
            for med in meds
        ]

    def save(self, commit=True):
        if not self.doctor:
            raise ValidationError("Aucun médecin spécifié.")

        ordonnance = Ordonnance(
            patient_last_name=self.cleaned_data['patient_last_name'],
            patient_first_name=self.cleaned_data['patient_first_name'],
            patient_date_birth=self.cleaned_data['patient_date_birth'],
            patient_email=self.cleaned_data.get('patient_email', ''),
            patient_phone=str(self.cleaned_data['patient_phone']),
            medicaments=self.cleaned_data['medicaments'],
            notes=self.cleaned_data['notes'],
            doctor=self.doctor,
            created_by=self.doctor.user
        )

        if commit:
            ordonnance.save()
            ordonnance.sign(self.doctor)

        return ordonnance
