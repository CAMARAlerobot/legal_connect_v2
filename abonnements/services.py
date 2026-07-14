"""
Verification des abonnements et des limites d'usage — Legal Connect.
Utilise par les autres apps (contrats, collaboration, chatbot...) pour
savoir si un utilisateur a droit a une action selon son plan.
"""
from datetime import timedelta

from django.utils import timezone

from .models import Abonnement

# Limites appliquees a un utilisateur qui n'a aucun abonnement actif
# (equivalent d'un plan gratuit implicite).
LIMITES_GRATUIT = {
    'max_contrats_mois':         1,
    'max_dossiers_mois':         2,
    'max_messages_chatbot_mois': 20,
}


def abonnement_actif(user):
    """Retourne l'Abonnement actif de l'utilisateur, ou None."""
    if not user.is_authenticated:
        return None
    return (
        Abonnement.objects
        .filter(utilisateur=user, statut='actif', date_fin__gte=timezone.now())
        .select_related('plan')
        .order_by('-date_fin')
        .first()
    )


def limite_pour(user, champ_limite):
    """
    Renvoie la limite (int) applicable a l'utilisateur pour ce champ, ou
    None si illimite. `champ_limite` doit correspondre a un champ de Plan
    (ex: 'max_contrats_mois').
    """
    abo = abonnement_actif(user)
    if abo:
        return getattr(abo.plan, champ_limite)
    return LIMITES_GRATUIT.get(champ_limite)


def limite_atteinte(user, champ_limite, queryset_utilisateur):
    """
    Verifie si l'utilisateur a atteint sa limite mensuelle pour ce champ.
    `queryset_utilisateur` doit deja etre filtre sur l'utilisateur concerne
    (ex: Contrat.objects.filter(proprietaire=user)) ; ce mois-ci est calcule
    ici a partir de `created_at`.

    Retourne False (jamais bloque) si la limite est None (illimite).
    """
    limite = limite_pour(user, champ_limite)
    if limite is None:
        return False
    debut_mois = timezone.now() - timedelta(days=30)
    return queryset_utilisateur.filter(created_at__gte=debut_mois).count() >= limite


def mise_en_avant(user):
    """Un expert avec un plan 'mise_en_avant_annuaire' doit apparaitre en tete de l'annuaire."""
    abo = abonnement_actif(user)
    return bool(abo and abo.plan.mise_en_avant_annuaire)
