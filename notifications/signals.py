"""
Signals Django — déclenchement automatique des notifications.
À connecter dans notifications/apps.py via ready().
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from collaboration.models import Dossier, Message
from contrats.models import Contrat
from documents.models import Document
from .models import Notification
from . import email as email_service


# ── DOSSIER ────────────────────────────────────────────────────────

@receiver(post_save, sender=Dossier)
def signal_dossier(sender, instance, created, **kwargs):
    dossier = instance

    if created:
        # Nouveau dossier → notifier l'expert si assigné
        if dossier.expert:
            Notification.objects.create(
                destinataire = dossier.expert,
                type_notif   = 'nouveau_dossier',
                titre        = f"Nouveau dossier : {dossier.titre}",
                message      = f"{dossier.client.first_name} {dossier.client.last_name} vous a soumis un dossier.",
                lien         = f"/collaboration/{dossier.pk}/",
            )
            email_service.notifier_nouveau_dossier(dossier)

    else:
        # Changement de statut → notifier le client
        if dossier.statut in ['valide', 'rejete']:
            Notification.objects.create(
                destinataire = dossier.client,
                type_notif   = f"dossier_{dossier.statut}",
                titre        = f"Dossier {'validé' if dossier.statut == 'valide' else 'rejeté'} : {dossier.titre}",
                message      = dossier.note_expert or "Votre dossier a été traité.",
                lien         = f"/collaboration/{dossier.pk}/",
            )
            email_service.notifier_statut_dossier(dossier)


# ── MESSAGE ────────────────────────────────────────────────────────

@receiver(post_save, sender=Message)
def signal_message(sender, instance, created, **kwargs):
    if not created:
        return

    msg     = instance
    dossier = msg.dossier
    destinataire = dossier.expert if msg.auteur == dossier.client else dossier.client

    if destinataire:
        Notification.objects.create(
            destinataire = destinataire,
            type_notif   = 'nouveau_message',
            titre        = f"Nouveau message dans : {dossier.titre}",
            message      = msg.contenu[:100] + ('...' if len(msg.contenu) > 100 else ''),
            lien         = f"/collaboration/{dossier.pk}/",
        )
        email_service.notifier_nouveau_message(msg)


# ── CONTRAT ────────────────────────────────────────────────────────

@receiver(post_save, sender=Contrat)
def signal_contrat(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            destinataire = instance.proprietaire,
            type_notif   = 'contrat_genere',
            titre        = f"Contrat généré : {instance.titre}",
            message      = f"Votre contrat '{instance.titre}' a été créé avec succès.",
            lien         = f"/contrats/{instance.pk}/",
        )
        email_service.notifier_contrat_genere(instance)


# ── DOCUMENT PARTAGÉ ───────────────────────────────────────────────

@receiver(pre_save, sender=Document)
def signal_document_partage(sender, instance, **kwargs):
    """Détecte quand un document passe en statut 'partage'."""
    if not instance.pk:
        return
    try:
        ancien = Document.objects.get(pk=instance.pk)
        if ancien.statut != 'partage' and instance.statut == 'partage' and instance.expert:
            Notification.objects.create(
                destinataire = instance.expert,
                type_notif   = 'document_partage',
                titre        = f"Document partagé : {instance.titre}",
                message      = f"{instance.proprietaire.first_name} {instance.proprietaire.last_name} a partagé un document avec vous.",
                lien         = f"/documents/{instance.pk}/",
            )
            email_service.notifier_document_partage(instance)
    except Document.DoesNotExist:
        pass