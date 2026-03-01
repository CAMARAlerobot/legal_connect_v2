from django.contrib import admin
from .models import Declaration, Echeance

@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display  = ['utilisateur', 'type_impot', 'annee', 'montant_impot', 'statut', 'created_at']
    list_filter   = ['type_impot', 'statut', 'annee']
    search_fields = ['utilisateur__username']

@admin.register(Echeance)
class EcheanceAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'utilisateur', 'type_impot', 'date_limite', 'statut']
    list_filter   = ['type_impot', 'statut']