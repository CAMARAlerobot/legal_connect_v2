from django.urls import path
from . import views

app_name = 'fiscalite'

urlpatterns = [
    # Dashboard & navigation principale
    path('',                                    views.dashboard_fiscal,         name='dashboard'),
    path('calculateur/',                        views.calculateur_view,         name='calculateur'),
    path('penalites/',                          views.penalites_view,           name='penalites'),
    path('historique/',                         views.historique,               name='historique'),
    path('calendrier/',                         views.calendrier,               name='calendrier'),
    path('statistiques/',                       views.statistiques,             name='statistiques'),
    path('recapitulatif/',                      views.recapitulatif_annuel,     name='recapitulatif'),
    path('conformite/',                         views.rapport_conformite,       name='conformite'),

    # Déclaration — détail & workflow expert
    path('declaration/<int:pk>/',               views.detail_declaration,       name='detail_declaration'),
    path('declaration/<int:pk>/pdf/',           views.exporter_pdf_declaration, name='pdf_declaration'),
    path('declaration/<int:pk>/soumettre/',     views.soumettre_expert,         name='soumettre_expert'),
    path('declaration/<int:pk>/commenter/',     views.ajouter_commentaire,      name='ajouter_commentaire'),

    # Exports
    path('export/excel/',                       views.export_excel,             name='export_excel'),
    path('export/pdf/recapitulatif/',           views.export_pdf_recapitulatif, name='pdf_recapitulatif'),

    # Échéances
    path('echeance/ajouter/',                   views.ajouter_echeance,         name='ajouter_echeance'),
    path('echeance/<int:pk>/fait/',             views.marquer_echeance,         name='marquer_echeance'),
    path('echeance/<int:pk>/supprimer/',        views.supprimer_echeance,       name='supprimer_echeance'),
]
