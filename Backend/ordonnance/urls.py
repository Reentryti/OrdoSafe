from django.urls import path
from .views import (
    OrdonnanceCreateView, OrdonnanceUpdateView, OrdonnanceDetailView,
    OrdonnanceListView, OrdonnanceDeleteView, OrdonnanceSignView
)

urlpatterns = [
    path('', OrdonnanceListView.as_view(), name='ordonnance_list'),
    path('new/', OrdonnanceCreateView.as_view(), name='ordonnance_create'),
    path('<int:pk>/', OrdonnanceDetailView.as_view(), name='ordonnance_detail'),
    path('<int:pk>/modifier/', OrdonnanceUpdateView.as_view(), name='ordonnance_update'),
    path('<int:pk>/supprimer/', OrdonnanceDeleteView.as_view(), name='ordonnance_delete'),
    path('<int:pk>/signer/', OrdonnanceSignView.as_view(), name='ordonnance_sign'),
]