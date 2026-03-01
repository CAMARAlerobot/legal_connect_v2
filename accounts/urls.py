from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',      views.connexion,   name='login'),
    path('logout/',     views.deconnexion, name='logout'),
    path('inscription/',views.inscription, name='inscription'),
    path('profil/',     views.profil,      name='profil'),
    path('admin/users/',views.admin_users, name='admin_users'),
    path('dashboard/',  views.dashboard,   name='dashboard'),
    
]