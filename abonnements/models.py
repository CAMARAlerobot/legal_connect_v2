from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import ROLES

PERIODES = [
    (30,  'Mensuel'),
    (365, 'Annuel'),
]

MOYENS_PAIEMENT = [
    ('orange_money', 'Orange Money'),
    ('mtn_money',     'MTN Mobile Money'),
    ('moov_money',    'Moov Money'),
    ('wave',          'Wave'),
    ('carte',         'Carte bancaire'),
]

STATUTS_ABONNEMENT = [
    ('en_attente_paiement', 'En attente de paiement'),
    ('actif',               'Actif'),
    ('expire',              'Expiré'),
    ('annule',              'Annulé'),
]

STATUTS_PAIEMENT = [
    ('en_attente', 'En attente'),
    ('reussi',     'Réussi'),
    ('echoue',     'Échoué'),
    ('rembourse',  'Remboursé'),
]


class Plan(models.Model):
    """Un palier d'abonnement propose a un role donne."""
    nom          = models.CharField(max_length=100)
    role_cible   = models.CharField(max_length=20, choices=ROLES,
                                     help_text="Role auquel ce plan s'adresse")
    prix         = models.DecimalField(max_digits=10, decimal_places=0, help_text="Prix en FCFA")
    periode_jours = models.PositiveIntegerField(choices=PERIODES, default=30)
    description  = models.TextField(blank=True)

    # Limites d'usage — null = illimite
    max_contrats_mois          = models.PositiveIntegerField(null=True, blank=True)
    max_dossiers_mois          = models.PositiveIntegerField(null=True, blank=True)
    max_documents_mois         = models.PositiveIntegerField(null=True, blank=True)
    max_messages_chatbot_mois  = models.PositiveIntegerField(null=True, blank=True)
    mise_en_avant_annuaire     = models.BooleanField(
        default=False, help_text="Reserve aux experts : mise en avant dans l'annuaire"
    )

    actif      = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.get_role_cible_display()}) — {self.prix:.0f} FCFA"

    @property
    def est_gratuit(self):
        return self.prix == 0

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        ordering = ['role_cible', 'prix']


class Abonnement(models.Model):
    """Souscription d'un utilisateur a un plan, pour une periode donnee."""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abonnements')
    plan        = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='abonnements')
    statut      = models.CharField(max_length=25, choices=STATUTS_ABONNEMENT, default='en_attente_paiement')
    date_debut  = models.DateTimeField(null=True, blank=True)
    date_fin    = models.DateTimeField(null=True, blank=True)
    renouvellement_auto = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur.username} — {self.plan.nom} ({self.get_statut_display()})"

    @property
    def est_actif(self):
        return (
            self.statut == 'actif'
            and self.date_fin is not None
            and self.date_fin >= timezone.now()
        )

    def activer(self):
        """Active l'abonnement pour la periode du plan, a partir de maintenant."""
        maintenant = timezone.now()
        self.statut     = 'actif'
        self.date_debut = maintenant
        self.date_fin   = maintenant + timezone.timedelta(days=self.plan.periode_jours)
        self.save(update_fields=['statut', 'date_debut', 'date_fin'])

    class Meta:
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        ordering = ['-created_at']


class Paiement(models.Model):
    """Une tentative de paiement pour activer un abonnement."""
    abonnement          = models.ForeignKey(Abonnement, on_delete=models.CASCADE, related_name='paiements')
    montant             = models.DecimalField(max_digits=10, decimal_places=0)
    moyen_paiement      = models.CharField(max_length=20, choices=MOYENS_PAIEMENT)
    numero_telephone    = models.CharField(max_length=20, blank=True,
                                            help_text="Numero Mobile Money a debiter (saisi par l'utilisateur)")
    reference_transaction = models.CharField(max_length=100, unique=True,
                                              help_text="Identifiant genere cote Legal Connect")
    reference_externe   = models.CharField(max_length=150, blank=True,
                                            help_text="Identifiant renvoye par l'operateur/CinetPay")
    statut              = models.CharField(max_length=15, choices=STATUTS_PAIEMENT, default='en_attente')
    created_at          = models.DateTimeField(auto_now_add=True)
    confirme_le         = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Paiement {self.reference_transaction} — {self.montant:.0f} FCFA ({self.get_statut_display()})"

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-created_at']
