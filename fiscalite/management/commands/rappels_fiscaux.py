"""
Commande de gestion : envoie des rappels email pour les échéances fiscales.

Usage :
    python manage.py rappels_fiscaux
    python manage.py rappels_fiscaux --dry-run   (simulation sans envoi)

À planifier via cron (Linux) ou Planificateur de tâches (Windows) :
    0 8 * * * /path/to/venv/bin/python manage.py rappels_fiscaux
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from fiscalite.models import Echeance


class Command(BaseCommand):
    help = "Envoie des rappels email pour les échéances fiscales à venir et en retard"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Affiche les rappels sans envoyer les emails",
        )

    def handle(self, *args, **options):
        dry_run     = options['dry_run']
        aujourd_hui = date.today()
        envoyes     = 0
        erreurs     = 0

        # Mettre à jour les statuts en retard
        Echeance.objects.filter(date_limite__lt=aujourd_hui, statut='a_faire').update(statut='en_retard')

        seuils = [1, 3, 7]  # jours avant échéance

        for jours in seuils:
            date_cible = aujourd_hui + timedelta(days=jours)
            echeances  = Echeance.objects.filter(
                date_limite=date_cible,
                statut='a_faire',
                rappel_email=True,
            ).select_related('utilisateur')

            for ech in echeances:
                email = ech.utilisateur.email
                if not email:
                    continue
                sujet = f"[Légal Connect] Rappel : {ech.titre} dans {jours} jour(s)"
                corps  = self._corps_email(ech, jours, 'a_venir')

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[DRY-RUN] → {email} | {ech.titre} dans {jours}j"
                        )
                    )
                else:
                    try:
                        send_mail(sujet, corps, settings.DEFAULT_FROM_EMAIL, [email])
                        envoyes += 1
                        self.stdout.write(self.style.SUCCESS(f"Email envoyé → {email} ({ech.titre})"))
                    except Exception as e:
                        erreurs += 1
                        self.stderr.write(self.style.ERROR(f"Erreur → {email} : {e}"))

        # Rappels pour les échéances en retard (envoi une seule fois le jour J+1)
        hier = aujourd_hui - timedelta(days=1)
        retards = Echeance.objects.filter(
            date_limite=hier,
            statut='en_retard',
            rappel_email=True,
        ).select_related('utilisateur')

        for ech in retards:
            email = ech.utilisateur.email
            if not email:
                continue
            sujet = f"[Légal Connect] URGENT : Échéance dépassée — {ech.titre}"
            corps  = self._corps_email(ech, 0, 'en_retard')

            if dry_run:
                self.stdout.write(self.style.ERROR(f"[DRY-RUN] RETARD → {email} | {ech.titre}"))
            else:
                try:
                    send_mail(sujet, corps, settings.DEFAULT_FROM_EMAIL, [email])
                    envoyes += 1
                    self.stdout.write(self.style.SUCCESS(f"Email retard envoyé → {email}"))
                except Exception as e:
                    erreurs += 1
                    self.stderr.write(self.style.ERROR(f"Erreur → {email} : {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTerminé — Emails envoyés : {envoyes} | Erreurs : {erreurs}"
                + (" (mode simulation)" if dry_run else "")
            )
        )

    def _corps_email(self, ech, jours, type_rappel):
        montant_str = f"{ech.montant:,.0f} FCFA" if ech.montant else "Non défini"
        base_url    = getattr(settings, 'SITE_URL', 'http://localhost:8000')

        if type_rappel == 'en_retard':
            intro = f"Votre échéance fiscale '{ech.titre}' est dépassée depuis hier."
            urgence = "ACTION REQUISE : Régularisez votre situation au plus vite pour éviter des pénalités supplémentaires."
        else:
            intro = f"Rappel : votre échéance fiscale '{ech.titre}' arrive dans {jours} jour(s)."
            urgence = f"Pensez à préparer votre déclaration avant le {ech.date_limite.strftime('%d/%m/%Y')}."

        return f"""Bonjour {ech.utilisateur.get_full_name() or ech.utilisateur.username},

{intro}

═══════════════════════════════════
  DÉTAILS DE L'ÉCHÉANCE
═══════════════════════════════════
  Titre       : {ech.titre}
  Type        : {ech.get_type_impot_display()}
  Date limite : {ech.date_limite.strftime('%d/%m/%Y')}
  Montant     : {montant_str}
  Statut      : {ech.get_statut_display()}
═══════════════════════════════════

{urgence}

Accédez à votre espace fiscal : {base_url}/fiscalite/calendrier/

{f"Notes : {ech.notes}" if ech.notes else ""}

---
Légal Connect — Plateforme Numérique d'Assistance Juridique
Université Nangui Abrogoua — Master 1 MIAGE 2025-2026
Ce message est automatique, merci de ne pas y répondre.
"""
