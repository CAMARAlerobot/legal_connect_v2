from django.contrib import admin
from .models import Document, VersionDocument, CommentaireDocument


class VersionInline(admin.TabularInline):
    model       = VersionDocument
    extra       = 0
    fields      = ('numero', 'note', 'taille', 'cree_par', 'created_at')
    readonly_fields = ('taille', 'created_at')


class CommentaireInline(admin.TabularInline):
    model       = CommentaireDocument
    extra       = 0
    fields      = ('auteur', 'texte', 'est_expert', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display    = ('titre', 'proprietaire', 'categorie', 'statut', 'taille_lisible', 'nb_telechargements', 'date_expiration', 'created_at')
    list_filter     = ('categorie', 'statut', 'created_at')
    search_fields   = ('titre', 'proprietaire__username', 'numero_reference', 'mots_cles')
    readonly_fields = ('taille', 'nb_telechargements', 'created_at', 'updated_at')
    filter_horizontal = ('experts_partage',)
    inlines         = [VersionInline, CommentaireInline]
    fieldsets = (
        ('Identification', {
            'fields': ('proprietaire', 'titre', 'categorie', 'numero_reference', 'mots_cles', 'description')
        }),
        ('Fichier', {
            'fields': ('fichier', 'taille', 'nb_telechargements')
        }),
        ('Statut & Partage', {
            'fields': ('statut', 'expert', 'experts_partage', 'date_expiration')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(VersionDocument)
class VersionAdmin(admin.ModelAdmin):
    list_display    = ('document', 'numero', 'note', 'taille', 'cree_par', 'created_at')
    list_filter     = ('created_at',)
    search_fields   = ('document__titre', 'note')
    readonly_fields = ('created_at',)


@admin.register(CommentaireDocument)
class CommentaireAdmin(admin.ModelAdmin):
    list_display    = ('document', 'auteur', 'est_expert', 'created_at')
    list_filter     = ('est_expert', 'created_at')
    search_fields   = ('document__titre', 'auteur__username', 'texte')
    readonly_fields = ('created_at',)
