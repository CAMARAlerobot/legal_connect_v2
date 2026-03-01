from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import FileResponse, Http404
from django.db.models import Q
import os

from .models import Document, CATEGORIES
from .forms import DocumentForm


@login_required
def liste_documents(request):
    user   = request.user
    profil = getattr(user, 'profil', None)
    role   = profil.role if profil else 'commercant'

    # Selon le rôle
    if role in ['admin', 'institution']:
        documents = Document.objects.all()
    elif role == 'expert':
        documents = Document.objects.filter(
            Q(proprietaire=user) | Q(expert=user, statut='partage')
        )
    else:
        documents = Document.objects.filter(proprietaire=user)

    # Filtres
    categorie = request.GET.get('categorie', '')
    statut    = request.GET.get('statut', '')
    recherche = request.GET.get('q', '')

    if categorie:
        documents = documents.filter(categorie=categorie)
    if statut:
        documents = documents.filter(statut=statut)
    if recherche:
        documents = documents.filter(
            Q(titre__icontains=recherche) | Q(description__icontains=recherche)
        )

    # Stats
    total      = documents.count()
    total_size = sum(d.taille for d in documents)
    if total_size < 1024 * 1024:
        total_size_str = f"{total_size // 1024} Ko"
    else:
        total_size_str = f"{total_size / (1024*1024):.1f} Mo"

    context = {
        'documents'    : documents,
        'categories'   : CATEGORIES,
        'cat_active'   : categorie,
        'statut_actif' : statut,
        'recherche'    : recherche,
        'total'        : total,
        'total_size'   : total_size_str,
    }
    return render(request, 'documents/liste.html', context)


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.proprietaire = request.user
            if request.FILES.get('fichier'):
                doc.taille = request.FILES['fichier'].size
            doc.save()
            messages.success(request, f'Document "{doc.titre}" uploadé avec succès !')
            return redirect('documents:liste')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form})


@login_required
def detail_document(request, pk):
    user   = request.user
    profil = getattr(user, 'profil', None)
    role   = profil.role if profil else 'commercant'

    if role in ['admin', 'institution']:
        doc = get_object_or_404(Document, pk=pk)
    elif role == 'expert':
        doc = get_object_or_404(Document, pk=pk)
        if doc.proprietaire != user and not (doc.expert == user and doc.statut == 'partage'):
            raise Http404
    else:
        doc = get_object_or_404(Document, pk=pk, proprietaire=user)

    # Liste des experts pour partage
    from accounts.models import Profil
    experts = User.objects.filter(profil__role='expert', is_active=True)

    return render(request, 'documents/detail.html', {'doc': doc, 'experts': experts})


@login_required
def modifier_document(request, pk):
    doc = get_object_or_404(Document, pk=pk, proprietaire=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            doc = form.save(commit=False)
            if request.FILES.get('fichier'):
                doc.taille = request.FILES['fichier'].size
            doc.save()
            messages.success(request, 'Document mis à jour !')
            return redirect('documents:detail', pk=doc.pk)
    else:
        form = DocumentForm(instance=doc)
    return render(request, 'documents/modifier.html', {'form': form, 'doc': doc})


@login_required
def supprimer_document(request, pk):
    doc = get_object_or_404(Document, pk=pk, proprietaire=request.user)
    if request.method == 'POST':
        # Supprimer le fichier physique
        if doc.fichier and os.path.isfile(doc.fichier.path):
            os.remove(doc.fichier.path)
        doc.delete()
        messages.success(request, 'Document supprimé.')
        return redirect('documents:liste')
    return render(request, 'documents/supprimer.html', {'doc': doc})


@login_required
def telecharger_document(request, pk):
    """Téléchargement sécurisé — vérifie les droits avant d'envoyer."""
    user   = request.user
    profil = getattr(user, 'profil', None)
    role   = profil.role if profil else 'commercant'

    if role in ['admin', 'institution']:
        doc = get_object_or_404(Document, pk=pk)
    elif role == 'expert':
        doc = get_object_or_404(Document, pk=pk)
        if doc.proprietaire != user and not (doc.expert == user and doc.statut == 'partage'):
            raise Http404
    else:
        doc = get_object_or_404(Document, pk=pk, proprietaire=user)

    if not doc.fichier or not os.path.isfile(doc.fichier.path):
        messages.error(request, 'Fichier introuvable.')
        return redirect('documents:detail', pk=pk)

    response = FileResponse(open(doc.fichier.path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(doc.fichier.name)}"'
    return response


@login_required
def partager_document(request, pk):
    """Partager un document avec un expert."""
    doc = get_object_or_404(Document, pk=pk, proprietaire=request.user)
    if request.method == 'POST':
        expert_id = request.POST.get('expert_id')
        if expert_id:
            expert = get_object_or_404(User, pk=expert_id)
            doc.expert = expert
            doc.statut = 'partage'
            doc.save()
            messages.success(request, f'Document partagé avec {expert.first_name or expert.username} !')
        else:
            messages.error(request, 'Sélectionnez un expert.')
    return redirect('documents:detail', pk=pk)


@login_required
def archiver_document(request, pk):
    """Archiver un document."""
    doc = get_object_or_404(Document, pk=pk, proprietaire=request.user)
    doc.statut = 'archive'
    doc.save()
    messages.success(request, 'Document archivé.')
    return redirect('documents:liste')