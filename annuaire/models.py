from django.db import models
from django.contrib.auth.models import User


class AvisExpert(models.Model):
    """Avis déposé par un client sur un expert."""
    expert      = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='avis_recus',
        limit_choices_to={'profil__role': 'expert'}
    )
    auteur      = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='avis_deposes'
    )
    note        = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} étoile(s)") for i in range(1, 6)]
    )
    commentaire = models.TextField(blank=True)
    valide      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Avis expert'
        verbose_name_plural = 'Avis experts'
        ordering            = ['-created_at']
        unique_together     = [['expert', 'auteur']]

    def __str__(self):
        return f"{self.note}★ — {self.auteur.username} → {self.expert.username}"