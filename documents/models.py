from django.db import models
from django.contrib.auth.models import User
import os

CATEGORIES = [
    ('contrat',       'Contrat'),
    ('facture',       'Facture'),
    ('declaration',   'Déclaration fiscale'),
    ('rapport',       'Rapport d\'activité'),
    ('identite',      'Pièce d\'identité'),
    ('registre',      'Registre de commerce'),
    ('autre',         'Autre'),
]

STATUTS_DOC = [
    ('prive',    'Privé'),
    ('partage',  'Partagé avec expert'),
    ('archive',  'Archivé'),
]

def upload_path(instance, filename):
    return f'documents/{instance.proprietaire.id}/{filename}'

class Document(models.Model):
    proprietaire  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    expert        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_partages')
    titre         = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    categorie     = models.CharField(max_length=20, choices=CATEGORIES, default='autre')
    fichier       = models.FileField(upload_to=upload_path)
    statut        = models.CharField(max_length=20, choices=STATUTS_DOC, default='prive')
    taille        = models.PositiveIntegerField(default=0, help_text='Taille en octets')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} ({self.proprietaire.username})"

    @property
    def extension(self):
        _, ext = os.path.splitext(self.fichier.name)
        return ext.lower().replace('.', '')

    @property
    def taille_lisible(self):
        if self.taille < 1024:
            return f"{self.taille} o"
        elif self.taille < 1024 * 1024:
            return f"{self.taille // 1024} Ko"
        else:
            return f"{self.taille / (1024*1024):.1f} Mo"

    @property
    def icone(self):
        icons = {
            'pdf'  : 'bi-file-pdf text-danger',
            'docx' : 'bi-file-word text-primary',
            'doc'  : 'bi-file-word text-primary',
            'xlsx' : 'bi-file-excel text-success',
            'xls'  : 'bi-file-excel text-success',
            'jpg'  : 'bi-file-image text-warning',
            'jpeg' : 'bi-file-image text-warning',
            'png'  : 'bi-file-image text-warning',
        }
        return icons.get(self.extension, 'bi-file-earmark text-secondary')

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']