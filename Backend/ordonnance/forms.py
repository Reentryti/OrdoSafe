from django import forms
from .models import Ordonnance

class OrdonnanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        
        #if doctor:
        #   self.fields['patient'].queryset = Patient.objects.all()
    
    class Meta:
        model = Ordonnance
        fields = ['patient', 'medicaments', 'notes']
        widgets = {
            'medicaments': forms.Textarea(attrs={'rows': 5}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }