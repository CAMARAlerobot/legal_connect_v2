from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'destinataire', 'type_notif', 'lu', 'email_envoye', 'created_at']
    list_filter   = ['type_notif', 'lu', 'email_envoye']
    search_fields = ['titre', 'destinataire__username']
    readonly_fields = ['created_at']