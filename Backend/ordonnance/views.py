from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .forms import OrdonnanceForm
import json
from audit.utils import log_security_event

# Ordonnance Creation view
class OrdonnanceCreateView(CreateView, LoginRequiredMixin):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'ordonnance/ordonnance_form.html'
    #success_url = reverse_lazy('ordonnance_list')

    def form_valid(self, form):    
        medicaments = json.loads(self.request.POST.get('medicaments', '[]'))
        form.instance.medicaments = medicaments
        form.instance.created_by = self.request.user

        response = super().form_valid(form)
        # Ordonnance creation log
        log_security_event(
            user=self.request.user,
            action='ordonnance_created',
            metadata={
                'ordonnance_id':self.object.id,
                'patient_id':self.object.patient.id
            }
        )
        return response

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self.request.user, 'doctor_profile'):
            initial['doctor'] = self.request.user.doctor_profile
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get._form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

# Ordonnance Update view
class OrdonnanceUpdateView(UpdateView, LoginRequiredMixin):
    model = Ordonnance
    form_class = OrdonnanceForm
    template_name = 'ordonnance/ordonnance_form.html'


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        medicaments = json.loads(self.request.POST.get('medicaments', '[]'))
        form.instance.medicaments = medicaments

        response = super().form_valid(form)

        # Ordonnance Update Log
        log_security_event(
            user=self.request.user,
            action='ordonnance_updated',
            metadata={
                'ordonnance_id':self.object.id,
                'patient_id':self.object.patient.id
            }
        )

        return response
    

# Ordonnance Update View
class OrdonnanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Ordonnance
    template_name = 'ordonnance/delete.html'

    def delete(self, request, *args, **kwargs):
        ordonnance = self.get_object()

        # Ordonnance Deletion Log
        log_security_event(
            user=request.user,
            action='ordonnance_deleted',
            metadata={
                'ordonnance_id':ordonnance.id,
                'patient_id':ordonnance.patient.id
            }
        )
        return super().delete(request, *args, **kwargs)



# Ordonnance Detail View
class OrdonnanceDetailView(LoginRequiredMixin, DetailView):
    model = Ordonnance
    template_name='ordonnance/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        ordonnance = self.object

        # Define access control 
        context['can_edit'] = (
            hasattr(user, 'doctor_profile') and ordonnance.medecin == user.doctor_profile and ordonnance.status == 'draft'
        )

        context['can_delete'] = context['can_edit']
        context['can_sign'] = (
            hasattr(user, 'doctor_profile') and ordonnance.medecin == user.doctor_profile and ordonnance.status in ['draft', 'issued']

        )
        return context
    

# Ordonnance Signature View
class OrdonnanceSignView(LoginRequiredMixin, DetailView):
    model = Ordonnance
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        ordonnance = self.get_object()

        if not (hasattr(request.user, 'doctor_profile') and ordonnance.medecin == request.user.doctor_profile):
            messages.error(request, "Action non autorisée")
            return redirect('ordonnance_detail', pk=ordonnance.pk)
        
        try:
            private_key_path = f"keys/doctor_{request.user.id}_private.pem"

            ordonnance.sign(private_key_path)
            messages.success(request, "Ordonnance signée avec succés")

            # Ordonnance Signature log
            log_security_event(
                user=request.user,
                action='ordonnance_signed',
                metadata={
                    'ordonnance_id':ordonnance.id,
                    'patient_id':ordonnance.patient.id,
                    'signature':ordonnance.signature[:50] + '...'
                }
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de la signature:{str(e)}")

        return redirect('ordonnance_detail', pk=ordonnance.pk)
    

# Ordonnance List View
class OrdonnanceListView(LoginRequiredMixin, ListView):
    model = Ordonnance
    template_name = 'ordonnance/list.html'
    context_object_name = 'ordonnances'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        #Distinguish btw patient and doctor list
        if hasattr(self.request.user, 'patient_profile'):
            return queryset.filter(patient=self.request.user.patient_profile)
        elif hasattr(self.request.user, 'doctor_profile'):
            return queryset.filter(doctor=self.request.user.doctor_profile)
        
        return queryset.none()
    
    
    