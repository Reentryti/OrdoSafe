from django.urls import path
from . import views

from .views import ( 
    PatientOrdonnanceListView, PatientOrdonnanceDetailView, RequestRenewalView,
    OrdonnanceCreateView, OrdonnanceUpdateView, OrdonnanceDetailView, OrdonnanceDeleteView, SignOrdonnanceView, RenewOrdonnanceView,
    ValidateOrdonnanceView, ReportOrdonnanceView, BlockOrdonnanceView, PharmacistOrdonnanceDetailView
)

urlpatterns = [
    # Patient endpoints
    path('patient/prescriptions/', PatientOrdonnanceListView.as_view(), name='patient_ordonnance_list'),
    path('patient/ordonnance/<int:pk>/', PatientOrdonnanceDetailView.as_view(), name='patient_ordonnance_detail'),
    path('patient/ordonnance/<int:pk>/request-renewal/', RequestRenewalView.as_view(), name='request_renewal'),
    # Doctor URLs
    path('doctor/ordonnance/create/', OrdonnanceCreateView.as_view(), name='doctor_ordonnance_create'),
    path('doctor/ordonnance/<int:pk>/update/', OrdonnanceUpdateView.as_view(), name='doctor_ordonnance_update'),
    path('doctor/ordonnance/<int:pk>/', OrdonnanceDetailView.as_view(), name='doctor_ordonnance_detail'),
    path('doctor/ordonnance/<int:pk>/delete/', OrdonnanceDeleteView.as_view(), name='doctor_ordonnance_delete'),
    path('doctor/ordonnance/<int:pk>/sign/', SignOrdonnanceView.as_view(), name='sign_ordonnance'),
    path('doctor/ordonnance/<int:pk>/renew/', RenewOrdonnanceView.as_view(), name='renew_ordonnance'),
    # Pharmacist URLs
    path('pharmacist/ordonnance/<int:pk>/validate/', ValidateOrdonnanceView.as_view(), name='validate_ordonnance'),
    path('pharmacist/ordonnance/<int:pk>/report/', ReportOrdonnanceView.as_view(), name='report_ordonnance'),
    path('pharmacist/ordonnance/<int:pk>/block/', BlockOrdonnanceView.as_view(), name='block_ordonnance'),
    path('pharmacist/ordonnance/<int:pk>/', PharmacistOrdonnanceDetailView.as_view(), name='pharmacist_ordonnance_detail'),

    #Utils
    path('ajax/patient-search/', views.patient_search, name='patient_search'),
]