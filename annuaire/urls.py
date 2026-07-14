from django.urls import path
from . import views

app_name = 'annuaire'

urlpatterns = [
    path('',                  views.liste_experts, name='liste'),
    path('<int:pk>/',         views.profil_expert, name='profil'),
    path('<int:pk>/avis/',    views.poster_avis,   name='poster_avis'),
]
