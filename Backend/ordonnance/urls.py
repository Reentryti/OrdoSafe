from django.urls import path
from .views import (
    OrdonnanceCreateView,
    OrdonnanceUpdateView,
    OrdonnanceDetailView,
    OrdonnanceListView
)

urlpatterns = [
    path('nouvelle/', OrdonnanceCreateView.as_view(), name='ordonnance_create'),
    path('<int:pk>/modifier/', OrdonnanceUpdateView.as_view(), name='ordonnance_update'),
    path('<int:pk>/', OrdonnanceDetailView.as_view(), name='ordonnance_detail'),
    path('liste/', OrdonnanceListView.as_view(), name='ordonnance_list'),
]