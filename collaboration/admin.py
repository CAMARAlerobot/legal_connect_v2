from django.contrib import admin
from .models import Dossier, Message, Commentaire

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'client', 'expert', 'type_dossier', 'statut', 'priorite', 'created_at']
    list_filter   = ['statut', 'type_dossier', 'priorite']
    search_fields = ['titre', 'client__username', 'expert__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['auteur', 'dossier', 'lu', 'created_at']
    list_filter   = ['lu']

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display  = ['auteur', 'dossier', 'created_at']