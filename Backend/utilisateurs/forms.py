from django import forms
from .models import Patient


# Form patient
class PatientForm(forms.ModelForm):
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

    class Meta: 
        model = Patient
        fiels = ['weight', 'blood_type', 'allergies']