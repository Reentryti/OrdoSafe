from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .forms import OrdonnanceForm
import json

class OrdonnanceCreateView(CreateView):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'ordonnance/ordonnance_form.html'
    success_url = reverse_lazy('ordonnance_list')

    def form_valid(self, form):
        
        medicaments = json.loads(self.request.POST.get('medicaments', '[]'))
        form.instance.medicaments = medicaments
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class OrdonnanceUpdateView(UpdateView):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'ordonnance/ordonnance_form.html'
    success_url = reverse_lazy('ordonnance_list')

    def form_valid(self, form):
        medicaments = json.loads(self.request.POST.get('medicaments', '[]'))
        form.instance.medicaments = medicaments
        return super().form_valid(form)