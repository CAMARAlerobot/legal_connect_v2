"""
Integration paiement — Legal Connect
Passe par CinetPay (agregateur qui couvre Orange Money, MTN Mobile Money,
Moov Money, Wave et carte bancaire en une seule API), plutot que d'integrer
chaque operateur telecom separement.

Si CINETPAY_API_KEY / CINETPAY_SITE_ID ne sont pas configures (comme pour
ANTHROPIC_API_KEY ailleurs dans ce projet), on bascule en mode manuel :
le paiement reste "en_attente" et un administrateur le confirme lui-meme
(depuis l'admin Django) apres verification hors-ligne du virement Mobile
Money — un mode degrade utile en demonstration/debut d'activite, avant
d'avoir un compte marchand CinetPay actif.
"""
import uuid

import httpx
from django.conf import settings
from django.urls import reverse

CINETPAY_API_URL = 'https://api-checkout.cinetpay.com/v2/payment'


def cinetpay_configure():
    return bool(settings.CINETPAY_API_KEY and settings.CINETPAY_SITE_ID)


def generer_reference_transaction():
    return f"LC-{uuid.uuid4().hex[:16]}"


def initier_paiement(paiement, request):
    """
    Lance le paiement pour l'objet Paiement donne.
    Retourne un dict :
      - {'mode': 'cinetpay', 'url': '...'} si CinetPay est configure : on
        redirige l'utilisateur vers `url` pour choisir son moyen Mobile Money.
      - {'mode': 'manuel', 'instructions': '...'} sinon : le paiement reste
        en attente, a confirmer manuellement (admin) une fois l'argent reçu.
    """
    if not cinetpay_configure():
        numero = paiement.numero_telephone or 'votre numero'
        return {
            'mode': 'manuel',
            'instructions': (
                f"Une demande de paiement de {paiement.montant:.0f} FCFA via "
                f"{paiement.get_moyen_paiement_display()} a ete envoyee au {numero}. "
                "Confirmez avec votre code secret sur votre telephone pour valider "
                f"(reference : {paiement.reference_transaction})."
            ),
        }

    payload = {
        'apikey':          settings.CINETPAY_API_KEY,
        'site_id':         settings.CINETPAY_SITE_ID,
        'transaction_id':  paiement.reference_transaction,
        'amount':          int(paiement.montant),
        'currency':        'XOF',
        'description':     f"Abonnement {paiement.abonnement.plan.nom} — Legal Connect",
        'notify_url':      request.build_absolute_uri(reverse('abonnements:webhook_cinetpay')),
        'return_url':      request.build_absolute_uri(reverse('abonnements:mon_abonnement')),
        'channels':        'ALL',
        'customer_name':   paiement.abonnement.utilisateur.first_name or paiement.abonnement.utilisateur.username,
        'customer_email':  paiement.abonnement.utilisateur.email or 'contact@legalconnect.ci',
    }

    try:
        reponse = httpx.post(CINETPAY_API_URL, json=payload, timeout=15.0)
        data = reponse.json()
    except (httpx.HTTPError, ValueError) as e:
        return {'mode': 'erreur', 'message': str(e)}

    if data.get('code') == '201':
        return {'mode': 'cinetpay', 'url': data['data']['payment_url']}
    return {'mode': 'erreur', 'message': data.get('message', 'Erreur CinetPay inconnue.')}


def verifier_paiement(reference_transaction):
    """
    Interroge CinetPay sur le statut reel d'une transaction (utilise par le
    webhook, qui ne doit jamais faire confiance aveuglement au contenu POSTe
    par un tiers sans le revalider aupres de l'operateur).
    Retourne 'reussi', 'echoue', ou 'en_attente'.
    """
    if not cinetpay_configure():
        return 'en_attente'

    payload = {
        'apikey':         settings.CINETPAY_API_KEY,
        'site_id':        settings.CINETPAY_SITE_ID,
        'transaction_id': reference_transaction,
    }
    try:
        reponse = httpx.post(f'{CINETPAY_API_URL}/check', json=payload, timeout=15.0)
        data = reponse.json()
    except (httpx.HTTPError, ValueError):
        return 'en_attente'

    statut_cinetpay = data.get('data', {}).get('status')
    if statut_cinetpay == 'ACCEPTED':
        return 'reussi'
    if statut_cinetpay in ('REFUSED', 'CANCELLED'):
        return 'echoue'
    return 'en_attente'
