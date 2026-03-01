from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'proprietaire', 'categorie', 'statut', 'taille_lisible', 'created_at']
    list_filter   = ['categorie', 'statut']
    search_fields = ['titre', 'proprietaire__username']
    readonly_fields = ['taille', 'created_at', 'updated_at']