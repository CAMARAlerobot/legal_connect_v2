from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg

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
    ).order_by('-nb_dossiers')

    # Filtres
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

    # Calcul taux de validation
    experts_list = []
    for expert in experts:
        taux = 0
        if expert.nb_dossiers > 0:
            taux = round((expert.nb_valides / expert.nb_dossiers) * 100)
        experts_list.append({
            'user'          : expert,
            'profil'        : expert.profil,
            'nb_dossiers'   : expert.nb_dossiers,
            'nb_valides'    : expert.nb_valides,
            'taux_validation': taux,
        })

    context = {
        'experts'          : experts_list,
        'specialites'      : SPECIALITES,
        'specialite_active': specialite,
        'recherche'        : recherche,
        'total'            : len(experts_list),
    }
    return render(request, 'annuaire/liste.html', context)


@login_required
def profil_expert(request, pk):
    expert = get_object_or_404(User, pk=pk, profil__role='expert', is_active=True)
    profil = expert.profil

    from collaboration.models import Dossier
    dossiers = Dossier.objects.filter(expert=expert)
    nb_total  = dossiers.count()
    nb_valides = dossiers.filter(statut='valide').count()
    nb_rejetes = dossiers.filter(statut='rejete').count()
    nb_en_cours = dossiers.filter(statut='en_cours').count()
    taux = round((nb_valides / nb_total) * 100) if nb_total > 0 else 0

    context = {
        'expert'      : expert,
        'profil'      : profil,
        'nb_total'    : nb_total,
        'nb_valides'  : nb_valides,
        'nb_rejetes'  : nb_rejetes,
        'nb_en_cours' : nb_en_cours,
        'taux'        : taux,
        'specialites' : SPECIALITES,
    }
    return render(request, 'annuaire/profil.html', context)