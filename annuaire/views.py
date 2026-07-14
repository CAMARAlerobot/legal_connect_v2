from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg

from .models import AvisExpert

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


@login_required
def liste_experts(request):
    experts = User.objects.filter(
        profil__role='expert',
        is_active=True
    ).select_related('profil').annotate(
        nb_dossiers = Count('dossiers_expert', distinct=True),
        nb_valides  = Count(
            'dossiers_expert',
            filter=Q(dossiers_expert__statut='valide'),
            distinct=True
        ),
        note_moy = Avg('avis_recus__note', filter=Q(avis_recus__valide=True)),
        nb_avis  = Count('avis_recus', filter=Q(avis_recus__valide=True), distinct=True),
    ).order_by('-nb_dossiers')

    specialite = request.GET.get('specialite', '')
    recherche  = request.GET.get('q', '')

    if specialite:
        experts = experts.filter(profil__specialite=specialite)
    if recherche:
        experts = experts.filter(
            Q(first_name__icontains=recherche) |
            Q(last_name__icontains=recherche)  |
            Q(profil__entreprise__icontains=recherche) |
            Q(profil__bio__icontains=recherche)
        )

    experts_list = []
    for expert in experts:
        taux = 0
        if expert.nb_dossiers > 0:
            taux = round((expert.nb_valides / expert.nb_dossiers) * 100)
        experts_list.append({
            'user'           : expert,
            'profil'         : expert.profil,
            'nb_dossiers'    : expert.nb_dossiers,
            'nb_valides'     : expert.nb_valides,
            'taux_validation': taux,
            'note_moy'       : round(expert.note_moy, 1) if expert.note_moy else None,
            'nb_avis'        : expert.nb_avis,
        })

    return render(request, 'annuaire/liste.html', {
        'experts'          : experts_list,
        'specialites'      : SPECIALITES,
        'specialite_active': specialite,
        'recherche'        : recherche,
        'total'            : len(experts_list),
    })


@login_required
def profil_expert(request, pk):
    expert = get_object_or_404(User, pk=pk, profil__role='expert', is_active=True)
    profil = expert.profil

    from collaboration.models import Dossier
    dossiers    = Dossier.objects.filter(expert=expert)
    nb_total    = dossiers.count()
    nb_valides  = dossiers.filter(statut='valide').count()
    nb_rejetes  = dossiers.filter(statut='rejete').count()
    nb_en_cours = dossiers.filter(statut='en_cours').count()
    taux        = round((nb_valides / nb_total) * 100) if nb_total > 0 else 0

    avis_list  = AvisExpert.objects.filter(expert=expert, valide=True).select_related('auteur')
    stats_avis = avis_list.aggregate(note_moy=Avg('note'), nb_avis=Count('id'))
    note_moy   = round(stats_avis['note_moy'], 1) if stats_avis['note_moy'] else None
    nb_avis    = stats_avis['nb_avis']

    # Vérifie si l'utilisateur courant a déjà laissé un avis
    deja_avis = AvisExpert.objects.filter(expert=expert, auteur=request.user).exists()

    # Vérifie que l'utilisateur a eu un dossier validé avec cet expert
    peut_noter = (
        not deja_avis
        and request.user != expert
        and Dossier.objects.filter(client=request.user, expert=expert, statut='valide').exists()
    )

    return render(request, 'annuaire/profil.html', {
        'expert'      : expert,
        'profil'      : profil,
        'nb_total'    : nb_total,
        'nb_valides'  : nb_valides,
        'nb_rejetes'  : nb_rejetes,
        'nb_en_cours' : nb_en_cours,
        'taux'        : taux,
        'specialites' : SPECIALITES,
        'avis_list'   : avis_list,
        'note_moy'    : note_moy,
        'nb_avis'     : nb_avis,
        'peut_noter'  : peut_noter,
        'deja_avis'   : deja_avis,
    })


@login_required
def poster_avis(request, pk):
    expert = get_object_or_404(User, pk=pk, profil__role='expert', is_active=True)

    if request.user == expert:
        messages.error(request, "Vous ne pouvez pas noter votre propre profil.")
        return redirect('annuaire:profil', pk=pk)

    if AvisExpert.objects.filter(expert=expert, auteur=request.user).exists():
        messages.warning(request, "Vous avez déjà laissé un avis pour cet expert.")
        return redirect('annuaire:profil', pk=pk)

    if request.method == 'POST':
        try:
            note        = int(request.POST.get('note', 0))
            commentaire = request.POST.get('commentaire', '').strip()

            if not (1 <= note <= 5):
                messages.error(request, "La note doit être comprise entre 1 et 5.")
                return redirect('annuaire:profil', pk=pk)

            AvisExpert.objects.create(
                expert      = expert,
                auteur      = request.user,
                note        = note,
                commentaire = commentaire,
            )
            messages.success(request, f"Merci ! Votre avis ({note}★) a été publié.")
        except (ValueError, TypeError):
            messages.error(request, "Données invalides.")

    return redirect('annuaire:profil', pk=pk)
