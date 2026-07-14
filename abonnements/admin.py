from django.contrib import admin
from .models import Plan, Abonnement, Paiement


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'role_cible', 'prix', 'periode_jours', 'actif')
    list_filter   = ('role_cible', 'actif', 'periode_jours')
    search_fields = ('nom',)


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display  = ('utilisateur', 'plan', 'statut', 'date_debut', 'date_fin', 'renouvellement_auto')
    list_filter   = ('statut', 'plan__role_cible')
    search_fields = ('utilisateur__username', 'utilisateur__email')
    autocomplete_fields = ('utilisateur', 'plan')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display  = ('reference_transaction', 'abonnement', 'montant', 'moyen_paiement', 'statut', 'created_at')
    list_filter   = ('statut', 'moyen_paiement')
    search_fields = ('reference_transaction', 'reference_externe', 'abonnement__utilisateur__username')
