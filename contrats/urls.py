from django.urls import path
from . import views

app_name = 'contrats'

urlpatterns = [
    path('',                        views.liste_contrats,   name='liste'),
    path('nouveau/',                views.choisir_modele,   name='choisir_modele'),
    path('nouveau/<int:modele_id>/',views.creer_contrat,    name='creer'),
    path('<int:pk>/',               views.detail_contrat,   name='detail'),
    path('<int:pk>/modifier/',      views.modifier_contrat, name='modifier'),
    path('<int:pk>/supprimer/',     views.supprimer_contrat,name='supprimer'),
    path('<int:pk>/pdf/',           views.exporter_pdf,     name='pdf'),
    path('<int:pk>/finaliser/',     views.finaliser_contrat,name='finaliser'),
]