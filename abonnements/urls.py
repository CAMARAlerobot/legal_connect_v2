from django.urls import path
from . import views

app_name = 'abonnements'

urlpatterns = [
    path('',                        views.liste_plans,           name='liste_plans'),
    path('souscrire/<int:plan_id>/', views.souscrire,             name='souscrire'),
    path('mon-abonnement/',         views.mon_abonnement,        name='mon_abonnement'),
    path('<int:pk>/annuler-renouvellement/', views.annuler_renouvellement, name='annuler_renouvellement'),
    path('paiement/<int:pk>/simuler-confirmation/', views.simuler_confirmation_paiement, name='simuler_confirmation'),
    path('webhook/cinetpay/',       views.webhook_cinetpay,      name='webhook_cinetpay'),
    path('admin/',                  views.admin_gestion,         name='admin_gestion'),
]
