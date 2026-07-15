from django.core.management.base import BaseCommand
from abonnements.models import Plan

PLANS_DEFAUT = [
    # role_cible, nom, prix, periode_jours, description,
    # max_contrats, max_dossiers, max_documents, max_chatbot, mise_en_avant
    ('commercant',  'Gratuit', 0,     30, "Pour démarrer.",
     1, 2, 3, 20, False),
    ('commercant',  'Pro',     5000,  30, "Contrats, dossiers, documents et chatbot illimités.",
     None, None, None, None, False),
    ('prestataire', 'Gratuit', 0,     30, "Pour démarrer.",
     1, 2, 3, 20, False),
    ('prestataire', 'Pro',     5000,  30, "Contrats, dossiers, documents et chatbot illimités.",
     None, None, None, None, False),
    ('expert',      'Gratuit', 0,     30, "Profil visible dans l'annuaire.",
     None, 2, 5, None, False),
    ('expert',      'Premium', 10000, 30, "Dossiers illimités et mise en avant dans l'annuaire.",
     None, None, None, None, True),
    ('institution',  'Institution', 20000, 30, "Toutes les fonctionnalités, sans limite.",
     None, None, None, None, False),
]


class Command(BaseCommand):
    help = "Cree ou met a jour les plans d'abonnement par defaut (idempotent)."

    def handle(self, *args, **options):
        crees = 0
        for role, nom, prix, periode, description, max_c, max_d, max_doc, max_ch, avant in PLANS_DEFAUT:
            _, cree = Plan.objects.update_or_create(
                role_cible=role, nom=nom,
                defaults={
                    'prix': prix,
                    'periode_jours': periode,
                    'description': description,
                    'max_contrats_mois': max_c,
                    'max_dossiers_mois': max_d,
                    'max_documents_mois': max_doc,
                    'max_messages_chatbot_mois': max_ch,
                    'mise_en_avant_annuaire': avant,
                },
            )
            crees += int(cree)
        self.stdout.write(self.style.SUCCESS(
            f"{crees} plan(s) cree(s), {len(PLANS_DEFAUT) - crees} mis a jour."
        ))
