from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('',                      views.liste_notifications,   name='liste'),
    path('<int:pk>/lire/',        views.marquer_lue,           name='lire'),
    path('<int:pk>/supprimer/',   views.supprimer_notification, name='supprimer'),
    path('api/non-lues/',         views.api_non_lues,          name='api_non_lues'),
]