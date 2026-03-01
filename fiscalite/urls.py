from django.urls import path
from . import views

app_name = 'fiscalite'

urlpatterns = [
    path('',                          views.dashboard_fiscal,         name='dashboard'),
    path('calculateur/',              views.calculateur_view,         name='calculateur'),
    path('historique/',               views.historique,               name='historique'),
    path('calendrier/',               views.calendrier,               name='calendrier'),
    path('echeance/ajouter/',         views.ajouter_echeance,         name='ajouter_echeance'),
    path('echeance/<int:pk>/fait/',   views.marquer_echeance,         name='marquer_echeance'),
    path('echeance/<int:pk>/supprimer/', views.supprimer_echeance,    name='supprimer_echeance'),
    path('declaration/<int:pk>/pdf/', views.exporter_pdf_declaration, name='pdf_declaration'),
]