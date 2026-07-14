from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Abonnement, Paiement, Plan
from .paiement import cinetpay_configure, generer_reference_transaction, initier_paiement, verifier_paiement
from .services import abonnement_actif


def _role(user):
    profil = getattr(user, 'profil', None)
    return profil.role if profil else 'commercant'


def _est_admin(user):
    profil = getattr(user, 'profil', None)
    return bool(profil and profil.role == 'admin')


@login_required
def liste_plans(request):
    role   = _role(request.user)
    plans  = Plan.objects.filter(role_cible=role, actif=True)
    abo    = abonnement_actif(request.user)
    return render(request, 'abonnements/liste_plans.html', {
        'plans': plans,
        'abonnement_actif': abo,
    })


@login_required
def souscrire(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id, actif=True)

    if request.method == 'POST':
        abonnement = Abonnement.objects.create(
            utilisateur=request.user,
            plan=plan,
            statut='en_attente_paiement',
        )

        # Plan gratuit : activation immediate, pas de paiement a faire.
        if plan.est_gratuit:
            abonnement.activer()
            messages.success(request, f"Plan « {plan.nom} » activé.")
            return redirect('abonnements:mon_abonnement')

        moyen_paiement   = request.POST.get('moyen_paiement', 'orange_money')
        numero_telephone = request.POST.get('numero_telephone', '').strip()
        paiement = Paiement.objects.create(
            abonnement=abonnement,
            montant=plan.prix,
            moyen_paiement=moyen_paiement,
            numero_telephone=numero_telephone,
            reference_transaction=generer_reference_transaction(),
        )

        resultat = initier_paiement(paiement, request)

        if resultat['mode'] == 'cinetpay':
            return redirect(resultat['url'])
        elif resultat['mode'] == 'manuel':
            messages.info(request, resultat['instructions'])
            return redirect('abonnements:mon_abonnement')
        else:
            messages.error(request, f"Erreur lors de l'initialisation du paiement : {resultat.get('message', '')}")
            return redirect('abonnements:liste_plans')

    return render(request, 'abonnements/souscrire.html', {'plan': plan})


@login_required
def mon_abonnement(request):
    abo = abonnement_actif(request.user)
    historique = (
        Abonnement.objects
        .filter(utilisateur=request.user)
        .prefetch_related('paiements')
        .order_by('-created_at')
    )
    paiement_en_attente = (
        Paiement.objects
        .filter(abonnement__utilisateur=request.user, statut='en_attente')
        .select_related('abonnement__plan')
        .order_by('-created_at')
        .first()
    )
    return render(request, 'abonnements/mon_abonnement.html', {
        'abonnement_actif': abo,
        'historique': historique,
        'paiement_en_attente': paiement_en_attente,
        'mode_simulation': not cinetpay_configure(),
    })


@login_required
@require_POST
def annuler_renouvellement(request, pk):
    abo = get_object_or_404(Abonnement, pk=pk, utilisateur=request.user)
    abo.renouvellement_auto = False
    abo.save(update_fields=['renouvellement_auto'])
    messages.success(request, 'Renouvellement automatique désactivé.')
    return redirect('abonnements:mon_abonnement')


@login_required
@require_POST
def simuler_confirmation_paiement(request, pk):
    """
    Simule la confirmation Mobile Money par l'utilisateur sur son telephone,
    pour permettre une demonstration de bout en bout sans compte CinetPay actif.
    Garde-fou : refuse si CinetPay est reellement configure, pour ne jamais
    permettre de s'auto-valider un paiement qui devrait passer par le vrai
    operateur.
    """
    if cinetpay_configure():
        messages.error(request, "Simulation indisponible : un moyen de paiement réel est configuré.")
        return redirect('abonnements:mon_abonnement')

    paiement = get_object_or_404(
        Paiement, pk=pk, abonnement__utilisateur=request.user, statut='en_attente'
    )
    paiement.statut      = 'reussi'
    paiement.confirme_le = timezone.now()
    paiement.save(update_fields=['statut', 'confirme_le'])
    paiement.abonnement.activer()

    messages.success(request, f"Paiement confirmé — plan « {paiement.abonnement.plan.nom} » activé !")
    return redirect('abonnements:mon_abonnement')


@csrf_exempt
@require_POST
def webhook_cinetpay(request):
    """
    Endpoint appele par les serveurs CinetPay (notify_url) pour signaler
    l'issue d'un paiement. On ne fait jamais confiance au contenu POSTe
    directement : on revérifie le statut réel aupres de CinetPay avant de
    changer quoi que ce soit (verifier_paiement).
    """
    reference = request.POST.get('cpm_trans_id') or request.POST.get('transaction_id')
    if not reference:
        return HttpResponse(status=400)

    try:
        paiement = Paiement.objects.select_related('abonnement').get(reference_transaction=reference)
    except Paiement.DoesNotExist:
        return HttpResponse(status=404)

    statut = verifier_paiement(reference)

    if statut == 'reussi' and paiement.statut != 'reussi':
        paiement.statut      = 'reussi'
        paiement.confirme_le = timezone.now()
        paiement.save(update_fields=['statut', 'confirme_le'])
        paiement.abonnement.activer()
    elif statut == 'echoue':
        paiement.statut = 'echoue'
        paiement.save(update_fields=['statut'])

    return HttpResponse(status=200)


@login_required
def admin_gestion(request):
    """Espace admin : vue d'ensemble des abonnements et des revenus."""
    if not _est_admin(request.user):
        messages.error(request, 'Accès réservé aux administrateurs.')
        return redirect('dashboard')

    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    paiements_reussis = Paiement.objects.filter(statut='reussi')
    revenu_total    = paiements_reussis.aggregate(t=Sum('montant'))['t'] or 0
    revenu_ce_mois  = paiements_reussis.filter(created_at__gte=debut_mois).aggregate(t=Sum('montant'))['t'] or 0

    nb_actifs      = Abonnement.objects.filter(statut='actif', date_fin__gte=timezone.now()).count()
    nb_en_attente  = Abonnement.objects.filter(statut='en_attente_paiement').count()
    nb_echoues     = Paiement.objects.filter(statut='echoue').count()

    revenu_par_plan = (
        paiements_reussis
        .values('abonnement__plan__nom', 'abonnement__plan__role_cible')
        .annotate(total=Sum('montant'), nb=Count('id'))
        .order_by('-total')
    )

    revenu_par_moyen = (
        paiements_reussis
        .values('moyen_paiement')
        .annotate(total=Sum('montant'), nb=Count('id'))
        .order_by('-total')
    )

    statut_filtre = request.GET.get('statut', '')
    abonnements = Abonnement.objects.select_related('utilisateur', 'plan').order_by('-created_at')
    if statut_filtre:
        abonnements = abonnements.filter(statut=statut_filtre)

    paiements_recents = (
        Paiement.objects
        .select_related('abonnement__utilisateur', 'abonnement__plan')
        .order_by('-created_at')[:30]
    )

    return render(request, 'abonnements/admin_gestion.html', {
        'revenu_total':      revenu_total,
        'revenu_ce_mois':    revenu_ce_mois,
        'nb_actifs':         nb_actifs,
        'nb_en_attente':     nb_en_attente,
        'nb_echoues':        nb_echoues,
        'revenu_par_plan':   revenu_par_plan,
        'revenu_par_moyen':  revenu_par_moyen,
        'abonnements':       abonnements[:100],
        'paiements_recents': paiements_recents,
        'statut_filtre':     statut_filtre,
    })
