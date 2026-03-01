from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('',                    views.liste_documents,   name='liste'),
    path('upload/',             views.upload_document,   name='upload'),
    path('<int:pk>/',           views.detail_document,   name='detail'),
    path('<int:pk>/modifier/',  views.modifier_document, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_document,name='supprimer'),
    path('<int:pk>/telecharger/',views.telecharger_document, name='telecharger'),
    path('<int:pk>/partager/',  views.partager_document, name='partager'),
    path('<int:pk>/archiver/',  views.archiver_document, name='archiver'),
]