from django import forms
from .models import Ordonnance
from utilisateurs.models import Patient

class OrdonnanceForm(forms.ModelForm):
    patient_phone = forms.CharField(label="Numero de téléphone du patient")

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

    def clean_patient_phone(self):
        phone_number = self.cleaned_data['patient_phone']
        try:
            patient = Patient.objects.get(phone_number=phone_number)
        except Patient.DoesNotExist:
            raise forms.ValidationError("Aucun patient avec ce numéro de téléphone")
        return patient
        
    def save(self, commit=True):
        ordonnance = super.save(commit=False)
        ordonnance.patient = self.cleaned_data['patient_phone']
        if commit:
            ordonnance.save()
        return ordonnance
        #if doctor:
        #   self.fields['patient'].queryset = Patient.objects.all()
    
    class Meta:
        model = Ordonnance
        fields = ['patient_phone', 'medicaments', 'notes']
        widgets = {
            'medicaments': forms.Textarea(attrs={'rows': 5}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }