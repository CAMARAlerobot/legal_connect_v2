# ml_recommandation/urls.py
from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('',         views.page_recherche,   name='recherche'),
    path('ajax/',    views.ajax_recommander, name='ajax'),
    path('dossier/', views.creer_dossier_ml, name='creer_dossier'),
]