from django.db import models
from django.contrib.auth.models import User

TYPES_CONTRAT = [
    ('prestation',      'Contrat de prestation de service'),
    ('vente',           'Contrat de vente'),
    ('bail',            'Contrat de bail commercial'),
    ('travail',         'Contrat de travail'),
    ('partenariat',     'Contrat de partenariat'),
    ('collaboration',   'Convention de collaboration'),
    ('confidentialite', 'Accord de confidentialité (NDA)'),
]

STATUTS = [
    ('brouillon',  'Brouillon'),
    ('finalise',   'Finalisé'),
    ('signe',      'Signé'),
    ('archive',    'Archivé'),
]

class ModeleContrat(models.Model):
    """Modèles prédéfinis de contrats."""
    type_contrat = models.CharField(max_length=30, choices=TYPES_CONTRAT)
    titre        = models.CharField(max_length=200)
    description  = models.TextField()
    contenu      = models.TextField(help_text="Template avec variables {{nom_client}}, {{date}}, etc.")
    actif        = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} ({self.get_type_contrat_display()})"

    class Meta:
        verbose_name = 'Modèle de contrat'
        verbose_name_plural = 'Modèles de contrats'
        ordering = ['type_contrat', 'titre']


class Contrat(models.Model):
    """Contrat généré par un utilisateur."""
    proprietaire  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contrats')
    expert        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contrats_expert')
    modele        = models.ForeignKey(ModeleContrat, on_delete=models.SET_NULL, null=True, blank=True)
    type_contrat  = models.CharField(max_length=30, choices=TYPES_CONTRAT)
    titre         = models.CharField(max_length=200)
    statut        = models.CharField(max_length=20, choices=STATUTS, default='brouillon')

    # Parties du contrat
    nom_client         = models.CharField(max_length=200, verbose_name='Nom du client / Preneur')
    email_client       = models.EmailField(blank=True, verbose_name='Email du client')
    telephone_client   = models.CharField(max_length=20, blank=True)
    adresse_client     = models.TextField(blank=True)

    nom_prestataire    = models.CharField(max_length=200, verbose_name='Nom du prestataire / Bailleur')
    email_prestataire  = models.EmailField(blank=True)
    telephone_prestataire = models.CharField(max_length=20, blank=True)
    adresse_prestataire   = models.TextField(blank=True)

    # Détails
    objet              = models.TextField(verbose_name='Objet du contrat')
    montant            = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    devise             = models.CharField(max_length=10, default='FCFA')
    date_debut         = models.DateField(null=True, blank=True)
    date_fin           = models.DateField(null=True, blank=True)
    lieu_signature     = models.CharField(max_length=200, blank=True)
    clauses_speciales  = models.TextField(blank=True, verbose_name='Clauses particulières')
    contenu_final      = models.TextField(blank=True, verbose_name='Contenu final du contrat')

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} — {self.proprietaire.username}"

    class Meta:
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering = ['-created_at']