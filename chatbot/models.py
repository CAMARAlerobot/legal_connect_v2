from django.db import models
from django.contrib.auth.models import User


class ConversationChatbot(models.Model):
    """Historique des conversations avec le chatbot."""
    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='conversations_chatbot'
    )
    session_id  = models.CharField(max_length=100, db_index=True)
    cree_le     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering    = ['-cree_le']
        verbose_name = 'Conversation chatbot'

    def __str__(self):
        return f"Session {self.session_id[:8]} — {self.cree_le:%d/%m/%Y}"


class MessageChatbot(models.Model):
    """Un message dans une conversation chatbot."""

    class Expediteur(models.TextChoices):
        UTILISATEUR = 'user', 'Utilisateur'
        BOT         = 'bot',  'Chatbot'

    conversation = models.ForeignKey(
        ConversationChatbot, on_delete=models.CASCADE,
        related_name='messages'
    )
    expediteur   = models.CharField(max_length=4, choices=Expediteur.choices)
    contenu      = models.TextField()
    intention    = models.CharField(max_length=50, blank=True)
    escalade     = models.BooleanField(default=False)
    cree_le      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering    = ['cree_le']
        verbose_name = 'Message chatbot'

    def __str__(self):
        return f"[{self.expediteur}] {self.contenu[:50]}"