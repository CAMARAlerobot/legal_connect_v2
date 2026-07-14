from django.contrib import admin
from .models import AvisExpert


@admin.register(AvisExpert)
class AvisExpertAdmin(admin.ModelAdmin):
    list_display  = ['expert', 'auteur', 'note', 'valide', 'created_at']
    list_filter   = ['valide', 'note']
    search_fields = ['expert__username', 'auteur__username', 'commentaire']
    list_editable = ['valide']
    ordering      = ['-created_at']
