from django.db import models
from django.contrib.auth.models import User
import os

CATEGORIES = [
    ('contrat',     'Contrat'),
    ('facture',     'Facture'),
    ('declaration', 'Déclaration fiscale'),
    ('rapport',     'Rapport d\'activité'),
    ('identite',    'Pièce d\'identité'),
    ('registre',    'Registre de commerce'),
    ('juridique',   'Document juridique'),
    ('assurance',   'Assurance'),
    ('judiciaire',  'Document judiciaire'),
    ('autre',       'Autre'),
]

STATUTS_DOC = [
    ('prive',       'Privé'),
    ('partage',     'Partagé avec expert'),
    ('en_revision', 'En révision'),
    ('signe',       'Signé'),
    ('archive',     'Archivé'),
]


def upload_path(instance, filename):
    return f'documents/{instance.proprietaire.id}/{filename}'


def version_upload_path(instance, filename):
    return f'documents/{instance.document.proprietaire.id}/versions/{filename}'


class Document(models.Model):
    proprietaire    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    expert          = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents_partages'
    )
    # Partage multiple avec experts
    experts_partage = models.ManyToManyField(
        User, blank=True, related_name='documents_partages_multi'
    )

    titre           = models.CharField(max_length=200)
    description     = models.TextField(blank=True)
    categorie       = models.CharField(max_length=20, choices=CATEGORIES, default='autre')
    mots_cles       = models.CharField(max_length=300, blank=True, help_text='Mots-clés séparés par des virgules')
    numero_reference = models.CharField(max_length=100, blank=True, help_text='Référence interne ou légale')
    date_expiration = models.DateField(null=True, blank=True, help_text='Date d\'expiration du document')

    fichier         = models.FileField(upload_to=upload_path)
    statut          = models.CharField(max_length=20, choices=STATUTS_DOC, default='prive')
    taille          = models.PositiveIntegerField(default=0, help_text='Taille en octets')
    nb_telechargements = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

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

    @property
    def est_image(self):
        return self.extension in ('jpg', 'jpeg', 'png')

    @property
    def est_pdf(self):
        return self.extension == 'pdf'

    @property
    def tags_liste(self):
        if self.mots_cles:
            return [t.strip() for t in self.mots_cles.split(',') if t.strip()]
        return []

    @property
    def est_expire(self):
        if self.date_expiration:
            from datetime import date
            return self.date_expiration < date.today()
        return False

    @property
    def expire_bientot(self):
        if self.date_expiration:
            from datetime import date, timedelta
            return date.today() <= self.date_expiration <= date.today() + timedelta(days=30)
        return False

    class Meta:
        verbose_name        = 'Document'
        verbose_name_plural = 'Documents'
        ordering            = ['-created_at']


class VersionDocument(models.Model):
    """Historique des versions d'un document lors de ses modifications."""
    document    = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    fichier     = models.FileField(upload_to=version_upload_path)
    taille      = models.PositiveIntegerField(default=0)
    note        = models.CharField(max_length=300, blank=True, help_text='Note sur les changements')
    cree_par    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    numero      = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"v{self.numero} — {self.document.titre}"

    @property
    def taille_lisible(self):
        if self.taille < 1024:
            return f"{self.taille} o"
        elif self.taille < 1024 * 1024:
            return f"{self.taille // 1024} Ko"
        return f"{self.taille / (1024*1024):.1f} Mo"

    class Meta:
        verbose_name        = 'Version de document'
        verbose_name_plural = 'Versions de documents'
        ordering            = ['-numero']


class CommentaireDocument(models.Model):
    """Annotations et commentaires sur un document."""
    document    = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='commentaires')
    auteur      = models.ForeignKey(User, on_delete=models.CASCADE)
    texte       = models.TextField()
    est_expert  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.document.titre}"

    class Meta:
        verbose_name        = 'Commentaire de document'
        verbose_name_plural = 'Commentaires de documents'
        ordering            = ['created_at']
