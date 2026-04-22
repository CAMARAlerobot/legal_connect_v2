from django.contrib import admin
from .models import Declaration, Echeance, CommentaireDeclaration


class CommentaireInline(admin.TabularInline):
    model       = CommentaireDeclaration
    extra       = 0
    fields      = ('auteur', 'texte', 'est_expert', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display    = ('utilisateur', 'type_impot', 'annee', 'periode', 'montant_impot', 'statut', 'soumise_a_expert', 'created_at')
    list_filter     = ('type_impot', 'statut', 'annee', 'soumise_a_expert', 'periode')
    search_fields   = ('utilisateur__username', 'utilisateur__email')
    readonly_fields = ('created_at', 'updated_at', 'date_soumission_expert')
    inlines         = [CommentaireInline]
    fieldsets = (
        ('Identification', {
            'fields': ('utilisateur', 'type_impot', 'periode', 'annee', 'mois', 'trimestre')
        }),
        ('Données financières', {
            'fields': ('chiffre_affaires', 'charges', 'benefice_net', 'taux_applique', 'montant_impot')
        }),
        ('Statut & Workflow', {
            'fields': ('statut', 'soumise_a_expert', 'expert', 'date_soumission_expert', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Echeance)
class EcheanceAdmin(admin.ModelAdmin):
    list_display   = ('titre', 'utilisateur', 'type_impot', 'date_limite', 'montant', 'statut', 'rappel_email')
    list_filter    = ('type_impot', 'statut', 'rappel_email')
    search_fields  = ('titre', 'utilisateur__username')
    date_hierarchy = 'date_limite'


@admin.register(CommentaireDeclaration)
class CommentaireAdmin(admin.ModelAdmin):
    list_display    = ('declaration', 'auteur', 'est_expert', 'created_at')
    list_filter     = ('est_expert',)
    search_fields   = ('auteur__username', 'texte')
    readonly_fields = ('created_at',)
