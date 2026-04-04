from django.urls import path
from .api_views import (
    APIOrdonnanceListView, APIOrdonnanceCreateView,
    APIOrdonnanceDetailView, APIOrdonnanceUpdateView,
    APIOrdonnanceDeleteView, APIOrdonnanceSignView,
    APIPharmacistSearchView, APIPharmacistOrdonnanceDetailView,
    APIPharmacistValidateView, APIPharmacistReportView,
    APIPharmacistBlockView,
)

urlpatterns = [
    # Doctor endpoints
    path('doctor/ordonnances/', APIOrdonnanceListView.as_view(), name='api_ordonnance_list'),
    path('doctor/ordonnances/create/', APIOrdonnanceCreateView.as_view(), name='api_ordonnance_create'),
    path('doctor/ordonnances/<int:pk>/', APIOrdonnanceDetailView.as_view(), name='api_ordonnance_detail'),
    path('doctor/ordonnances/<int:pk>/update/', APIOrdonnanceUpdateView.as_view(), name='api_ordonnance_update'),
    path('doctor/ordonnances/<int:pk>/delete/', APIOrdonnanceDeleteView.as_view(), name='api_ordonnance_delete'),
    path('doctor/ordonnances/<int:pk>/sign/', APIOrdonnanceSignView.as_view(), name='api_ordonnance_sign'),

    # Pharmacist endpoints
    path('pharmacist/search/', APIPharmacistSearchView.as_view(), name='api_pharmacist_search'),
    path('pharmacist/ordonnances/<int:pk>/', APIPharmacistOrdonnanceDetailView.as_view(), name='api_pharmacist_ordonnance_detail'),
    path('pharmacist/ordonnances/<int:pk>/validate/', APIPharmacistValidateView.as_view(), name='api_pharmacist_validate'),
    path('pharmacist/ordonnances/<int:pk>/report/', APIPharmacistReportView.as_view(), name='api_pharmacist_report'),
    path('pharmacist/ordonnances/<int:pk>/block/', APIPharmacistBlockView.as_view(), name='api_pharmacist_block'),
]
