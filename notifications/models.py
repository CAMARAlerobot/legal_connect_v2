from django.db import models
from django.contrib.auth.models import User

TYPES_NOTIF = [
    ('nouveau_dossier',    'Nouveau dossier soumis'),
    ('dossier_valide',     'Dossier validé'),
    ('dossier_rejete',     'Dossier rejeté'),
    ('nouveau_message',    'Nouveau message reçu'),
    ('contrat_genere',     'Contrat généré'),
    ('echeance_7j',        'Échéance dans 7 jours'),
    ('echeance_1j',        'Échéance demain'),
    ('echeance_depassee',  'Échéance dépassée'),
    ('nouveau_commentaire','Nouveau commentaire'),
    ('document_partage',   'Document partagé'),
]

class Notification(models.Model):
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type_notif   = models.CharField(max_length=30, choices=TYPES_NOTIF)
    titre        = models.CharField(max_length=200)
    message      = models.TextField()
    lien         = models.CharField(max_length=300, blank=True)
    lu           = models.BooleanField(default=False)
    email_envoye = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} → {self.destinataire.username}"

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']