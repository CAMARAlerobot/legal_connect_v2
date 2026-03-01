from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    path('',                          views.liste_dossiers,    name='liste'),
    path('creer/',                    views.creer_dossier,     name='creer'),
    path('<int:pk>/',                 views.detail_dossier,    name='detail'),
    path('<int:pk>/message/',         views.envoyer_message,   name='message'),
    path('<int:pk>/valider/',         views.valider_dossier,   name='valider'),
    path('<int:pk>/assigner/',        views.assigner_expert,   name='assigner'),
    path('<int:pk>/commentaire/',     views.ajouter_commentaire, name='commentaire'),
    path('<int:pk>/archiver/',        views.archiver_dossier,  name='archiver'),
]