from django.db import models
from django.contrib.auth.models import User

TYPES_IMPOT = [
    ('tva',     'TVA — Taxe sur la Valeur Ajoutée'),
    ('is',      'IS — Impôt sur les Sociétés'),
    ('cnps',    'CNPS — Caisse Nationale de Prévoyance Sociale'),
    ('bnc',     'BNC — Bénéfices Non Commerciaux'),
    ('bic',     'BIC — Bénéfices Industriels et Commerciaux'),
    ('patente', 'Patente — Taxe professionnelle'),
    ('tse',     'TSE — Taxe Spéciale sur l\'Équipement'),
    ('imf',     'IMF — Impôt Minimum Forfaitaire'),
]

PERIODES = [
    ('mensuel',    'Mensuel'),
    ('trimestriel','Trimestriel'),
    ('annuel',     'Annuel'),
]

STATUTS_DECL = [
    ('en_attente',     'En attente'),
    ('soumise',        'Soumise'),
    ('en_revision',    'En révision'),
    ('validee',        'Validée'),
    ('en_retard',      'En retard'),
]


class Declaration(models.Model):
    utilisateur      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='declarations')
    type_impot       = models.CharField(max_length=10, choices=TYPES_IMPOT)
    periode          = models.CharField(max_length=15, choices=PERIODES, default='mensuel')
    annee            = models.PositiveIntegerField()
    mois             = models.PositiveIntegerField(null=True, blank=True, help_text="1-12 pour mensuel")
    trimestre        = models.PositiveIntegerField(null=True, blank=True, help_text="1-4 pour trimestriel")

    chiffre_affaires = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    charges          = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    benefice_net     = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    taux_applique    = models.DecimalField(max_digits=5,  decimal_places=2, default=0)
    montant_impot    = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    statut           = models.CharField(max_length=15, choices=STATUTS_DECL, default='en_attente')
    notes            = models.TextField(blank=True)

    # Workflow expert fiscal
    soumise_a_expert = models.BooleanField(default=False)
    expert           = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='declarations_a_reviser'
    )
    date_soumission_expert = models.DateTimeField(null=True, blank=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_impot_display()} — {self.annee} ({self.utilisateur.username})"

    class Meta:
        verbose_name        = 'Déclaration fiscale'
        verbose_name_plural = 'Déclarations fiscales'
        ordering            = ['-annee', '-created_at']


class CommentaireDeclaration(models.Model):
    declaration  = models.ForeignKey(Declaration, on_delete=models.CASCADE, related_name='commentaires')
    auteur       = models.ForeignKey(User, on_delete=models.CASCADE)
    texte        = models.TextField()
    est_expert   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur #{self.declaration.pk}"

    class Meta:
        verbose_name        = 'Commentaire de déclaration'
        verbose_name_plural = 'Commentaires de déclarations'
        ordering            = ['created_at']


class Echeance(models.Model):
    utilisateur  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='echeances')
    titre        = models.CharField(max_length=200)
    type_impot   = models.CharField(max_length=10, choices=TYPES_IMPOT)
    date_limite  = models.DateField()
    montant      = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    statut       = models.CharField(max_length=15, choices=[
        ('a_faire',  'À faire'),
        ('fait',     'Fait'),
        ('en_retard','En retard'),
    ], default='a_faire')
    rappel_email = models.BooleanField(default=True)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} — {self.date_limite}"

    class Meta:
        verbose_name        = 'Échéance fiscale'
        verbose_name_plural = 'Échéances fiscales'
        ordering            = ['date_limite']
