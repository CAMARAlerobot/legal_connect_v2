from django.contrib import admin
from .models import ModeleContrat, Contrat


@admin.register(ModeleContrat)
class ModeleContratAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'type_contrat', 'actif', 'created_at']
    list_filter   = ['type_contrat', 'actif']
    search_fields = ['titre', 'description']
    list_editable = ['actif']


@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'proprietaire', 'type_contrat', 'statut', 'created_at']
    list_filter   = ['statut', 'type_contrat']
    search_fields = ['titre', 'nom_client', 'nom_prestataire']
    readonly_fields = ['created_at', 'updated_at']