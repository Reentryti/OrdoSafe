from django import forms
from .models import Ordonnance
from utilisateurs.models import Patient
from phonenumber_field.formfields import PhoneNumberField

class OrdonnanceForm(forms.ModelForm):
    patient_phone = PhoneNumberField(
        label="Numero de téléphone du patient", 
        region='SN',
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'77 777 77 77'
        }))
    medicaments = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Exemple:\nParacétamol 1000mg - 1 comprimé toutes les 6 heures - 3 jours\nIbuprofène 400mg - 1 comprimé 3x/jour après les repas - 5 jours'
        }),
        label="Médicaments et posologie",
        help_text="Saisissez chaque médicament sur une ligne séparée"
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Instructions complémentaires, conseils au patient...'
        }),
        required=False,
        label="Notes et instructions"
    )

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        print("Champs du formulaire :", self.fields.keys())

    def clean_patient_phone(self):
        phone_number = self.cleaned_data['patient_phone']
        try:
            patient = Patient.objects.get(user__phone_number=phone_number)
        except Patient.DoesNotExist:
            raise forms.ValidationError("Aucun patient avec ce numéro de téléphone")
        return patient
    
    def clean_medicaments(self):
        medicaments_text = self.cleaned_data.get('medicaments')
        if not medicaments_text:
            raise forms.ValidationError("Veuillez saisir au moins un médicament.")
        
        # Conversion on A JSON
        medicaments_list = []
        lines = medicaments_text.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
      
            parts = [part.strip() for part in line.split(' - ')]
            
            if len(parts) >= 1:
                medicament = {
                    "id": i,
                    "nom": parts[0],
                    "posologie": parts[1] if len(parts) > 1 else "",
                    "duree": parts[2] if len(parts) > 2 else "",
                    "texte_complet": line
                }
                medicaments_list.append(medicament)
            else:
                medicament = {
                    "id": i,
                    "nom": line,
                    "posologie": "",
                    "duree": "",
                    "texte_complet": line
                }
                medicaments_list.append(medicament)
        
        if not medicaments_list:
            raise forms.ValidationError("Aucun médicament valide détecté.")
            
        return medicaments_list 
        
    def save(self, commit=True):
        ordonnance = super().save(commit=False)
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