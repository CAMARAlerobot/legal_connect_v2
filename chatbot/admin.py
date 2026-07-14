from django.contrib import admin
from .models import ConversationChatbot, MessageChatbot


class MessageInline(admin.TabularInline):
    model      = MessageChatbot
    extra      = 0
    readonly_fields = ['expediteur', 'contenu', 'intention', 'escalade', 'cree_le']
    can_delete = False


@admin.register(ConversationChatbot)
class ConversationChatbotAdmin(admin.ModelAdmin):
    list_display  = ['session_id', 'utilisateur', 'cree_le']
    search_fields = ['session_id', 'utilisateur__username']
    list_filter   = ['cree_le']
    inlines       = [MessageInline]
    ordering      = ['-cree_le']


@admin.register(MessageChatbot)
class MessageChatbotAdmin(admin.ModelAdmin):
    list_display  = ['expediteur', 'contenu_court', 'intention', 'escalade', 'cree_le']
    list_filter   = ['expediteur', 'escalade', 'intention']
    search_fields = ['contenu', 'intention']
    ordering      = ['-cree_le']

    def contenu_court(self, obj):
        return obj.contenu[:60] + '…' if len(obj.contenu) > 60 else obj.contenu
    contenu_court.short_description = 'Message'
