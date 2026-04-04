from django.urls import path
from .views import (
    OrdonnanceCreateView, OrdonnanceUpdateView, OrdonnanceDetailView, OrdonnanceDeleteView, SignOrdonnanceView,
    ValidateOrdonnanceView, ReportOrdonnanceView, BlockOrdonnanceView, PharmacistOrdonnanceDetailView, search_ordonnances_by_contact,
    search_ordonnances_by_patient_info
)

app_name = 'ordonnance'

urlpatterns = [

    # Doctor URLs
    path('doctor/ordonnance/create/', OrdonnanceCreateView.as_view(), name='doctor_ordonnance_create'),
    path('doctor/ordonnance/<int:pk>/update/', OrdonnanceUpdateView.as_view(), name='doctor_ordonnance_update'),
    path('doctor/ordonnance/<int:pk>/', OrdonnanceDetailView.as_view(), name='doctor_ordonnance_detail'),
    path('doctor/ordonnance/<int:pk>/delete/', OrdonnanceDeleteView.as_view(), name='doctor_ordonnance_delete'),
    path('doctor/ordonnance/<int:pk>/sign/', SignOrdonnanceView.as_view(), name='sign_ordonnance'),
    # Pharmacist URLs
    path('pharmacist/ordonnance/<int:pk>/validate/', ValidateOrdonnanceView.as_view(), name='validate_ordonnance'),
    path('pharmacist/ordonnance/<int:pk>/report/', ReportOrdonnanceView.as_view(), name='report_ordonnance'),
    path('pharmacist/ordonnance/<int:pk>/block/', BlockOrdonnanceView.as_view(), name='block_ordonnance'),
    path('pharmacist/ordonnance/<int:pk>/', PharmacistOrdonnanceDetailView.as_view(), name='pharmacist_ordonnance_detail'),
    path('pharmacist/ordonnance/search-contact/', search_ordonnances_by_contact, name='ordonnance_search_contact'),
    path('pharmacist/ordonnance/search-info/', search_ordonnances_by_patient_info, name='ordonnance_search_info'),
]