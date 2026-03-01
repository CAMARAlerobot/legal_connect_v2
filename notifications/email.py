"""
Service d'envoi d'emails — Légal Connect.
Utilise Django's send_mail avec des templates HTML.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def envoyer_email(destinataire_email, sujet, template, contexte):
    """
    Envoie un email HTML à partir d'un template.
    Ne lève pas d'exception — log l'erreur en cas d'échec.
    """
    try:
        html_content  = render_to_string(f'notifications/emails/{template}', contexte)
        text_content  = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject     = f"[Légal Connect] {sujet}",
            body        = text_content,
            from_email  = settings.DEFAULT_FROM_EMAIL,
            to          = [destinataire_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        logger.info(f"Email envoyé à {destinataire_email} : {sujet}")
        return True
    except Exception as e:
        logger.error(f"Échec envoi email à {destinataire_email} : {e}")
        return False


def notifier_nouveau_dossier(dossier):
    """Notifie l'expert qu'un nouveau dossier lui est assigné."""
    if not dossier.expert:
        return
    contexte = {
        'expert'  : dossier.expert,
        'dossier' : dossier,
        'client'  : dossier.client,
    }
    envoyer_email(
        dossier.expert.email,
        f"Nouveau dossier : {dossier.titre}",
        'nouveau_dossier.html',
        contexte,
    )


def notifier_statut_dossier(dossier):
    """Notifie le client du changement de statut de son dossier."""
    contexte = {
        'client'  : dossier.client,
        'dossier' : dossier,
        'expert'  : dossier.expert,
    }
    sujet = f"Dossier {'validé' if dossier.statut == 'valide' else 'rejeté'} : {dossier.titre}"
    template = 'dossier_valide.html' if dossier.statut == 'valide' else 'dossier_rejete.html'
    envoyer_email(dossier.client.email, sujet, template, contexte)


def notifier_nouveau_message(message):
    """Notifie le destinataire d'un nouveau message."""
    dossier = message.dossier
    # Notifier l'autre partie
    if message.auteur == dossier.client:
        destinataire = dossier.expert
    else:
        destinataire = dossier.client

    if not destinataire or not destinataire.email:
        return

    contexte = {
        'destinataire': destinataire,
        'expediteur'  : message.auteur,
        'dossier'     : dossier,
        'message'     : message,
    }
    envoyer_email(
        destinataire.email,
        f"Nouveau message dans : {dossier.titre}",
        'nouveau_message.html',
        contexte,
    )


def notifier_contrat_genere(contrat):
    """Notifie l'utilisateur qu'un contrat a été généré."""
    contexte = {
        'user'    : contrat.proprietaire,
        'contrat' : contrat,
    }
    envoyer_email(
        contrat.proprietaire.email,
        f"Contrat généré : {contrat.titre}",
        'contrat_genere.html',
        contexte,
    )


def notifier_echeance(echeance, jours_restants):
    """Notifie l'utilisateur d'une échéance fiscale proche."""
    contexte = {
        'user'           : echeance.utilisateur,
        'echeance'       : echeance,
        'jours_restants' : jours_restants,
    }
    if jours_restants == 0:
        sujet    = f"⚠ Échéance dépassée : {echeance.titre}"
        template = 'echeance_depassee.html'
    elif jours_restants == 1:
        sujet    = f"⏰ Échéance demain : {echeance.titre}"
        template = 'echeance_1j.html'
    else:
        sujet    = f"📅 Échéance dans {jours_restants} jours : {echeance.titre}"
        template = 'echeance_7j.html'

    envoyer_email(echeance.utilisateur.email, sujet, template, contexte)


def notifier_document_partage(document):
    """Notifie l'expert qu'un document a été partagé avec lui."""
    if not document.expert:
        return
    contexte = {
        'expert'   : document.expert,
        'document' : document,
        'client'   : document.proprietaire,
    }
    envoyer_email(
        document.expert.email,
        f"Document partagé : {document.titre}",
        'document_partage.html',
        contexte,
    )