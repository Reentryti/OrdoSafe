"""
API views for Vue.js frontend - ordonnance management.
"""
import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Ordonnance
from .forms import OrdonnanceForm
from .utils import log_medical_action, log_security_event, send_access_code


def parse_json_body(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return {}
    return request.POST


class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'doctor_profile')

    def handle_no_permission(self):
        return JsonResponse({'error': 'Accès réservé aux médecins'}, status=403)


class PharmacistRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'pharmacist_profile')

    def handle_no_permission(self):
        return JsonResponse({'error': 'Accès réservé aux pharmaciens'}, status=403)


# ─── Doctor API ───────────────────────────────────

class APIOrdonnanceListView(DoctorRequiredMixin, View):
    """List ordonnances for the logged-in doctor."""
    def get(self, request):
        doctor = request.user.doctor_profile
        status_filter = request.GET.get('status', '')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        qs = Ordonnance.objects.filter(doctor=doctor)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search:
            qs = qs.filter(
                Q(patient_first_name__icontains=search) |
                Q(patient_last_name__icontains=search)
            )
        qs = qs.order_by('-date_creation')

        total = qs.count()
        start = (page - 1) * page_size
        ordonnances = qs[start:start + page_size]

        results = []
        for o in ordonnances:
            results.append({
                'id': o.id,
                'patient_name': f"{o.patient_first_name} {o.patient_last_name}",
                'patient_first_name': o.patient_first_name,
                'patient_last_name': o.patient_last_name,
                'date_creation': o.date_creation.isoformat(),
                'status': o.status,
                'access_code': o.access_code,
                'has_signature': bool(o.signature),
            })

        return JsonResponse({'count': total, 'results': results})


class APIOrdonnanceCreateView(DoctorRequiredMixin, View):
    """Create a new ordonnance."""
    def post(self, request):
        data = parse_json_body(request)
        doctor = request.user.doctor_profile
        form = OrdonnanceForm(data, doctor=doctor)

        if form.is_valid():
            ordonnance = form.save()
            log_medical_action(
                user=request.user,
                action="ORDONNANCE_CREATED",
                ordonnance_id=ordonnance.id,
                details=f"Créée pour {ordonnance.patient_first_name} {ordonnance.patient_last_name}"
            )
            return JsonResponse({
                'id': ordonnance.id,
                'status': ordonnance.status,
                'access_code': ordonnance.access_code,
            }, status=201)

        return JsonResponse({'errors': form.errors}, status=400)


class APIOrdonnanceDetailView(DoctorRequiredMixin, View):
    """Get ordonnance details for doctor."""
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            return JsonResponse({'error': 'Non autorisé'}, status=403)

        sensitive = ordonnance.sensitive_data or {}
        return JsonResponse({
            'id': ordonnance.id,
            'patient_first_name': ordonnance.patient_first_name,
            'patient_last_name': ordonnance.patient_last_name,
            'patient_date_birth': str(ordonnance.patient_date_birth) if ordonnance.patient_date_birth else None,
            'patient_phone': str(ordonnance.patient_phone) if ordonnance.patient_phone else None,
            'patient_email': ordonnance.patient_email,
            'medicaments': ordonnance.medicaments,
            'notes': ordonnance.notes,
            'status': ordonnance.status,
            'access_code': ordonnance.access_code,
            'date_creation': ordonnance.date_creation.isoformat(),
            'doctor_name': ordonnance.doctor.user.get_full_name(),
            'doctor_specialisation': ordonnance.doctor.specialisation,
            'has_signature': bool(ordonnance.signature),
            'signature_valid': ordonnance.verify_signature() if ordonnance.signature else None,
        })


class APIOrdonnanceUpdateView(DoctorRequiredMixin, View):
    """Update an ordonnance."""
    def put(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            return JsonResponse({'error': 'Non autorisé'}, status=403)
        if ordonnance.status != 'draft':
            return JsonResponse({'error': 'Seuls les brouillons peuvent être modifiés'}, status=400)

        data = parse_json_body(request)
        form = OrdonnanceForm(data, instance=ordonnance, doctor=request.user.doctor_profile)
        if form.is_valid():
            ordonnance = form.save()
            log_medical_action(
                user=request.user,
                action="ORDONNANCE_UPDATED",
                ordonnance_id=ordonnance.id,
                details=f"Modifiée pour {ordonnance.patient_first_name} {ordonnance.patient_last_name}"
            )
            return JsonResponse({'status': 'success'})

        return JsonResponse({'errors': form.errors}, status=400)


class APIOrdonnanceDeleteView(DoctorRequiredMixin, View):
    """Delete a draft ordonnance."""
    def delete(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            return JsonResponse({'error': 'Non autorisé'}, status=403)
        if ordonnance.status != 'draft':
            return JsonResponse({'error': 'Seuls les brouillons peuvent être supprimés'}, status=400)

        log_medical_action(
            user=request.user,
            action="ORDONNANCE_DELETED",
            ordonnance_id=ordonnance.id,
            details=f"Supprimée pour {ordonnance.patient_first_name} {ordonnance.patient_last_name}"
        )
        ordonnance.delete()
        return JsonResponse({'status': 'success'})


class APIOrdonnanceSignView(DoctorRequiredMixin, View):
    """Sign an ordonnance."""
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.doctor != request.user.doctor_profile:
            return JsonResponse({'error': 'Non autorisé'}, status=403)
        if ordonnance.status != 'draft':
            return JsonResponse({'error': 'Seuls les brouillons peuvent être signés'}, status=400)

        try:
            ordonnance.sign(request.user.doctor_profile)
            try:
                send_access_code(ordonnance)
            except Exception:
                pass  # Don't fail if notification fails
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        log_medical_action(
            user=request.user,
            action="ORDONNANCE_SIGNED",
            ordonnance_id=ordonnance.id,
            details="Ordonnance signée électroniquement"
        )
        return JsonResponse({
            'status': 'success',
            'access_code': ordonnance.access_code,
        })


# ─── Pharmacist API ───────────────────────────────

class APIPharmacistSearchView(PharmacistRequiredMixin, View):
    """Search ordonnances by patient info or contact+code."""
    def get(self, request):
        search_type = request.GET.get('type', 'info')

        if search_type == 'contact':
            contact = request.GET.get('contact', '').strip()
            code = request.GET.get('code', '').strip()
            if not contact or not code:
                return JsonResponse({'results': [], 'error': 'Contact et code requis'}, status=400)

            ordonnances = Ordonnance.objects.filter(
                Q(patient_email__iexact=contact) |
                Q(patient_phone__icontains=contact),
                access_code__iexact=code,
                status='issued'
            ).order_by('-date_creation')
        else:
            q = request.GET.get('q', '').strip()
            if not q or len(q) < 2:
                return JsonResponse({'results': []})

            ordonnances = Ordonnance.objects.filter(
                Q(patient_last_name__icontains=q) |
                Q(patient_first_name__icontains=q) |
                Q(notes__icontains=q)
            ).order_by('-date_creation')[:20]

        results = [{
            'id': o.id,
            'patient_name': f"{o.patient_first_name} {o.patient_last_name}",
            'patient_first_name': o.patient_first_name,
            'patient_last_name': o.patient_last_name,
            'date_creation': o.date_creation.strftime('%Y-%m-%d'),
            'status': o.status,
            'access_code': o.access_code,
        } for o in ordonnances]

        return JsonResponse({'results': results})


class APIPharmacistOrdonnanceDetailView(PharmacistRequiredMixin, View):
    """Get ordonnance details for pharmacist."""
    def get(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        sensitive = ordonnance.sensitive_data or {}

        return JsonResponse({
            'id': ordonnance.id,
            'patient_first_name': ordonnance.patient_first_name,
            'patient_last_name': ordonnance.patient_last_name,
            'patient_date_birth': str(ordonnance.patient_date_birth) if ordonnance.patient_date_birth else None,
            'patient_phone': str(ordonnance.patient_phone) if ordonnance.patient_phone else None,
            'patient_email': ordonnance.patient_email,
            'medicaments': ordonnance.medicaments,
            'notes': ordonnance.notes,
            'status': ordonnance.status,
            'access_code': ordonnance.access_code,
            'date_creation': ordonnance.date_creation.isoformat(),
            'doctor_name': ordonnance.doctor.user.get_full_name(),
            'doctor_specialisation': ordonnance.doctor.specialisation,
            'has_signature': bool(ordonnance.signature),
            'signature_valid': ordonnance.verify_signature() if ordonnance.signature else None,
        })


class APIPharmacistValidateView(PharmacistRequiredMixin, View):
    """Validate (fulfill) an ordonnance."""
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.status != 'issued':
            return JsonResponse({'error': 'Ordonnance non émise'}, status=400)

        ordonnance.status = 'fulfilled'
        ordonnance.save()
        log_medical_action(
            user=request.user,
            action="ORDONNANCE_VALIDATED",
            ordonnance_id=ordonnance.id,
            details="Ordonnance honorée par le pharmacien"
        )
        return JsonResponse({'status': 'success'})


class APIPharmacistReportView(PharmacistRequiredMixin, View):
    """Report a suspicious ordonnance."""
    def post(self, request, pk):
        data = parse_json_body(request)
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        reason = data.get('reason', '')
        if not reason:
            return JsonResponse({'error': 'Raison requise'}, status=400)

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
        return JsonResponse({'status': 'success'})


class APIPharmacistBlockView(PharmacistRequiredMixin, View):
    """Block an ordonnance."""
    def post(self, request, pk):
        ordonnance = get_object_or_404(Ordonnance, pk=pk)
        if ordonnance.status == 'fulfilled':
            return JsonResponse({'error': 'Ordonnance déjà honorée'}, status=400)

        ordonnance.status = 'cancelled'
        ordonnance.notes = "Bloquée par le pharmacien"
        ordonnance.save()
        log_security_event(
            user=request.user,
            event="ORDONNANCE_BLOCKED",
            ordonnance_id=ordonnance.id,
            ip_address=request.META.get('REMOTE_ADDR'),
            details="Ordonnance bloquée"
        )
        return JsonResponse({'status': 'success'})
