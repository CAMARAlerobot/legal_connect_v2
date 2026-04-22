from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Dossier, Message, Commentaire, STATUTS_DOSSIER, TYPES_DOSSIER


def get_role(user):
    profil = getattr(user, 'profil', None)
    return profil.role if profil else 'commercant'


@login_required
def liste_dossiers(request):
    user = request.user
    role = get_role(user)

    if role in ['admin', 'institution']:
        dossiers = Dossier.objects.all().select_related('client', 'expert')
    elif role == 'expert':
        dossiers = Dossier.objects.filter(
            Q(expert=user) | Q(statut='en_attente', expert__isnull=True)
        ).select_related('client', 'expert')
    else:
        dossiers = Dossier.objects.filter(client=user).select_related('expert')

    # Filtres
    statut       = request.GET.get('statut', '')
    type_dossier = request.GET.get('type', '')
    recherche    = request.GET.get('q', '')

    if statut:
        dossiers = dossiers.filter(statut=statut)
    if type_dossier:
        dossiers = dossiers.filter(type_dossier=type_dossier)
    if recherche:
        dossiers = dossiers.filter(
            Q(titre__icontains=recherche) | Q(description__icontains=recherche)
        )

    # Stats (calculées avant pagination)
    total        = dossiers.count()
    en_attente   = dossiers.filter(statut='en_attente').count()
    en_cours     = dossiers.filter(statut='en_cours').count()
    valides      = dossiers.filter(statut='valide').count()

    # Messages non lus
    non_lus = Message.objects.filter(
        dossier__in=dossiers, lu=False
    ).exclude(auteur=user).count()

    # Pagination
    paginator = Paginator(dossiers.order_by('-created_at'), 9)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'dossiers'     : page_obj,
        'page_obj'     : page_obj,
        'statuts'      : STATUTS_DOSSIER,
        'types'        : TYPES_DOSSIER,
        'statut_actif' : statut,
        'type_actif'   : type_dossier,
        'recherche'    : recherche,
        'role'         : role,
        'total'        : total,
        'en_attente'   : en_attente,
        'en_cours'     : en_cours,
        'valides'      : valides,
        'non_lus'      : non_lus,
    }
    return render(request, 'collaboration/liste.html', context)


@login_required
def creer_dossier(request):
    role = get_role(request.user)

    if request.method == 'POST':
        titre        = request.POST.get('titre', '').strip()
        description  = request.POST.get('description', '').strip()
        type_dossier = request.POST.get('type_dossier', 'autre')
        priorite     = request.POST.get('priorite', 'normale')
        expert_id    = request.POST.get('expert_id') or None

        if not titre or not description:
            messages.error(request, 'Le titre et la description sont obligatoires.')
        else:
            expert = None
            if expert_id:
                expert = get_object_or_404(User, pk=expert_id)

            dossier = Dossier.objects.create(
                client       = request.user,
                expert       = expert,
                titre        = titre,
                description  = description,
                type_dossier = type_dossier,
                priorite     = priorite,
                statut       = 'en_attente',
            )
            messages.success(request, f'Dossier "{titre}" créé avec succès !')
            return redirect('collaboration:detail', pk=dossier.pk)

    # Liste des experts disponibles
    experts = User.objects.filter(profil__role='expert', is_active=True).select_related('profil')
    context = {
        'types'   : TYPES_DOSSIER,
        'experts' : experts,
        'role'    : role,
    }
    return render(request, 'collaboration/creer.html', context)


# Remplacez la fonction detail_dossier dans collaboration/views.py

@login_required
def detail_dossier(request, pk):
    user = request.user
    role = get_role(user)

    # Admin et institution voient tout
    if role in ['admin', 'institution']:
        dossier = get_object_or_404(Dossier, pk=pk)

    # Expert : voit ses dossiers assignés + les dossiers en attente sans expert
    elif role == 'expert':
        from django.db.models import Q
        try:
            dossier = Dossier.objects.get(pk=pk)
            # Vérifier accès : son dossier ou dossier sans expert
            if dossier.expert and dossier.expert != user:
                messages.error(request, 'Accès refusé.')
                return redirect('collaboration:liste')
        except Dossier.DoesNotExist:
            from django.http import Http404
            raise Http404

    # Client : voit uniquement ses propres dossiers
    else:
        dossier = get_object_or_404(Dossier, pk=pk, client=user)

    # Marquer les messages comme lus
    dossier.messages.exclude(auteur=user).update(lu=True)

    msgs         = dossier.messages.all().select_related('auteur')
    commentaires = dossier.commentaires.all().select_related('auteur')
    experts      = User.objects.filter(profil__role='expert', is_active=True)

    context = {
        'dossier'     : dossier,
        'msgs'        : msgs,
        'commentaires': commentaires,
        'experts'     : experts,
        'role'        : role,
    }
    return render(request, 'collaboration/detail.html', context)
@login_required
def envoyer_message(request, pk):
    user = request.user
    role = get_role(user)

    if role in ['admin', 'institution']:
        dossier = get_object_or_404(Dossier, pk=pk)
    elif role == 'expert':
        dossier = get_object_or_404(Dossier, pk=pk)
    else:
        dossier = get_object_or_404(Dossier, pk=pk, client=user)

    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        if contenu:
            Message.objects.create(
                dossier = dossier,
                auteur  = user,
                contenu = contenu,
            )
            # Mettre à jour le statut si expert répond
            if role == 'expert' and dossier.statut == 'en_attente':
                dossier.statut = 'en_cours'
                dossier.save()
        else:
            messages.error(request, 'Le message ne peut pas être vide.')

    return redirect('collaboration:detail', pk=pk)


@login_required
def valider_dossier(request, pk):
    role = get_role(request.user)
    if role not in ['expert', 'admin']:
        messages.error(request, 'Seul un expert peut valider un dossier.')
        return redirect('collaboration:liste')

    dossier = get_object_or_404(Dossier, pk=pk)

    if request.method == 'POST':
        action     = request.POST.get('action')
        note_expert = request.POST.get('note_expert', '').strip()

        if action == 'valider':
            dossier.statut     = 'valide'
            dossier.note_expert = note_expert
            dossier.expert     = request.user
            dossier.save()
            messages.success(request, f'Dossier "{dossier.titre}" validé !')
        elif action == 'rejeter':
            dossier.statut     = 'rejete'
            dossier.note_expert = note_expert
            dossier.expert     = request.user
            dossier.save()
            messages.warning(request, f'Dossier "{dossier.titre}" rejeté.')

    return redirect('collaboration:detail', pk=pk)


@login_required
def assigner_expert(request, pk):
    role = get_role(request.user)
    if role not in ['admin', 'institution']:
        messages.error(request, 'Accès refusé.')
        return redirect('collaboration:liste')

    dossier = get_object_or_404(Dossier, pk=pk)
    if request.method == 'POST':
        expert_id = request.POST.get('expert_id')
        if expert_id:
            expert         = get_object_or_404(User, pk=expert_id)
            dossier.expert = expert
            dossier.statut = 'en_cours'
            dossier.save()
            messages.success(request, f'Dossier assigné à {expert.first_name or expert.username} !')

    return redirect('collaboration:detail', pk=pk)


@login_required
def ajouter_commentaire(request, pk):
    user = request.user
    role = get_role(user)

    if role in ['admin', 'institution']:
        dossier = get_object_or_404(Dossier, pk=pk)
    elif role == 'expert':
        dossier = get_object_or_404(Dossier, pk=pk)
    else:
        dossier = get_object_or_404(Dossier, pk=pk, client=user)

    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        if contenu:
            Commentaire.objects.create(dossier=dossier, auteur=user, contenu=contenu)
            messages.success(request, 'Commentaire ajouté.')

    return redirect('collaboration:detail', pk=pk)


@login_required
def archiver_dossier(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk, client=request.user)
    dossier.statut = 'archive'
    dossier.save()
    messages.success(request, 'Dossier archivé.')
    return redirect('collaboration:liste')

