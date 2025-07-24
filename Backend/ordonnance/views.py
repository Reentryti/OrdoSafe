from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import OrdonnanceForm
import json
from audit.utils import log_security_event
from .models import Ordonnance
from django.shortcuts import render, redirect, get_object_or_404

from django.views import View
from django.http import JsonResponse
from utilisateurs.models import Doctor, Patient, BasicUser
from django.utils import timezone
from .forms import OrdonnanceForm
from django.core.exceptions import PermissionDenied
import logging
from .utils import log_medical_action, log_security_event
from django.views.decorators.http import require_http_methods, require_GET
from django.db.models import Q
from .utils import send_access_code



#####################################################

# Patient Views

#####################################################

class PatientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'patient_profile')

# Ordonnance display list

class PatientOrdonnanceListView(PatientRequiredMixin, View):
    def get(self, request):
        patient = request.user.patient_profile
        ordonnances = Ordonnance.objects.filter(patient=patient).order_by('-date_creation')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
            # Requête fetch() => on renvoie du JSON
            data = []
            for o in ordonnances:
                data.append({
                    'id': o.id,
                    'doctor': str(o.doctor),
                    'date_creation': o.date_creation.isoformat(),
                    'status': o.status,
                    'medicaments': o.medicaments  # doit être un dict ou JSONField
                })
            return JsonResponse(data, safe=False)

        # Sinon, on renvoie la page HTML classique
        return render(request, 'list.html', {'ordonnance': ordonnances})

# Ordonnance Detail view
class PatientOrdonnanceDetailView(PatientRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.patient != request.user.patient_profile:
            raise PermissionDenied
        
        context = {
            'ordonnance': ordonnance,
            'doctor_info': ordonnance.sensitive_data['doctor_info'],
            'medicaments': ordonnance.sensitive_data['medicaments'],
            'is_patient': True
        }
        return render(request, 'ordonnance/detail.html', context)

# Ordonnance Renewal Request
class RequestRenewalView(PatientRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.patient != request.user.patient_profile:
            raise PermissionDenied
        
        if ordonnance.status != 'issued':
            return JsonResponse({'status': 'error', 'message': 'Seules les ordonnances émises peuvent être renouvelées'}, status=400)
        
        # In a real app, you would send a notification to the doctor
        ordonnance.notes = f"Demande de renouvellement par le patient le {timezone.now().strftime('%Y-%m-%d')}"
        ordonnance.save()
        
        log_medical_action(
            user=request.user,
            action="RENEWAL_REQUESTED",
            ordonnance_id=ordonnance.id,
            patient=ordonnance.patient,
            details="Demande de renouvellement par le patient"
        )
        #logger.info(f"Patient {request.user.get_full_name()} a demandé une demande de renouvellement pour l'ordonnance {pk}")
        return JsonResponse({'status': 'success', 'message': 'Demande de renouvellement envoyée au médecin'})


#####################################################

# Doctor View 

#####################################################

# Doctor Access Control View
class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'doctor_profile')

# Ordonnance Creation
class OrdonnanceCreateView(DoctorRequiredMixin, View):
    def get(self, request):
        form = OrdonnanceForm(doctor=request.user.doctor_profile)
        return render(request, 'create.html', {'form': form})
    
    def post(self, request):
        form = OrdonnanceForm(request.POST, doctor=request.user.doctor_profile)
        if form.is_valid():
            ordonnance = form.save()
            log_medical_action(
                user=request.user,
                action="ORDONNANCE_CREATED",
                ordonnance_id=ordonnance.id,
                details=f"Créée pour {ordonnance.patient_first_name} {ordonnance.patient_last_name}"
            )
            return redirect('ordonnance:doctor_ordonnance_detail', pk=ordonnance.id)
        return render(request, 'create.html', {'form': form})

# Ordonnance Modification
class OrdonnanceUpdateView(DoctorRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        form = OrdonnanceForm(instance=ordonnance, doctor=request.user.doctor_profile)
        return render(request, 'update.html', {'form': form, 'ordonnance': ordonnance})
    
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        form = OrdonnanceForm(request.POST, instance=ordonnance, doctor=request.user.doctor_profile)
        if form.is_valid():
            form.save()
            log_medical_action(
                user=request.user,
                action="ORDONNANCE_UPDATED",
                ordonnance_id=ordonnance.id,
                details=f"Modifiée pour {ordonnance.patient_first_name} {ordonnance.patient_last_name}"
            )
            return redirect('ordonnance:doctor_ordonnance_detail', pk=ordonnance.id)
        return render(request, 'update.html', {'form': form, 'ordonnance': ordonnance})

# Ordonnance Details
class OrdonnanceDetailView(DoctorRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        context = {
            'ordonnance': ordonnance,
            'patient_info': ordonnance.sensitive_data.get('patient_info', {}),
            'medicaments': ordonnance.sensitive_data.get('medicaments', []),
            'is_doctor': True
        }
        return render(request, 'detail.html', context)

# Ordonnance Deletion
class OrdonnanceDeleteView(DoctorRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        log_medical_action(
            user=request.user,
            action="ORDONNANCE_DELETED",
            ordonnance_id=ordonnance.id,
            details=f"Supprimée pour {ordonnance.patient_prenom} {ordonnance.patient_nom}"
        )
        ordonnance.delete()
        return JsonResponse({'status': 'success', 'message': 'Ordonnance supprimée avec succès'})

# Ordonnance Signature 
class SignOrdonnanceView(DoctorRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        if ordonnance.status != 'draft':
            return JsonResponse({'status': 'error', 'message': 'Seuls les brouillons peuvent être signés'}, status=400)
        try:
            ordonnance.sign(request.user.doctor_profile)
            send_access_code(ordonnance) 
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        log_medical_action(
            user=request.user,
            action="ORDONNANCE_SIGNED",
            ordonnance_id=ordonnance.id,
            details="Ordonnance signée électroniquement"
        )
        return JsonResponse({'status': 'success', 'message': 'Ordonnance signée avec succès'})

# Reorder ordonnance (dont need it)
class RenewOrdonnanceView(DoctorRequiredMixin, View):
    def post(self, request, pk):
        original = get_object_or_404(Ordonnance, pk=pk)
        if original.doctor != request.user.doctor_profile:
            raise PermissionDenied
        
        if original.status != 'issued':
            return JsonResponse({'status': 'error', 'message': 'Seules les ordonnances émises peuvent être renouvelées'}, status=400)
        
        new_ordonnance = Ordonnance.objects.create(
            patient=original.patient,
            doctor=original.doctor,
            medicaments=original.medicaments,
            status='draft',
            created_by=request.user,
            notes=f"Renouvellement de l'ordonnance #{original.id}"
        )
        
        log_medical_action(
            user=request.user,
            action="ORDONNANCE_RENEWED",
            ordonnance_id=new_ordonnance.id,
            patient=new_ordonnance.patient,
            details=f"Renouvellement de #{original.id}"
        )
        #logger.info(f"Dr {request.user.get_full_name()} a renouvellé la prescription {pk} as {new_ordonnance.id}")
        return JsonResponse({
            'status': 'success', 
            'message': 'Ordonnance renouvelée avec succès',
            'new_ordonnance_id': new_ordonnance.id
        })


#####################################################

# Pharmacist Views

#####################################################

# Pharmacist Access Control Function
class PharmacistRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'pharmacist_profile')

# Ordonnance Validation
class ValidateOrdonnanceView(PharmacistRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.status != 'issued':
            return JsonResponse({'status': 'error', 'message': 'Ordonnance non émise'}, status=400)
        if not ordonnance.signature:
            return JsonResponse({'status': 'error', 'message': 'Ordonnance non signée'}, status=400)
        ordonnance.status = 'fulfilled'
        ordonnance.save()
        log_medical_action(
            user=request.user,
            action="ORDONNANCE_VALIDATED",
            ordonnance_id=ordonnance.id,
            details="Ordonnance honorée par le pharmacien"
        )
        return JsonResponse({'status': 'success', 'message': 'Ordonnance honorée avec succès'})

# Ordonnance Reported Feat 
class ReportOrdonnanceView(PharmacistRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        reason = request.POST.get('reason', '')
        if not reason:
            return JsonResponse({'status': 'error', 'message': 'Veuillez fournir une raison'}, status=400)
        ordonnance.status = 'cancelled'
        ordonnance.notes = f"Signalée : {reason}"
        ordonnance.save()
        log_security_event(
            user=request.user,
            event="ORDONNANCE_REPORTED",
            ordonnance_id=ordonnance.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            details=reason
        )
        return JsonResponse({'status': 'success', 'message': 'Signalement effectué'})

# Ordonnance Blocked view
class BlockOrdonnanceView(PharmacistRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.status == 'fulfilled':
            return JsonResponse({'status': 'error', 'message': 'Ordonnance déjà honorée'}, status=400)
        ordonnance.status = 'cancelled'
        ordonnance.notes = f"Bloquée par le pharmacien"
        ordonnance.save()
        log_security_event(
            user=request.user,
            event="ORDONNANCE_BLOCKED",
            ordonnance_id=ordonnance.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            details="Ordonnance bloquée"
        )
        return JsonResponse({'status': 'success', 'message': 'Ordonnance bloquée'})

# Ordonnance Detail View
class PharmacistOrdonnanceDetailView(PharmacistRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        context = {
            'ordonnance': ordonnance,
            'patient_info': ordonnance.sensitive_data.get('patient_info', {}),
            'doctor_info': ordonnance.sensitive_data.get('doctor_info', {}),
            'medicaments': ordonnance.sensitive_data.get('medicaments', []),
            'is_pharmacist': True
        }
        return render(request, 'detail.html', context)


# Search view
# Based on patient information (name, date_birth, etc)
@require_http_methods(["GET"])
def search_ordonnances_by_patient_info(request):
    q = request.GET.get("q", "").strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    ordonnances = Ordonnance.objects.filter(
        Q(patient_last_name__icontains=q) |
        Q(patient_first_name__icontains=q) |
        Q(notes__icontains=q) |
        Q(_encrypted_data__icontains=q)
    ).order_by('-date_creation')[:20]

    results = [{
        'id': o.id,
        'nom': o.patient_last_name,
        'prenom': o.patient_first_name,
        'date': o.date_creation.strftime('%Y-%m-%d'),
        'status': o.status
    } for o in ordonnances]

    return JsonResponse({'results': results})

# Based on patient phonenumber or/and email
@require_GET
def search_ordonnances_by_contact(request):
    contact = request.GET.get("contact", "").strip()
    code    = request.GET.get("code", "").strip()

    # Info check
    if not contact or not code:
        return JsonResponse({'results': [], 'error': 'Contact et code requis.'}, status=400)

    ordonnances = Ordonnance.objects.filter(
        Q(patient_email__iexact=contact) |
        Q(patient_phone__icontains=contact),
        access_code__iexact=code,
        status='issued'
    ).order_by('-date_creation')

    results = [{
        'id': o.id,
        'nom': o.patient_last_name,
        'prenom': o.patient_first_name,
        'date': o.date_creation.strftime('%Y-%m-%d'),
        'status': o.status
    } for o in ordonnances]

    return JsonResponse({'results': results})


# Maybe we gonna add a complete different search options
@require_http_methods(["GET"])
def patient_search(request):
    phone_number = request.GET.get('phone', '').strip()
    
    if not phone_number:
        return JsonResponse({'trouvé': False})
    
    try:
        
        user = BasicUser.objects.get(phone_number=phone_number)
        
        try:
            patient = user.patient_profile
            return JsonResponse({
                'trouvé': True,
                'name': user.get_full_name(),
                'id': patient.id,
                'user_id': user.id
            })
        except Patient.DoesNotExist:
            
            return JsonResponse({
                'trouvé': False,
                'message': 'Cet utilisateur n\'est pas enregistré comme patient'
            })
            
    except BasicUser.DoesNotExist:
        return JsonResponse({'trouvé': False})
    
    except Exception as e:
        return JsonResponse({'trouvé': False, 'error': str(e)})




#### thinking bout a new logic

class PatientSearchAPI(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({'results': []})

        users = BasicUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number_icontains=query),
            patient_profile__isnull=False

        ).select_related('patient_profile')[:10]

        results = [{
            'id': user.patient_profile.id,
            'text': f"{user.get_full_name()}",
            'phone': str(user.phone_number) 
        } for user in users]
         
        return JsonResponse({'results': results})

class PatientOrdonnanceListAPI(LoginRequiredMixin, View):
    def get(self, request, patient_id):
        ordonnances = Ordonnance.objects.filter(
            patient_id=patient_id,
            status='issued'
        ).select_related('doctor__user')
        
        data = [{
            'id': o.id,
            'doctor': o.doctor.user.get_full_name(),
            'date_creation': o.date_creation.strftime('%d/%m/%Y'),
            'expiry_date': o.expiry_date.strftime('%d/%m/%Y') if o.expiry_date else None,
            'medicaments': o.medicaments
        } for o in ordonnances]
        
        return JsonResponse(data, safe=False)