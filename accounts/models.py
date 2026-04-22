from django.db import models
from django.contrib.auth.models import User

ROLES = [
    ('commercant',  'Commerçant'),
    ('prestataire', 'Prestataire de services'),
    ('expert',      'Expert juridique / comptable'),
    ('institution', 'Institution / ONG'),
    ('admin',       'Administrateur'),
]

SPECIALITES = [
    ('droit_commercial',  'Droit Commercial'),
    ('droit_travail',     'Droit du Travail'),
    ('droit_fiscal',      'Droit Fiscal'),
    ('comptabilite',      'Comptabilité & Finance'),
    ('droit_immobilier',  'Droit Immobilier'),
    ('droit_penal',       'Droit Pénal des Affaires'),
    ('droit_civil',       'Droit Civil'),
    ('audit',             'Audit & Contrôle'),
]

class Profil(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role        = models.CharField(max_length=20, choices=ROLES, default='commercant')
    telephone   = models.CharField(max_length=20, blank=True)
    entreprise  = models.CharField(max_length=100, blank=True)
    adresse     = models.TextField(blank=True)
    bio         = models.TextField(blank=True)
    specialite  = models.CharField(max_length=30, choices=SPECIALITES, blank=True,
                                   help_text="Spécialité principale (experts uniquement)")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.utilisateur.username} — {self.get_role_display()}"

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'