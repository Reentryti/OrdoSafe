from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import OrdonnanceForm
import json
from audit.utils import log_security_event
from .models import Ordonnance
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from utilisateurs.models import Doctor, Patient, BasicUser
from django.utils import timezone
from .forms import OrdonnanceForm
from django.core.exceptions import PermissionDenied
import logging
from .utils import log_medical_action, log_security_event
from django.views.decorators.http import require_http_methods



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
        ordonnance = Ordonnance.objects.filter(patient=patient).order_by('-date_creation')
        return render(request, 'ordonnance/patient_list.html', {'ordonnance': ordonnance})

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
            ordonnance = form.save(commit=False)
            ordonnance.doctor = request.user.doctor_profile
            ordonnance.created_by = request.user
            ordonnance.status = 'draft'
            ordonnance.save()
            
            log_medical_action(
                user=request.user,
                action="ORDONNANCE_CREATED",
                ordonnance_id=ordonnance.id,
                patient=ordonnance.patient,
                details=f"Status: {ordonnance.status}"
            )
            
            return redirect('doctor_ordonnance_detail', pk=ordonnance.id)
        
        return render(request, 'create.html', {'form': form})


# Ordonnance Modification
class OrdonnanceUpdateView(DoctorRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        
        form = OrdonnanceForm(instance=ordonnance, doctor=request.user.doctor_profile)
        return render(request, 'ordonnance/update.html', {'form': form, 'ordonnance': ordonnance})
    
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
                patient=ordonnance.patient,
                details="Ordonnance mise à jour"
            )
            #logger.info(f"Dr {request.user.get_full_name()} a modifié la prescription {pk}")
            return redirect('doctor_ordonnance_detail', pk=pk)
        
        return render(request, 'ordonnance/update.html', {'form': form, 'ordonnance': ordonnance})


# Ordonnance Details
class OrdonnanceDetailView(DoctorRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied
        
        context = {
            'ordonnance': ordonnance,
            'patient_info': ordonnance.sensitive_data['patient_info'],
            'medicaments': ordonnance.sensitive_data['medicaments'],
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
            patient=ordonnance.patient,
            details="Ordonnance supprimée"
        )
        ordonnance.delete()
        #logger.info(f"Dr {request.user.get_full_name()} a supprimé la prescription {pk}")
        return JsonResponse({'status': 'success', 'message': 'Ordonnance supprimée avec succès'})

class SignOrdonnanceView(DoctorRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)

        if ordonnance.doctor != request.user.doctor_profile:
            raise PermissionDenied

        if ordonnance.status != 'draft':
            return JsonResponse({'status': 'error', 'message': 'Seuls les brouillons peuvent être signés'}, status=400)

        try:
            ordonnance.sign(request.user.doctor_profile)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        log_medical_action(
            user=request.user,
            action="ORDONNANCE_SIGNED",
            ordonnance_id=ordonnance.id,
            patient=ordonnance.patient,
            details="Signature électronique sécurisée ajoutée"
        )

        return JsonResponse({'status': 'success', 'message': 'Ordonnance signée avec une signature cryptographique'})


# Reorder ordonnance
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

class PharmacistRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'pharmacist_profile')

# Ordonnance Validation
class ValidateOrdonnanceView(PharmacistRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        pharmacist = request.user.pharmacist_profile
        
        if ordonnance.status != 'issued':
            return JsonResponse({'status': 'error', 'message': 'Seules les ordonnances émises peuvent être honorées'}, status=400)
        
        # Verify signature if needed
        if not ordonnance.signature:
            return JsonResponse({'status': 'error', 'message': 'Ordonnance non signée'}, status=400)
        
        ordonnance.status = 'fulfilled'
        ordonnance.save()
        
        log_medical_action(
            user=request.user,
            action="ORDONNANCE_VALIDATED",
            ordonnance_id=ordonnance.id,
            patient=ordonnance.patient,
            details="Ordonnance honorée par le pharmacien"
        )
        #logger.info(f"Pharmacist {pharmacist.user.get_full_name()} a validé l'ordonnance {pk}")
        return JsonResponse({'status': 'success', 'message': 'Ordonnance honorée avec succès'})

# Ordonnance Reported Feat 
class ReportOrdonnanceView(PharmacistRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        pharmacist = request.user.pharmacist_profile
        reason = request.POST.get('reason', '')
        
        if not reason:
            return JsonResponse({'status': 'error', 'message': 'Veuillez fournir une raison'}, status=400)
        
        ordonnance.status = 'cancelled'
        ordonnance.notes = f"Signalée par {pharmacist.user.get_full_name()} ({pharmacist.pharmacy_name}): {reason}"
        ordonnance.save()

        log_security_event(
            user=request.user,
            event="ORDONNANCE_REPORTED",
            ordonnance_id=ordonnance.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            details=f"Raison: {reason}"
        )
        #logger.warning(f"Pharmacist {pharmacist.user.get_full_name()} a reporté {pk}: {reason}")
        return JsonResponse({'status': 'success', 'message': 'Ordonnance signalée avec succès'})

# Ordonnance Blocked view
class BlockOrdonnanceView(PharmacistRequiredMixin, View):
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        pharmacist = request.user.pharmacist_profile
        
        if ordonnance.status == 'fulfilled':
            return JsonResponse({'status': 'error', 'message': 'Ordonnance déjà honorée'}, status=400)
        
        ordonnance.status = 'cancelled'
        ordonnance.notes = f"Bloquée par {pharmacist.user.get_full_name()} ({pharmacist.pharmacy_name})"
        ordonnance.save()
        
        log_security_event(
            user=request.user,
            event="ORDONNANCE_BLOCKED",
            ordonnance_id=ordonnance.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            details="Ordonnance bloquée par le pharmacien"
        )
        #logger.warning(f"Pharmacist {pharmacist.user.get_full_name()} a bloqué l'ordonnance {pk}")
        return JsonResponse({'status': 'success', 'message': 'Ordonnance bloquée avec succès'})


class PharmacistOrdonnanceDetailView(PharmacistRequiredMixin, View):
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        
        context = {
            'ordonnance': ordonnance,
            'patient_info': ordonnance.sensitive_data['patient_info'],
            'doctor_info': ordonnance.sensitive_data['doctor_info'],
            'medicaments': ordonnance.sensitive_data['medicaments'],
            'is_pharmacist': True
        }
        
        return render(request, 'ordonnance/detail.html', context)

    

# Search view (just to test smt)
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
