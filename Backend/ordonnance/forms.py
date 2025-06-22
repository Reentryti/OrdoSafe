from django import forms
from .models import Ordonnance
import json

class MedicamentField(forms.CharField):
    def prepare_value(self, value):
        if isinstance(value, list):
            return json.dumps(value)
        return value

    def to_python(self, value):
        if not value:
            return []
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []

class OrdonnanceForm(forms.ModelForm):
    medicaments = MedicamentField(
        widget=forms.HiddenInput(),
        required=False,
        initial=[]
    )

    class Meta:
        model = Ordonnance
        fields = ['patient', 'medecin', 'notes', 'medicaments']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'medecin': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.medicaments:
            self.initial['medicaments'] = json.dumps(self.instance.medicaments)