"""
Commande de gestion : marque comme expires les abonnements dont la date de
fin est depassee, et prepare un renouvellement en attente pour ceux qui ont
le renouvellement automatique active.

Usage :
    python manage.py expirer_abonnements
    python manage.py expirer_abonnements --dry-run   (simulation, rien n'est modifie)

A planifier via cron (Linux) ou Planificateur de taches (Windows), une fois
par jour par exemple :
    0 2 * * * /path/to/venv/bin/python manage.py expirer_abonnements
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from abonnements.models import Abonnement, Paiement
from abonnements.paiement import generer_reference_transaction


class Command(BaseCommand):
    help = "Marque comme expires les abonnements dont la date de fin est depassee."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Affiche ce qui serait fait sans modifier la base.",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        maintenant = timezone.now()

        a_expirer = Abonnement.objects.filter(statut='actif', date_fin__lt=maintenant).select_related('plan', 'utilisateur')

        nb_expires = 0
        nb_renouvellements_prepares = 0

        for abo in a_expirer:
            nb_expires += 1
            self.stdout.write(f"  Expiration : {abo.utilisateur.username} — {abo.plan.nom}")

            if not dry_run:
                abo.statut = 'expire'
                abo.save(update_fields=['statut'])

            if abo.renouvellement_auto and not abo.plan.est_gratuit:
                nb_renouvellements_prepares += 1
                self.stdout.write(f"    -> Renouvellement en attente prepare (plan payant)")
                if not dry_run:
                    nouvel_abo = Abonnement.objects.create(
                        utilisateur=abo.utilisateur,
                        plan=abo.plan,
                        statut='en_attente_paiement',
                        renouvellement_auto=True,
                    )
                    Paiement.objects.create(
                        abonnement=nouvel_abo,
                        montant=abo.plan.prix,
                        moyen_paiement='orange_money',
                        reference_transaction=generer_reference_transaction(),
                    )
            elif abo.renouvellement_auto and abo.plan.est_gratuit:
                # Plan gratuit : pas besoin de paiement, on reactive directement.
                if not dry_run:
                    nouvel_abo = Abonnement.objects.create(
                        utilisateur=abo.utilisateur, plan=abo.plan, statut='en_attente_paiement',
                        renouvellement_auto=True,
                    )
                    nouvel_abo.activer()

        prefixe = "[SIMULATION] " if dry_run else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefixe}{nb_expires} abonnement(s) expire(s), "
            f"{nb_renouvellements_prepares} renouvellement(s) payant(s) prepare(s)."
        ))
