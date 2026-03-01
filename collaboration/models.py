from django.db import models
from django.contrib.auth.models import User

STATUTS_DOSSIER = [
    ('en_attente',  'En attente'),
    ('en_cours',    'En cours'),
    ('valide',      'Validé'),
    ('rejete',      'Rejeté'),
    ('archive',     'Archivé'),
]

TYPES_DOSSIER = [
    ('contrat',     'Révision de contrat'),
    ('fiscal',      'Conseil fiscal'),
    ('juridique',   'Conseil juridique'),
    ('document',    'Vérification de document'),
    ('autre',       'Autre'),
]

class Dossier(models.Model):
    """Dossier soumis par un client à un expert."""
    client      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dossiers_client')
    expert      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dossiers_expert')
    titre       = models.CharField(max_length=200)
    description = models.TextField()
    type_dossier= models.CharField(max_length=20, choices=TYPES_DOSSIER, default='autre')
    statut      = models.CharField(max_length=15, choices=STATUTS_DOSSIER, default='en_attente')
    priorite    = models.CharField(max_length=10, choices=[
        ('basse',   'Basse'),
        ('normale', 'Normale'),
        ('haute',   'Haute'),
        ('urgente', 'Urgente'),
    ], default='normale')
    note_expert = models.TextField(blank=True, help_text="Avis / conclusion de l'expert")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} ({self.client.username})"

    @property
    def nb_messages(self):
        return self.messages.count()

    class Meta:
        verbose_name = 'Dossier'
        verbose_name_plural = 'Dossiers'
        ordering = ['-created_at']


class Message(models.Model):
    """Message dans un dossier (fil de discussion)."""
    dossier    = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='messages')
    auteur     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    contenu    = models.TextField()
    lu         = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.auteur.username} — {self.dossier.titre}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']


class Commentaire(models.Model):
    """Commentaire sur un document dans un dossier."""
    dossier    = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='commentaires')
    auteur     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires')
    contenu    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur.username}"

    class Meta:
        verbose_name = 'Commentaire'
        ordering = ['created_at']