from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profil
from .forms import InscriptionForm, ProfilForm


def inscription(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profil.objects.get_or_create(
                utilisateur=user,
                defaults={
                    'role'      : form.cleaned_data['role'],
                    'telephone' : form.cleaned_data.get('telephone', ''),
                    'entreprise': form.cleaned_data.get('entreprise', ''),
                }
            )
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé.')
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'accounts/login.html')

def deconnexion(request):
    logout(request)
    return redirect('landing')

@login_required
def dashboard(request):
    user   = request.user
    profil, _ = Profil.objects.get_or_create(utilisateur=user)
    role   = profil.role

    from contrats.models import Contrat
    from documents.models import Document
    from collaboration.models import Dossier
    from fiscalite.models import Declaration, Echeance
    from notifications.models import Notification
    from django.utils import timezone
    from datetime import timedelta

    contrats     = Contrat.objects.filter(proprietaire=user)
    documents    = Document.objects.filter(proprietaire=user)
    declarations = Declaration.objects.filter(utilisateur=user)
    aujourd_hui  = timezone.now().date()

    if role == 'expert':
        dossiers = Dossier.objects.filter(expert=user)
    else:
        dossiers = Dossier.objects.filter(client=user)

    echeances_urgentes = Echeance.objects.filter(
        utilisateur=user,
        date_limite__gte=aujourd_hui,
        date_limite__lte=aujourd_hui + timedelta(days=7),
        statut='a_faire'
    ).count()

    non_lus = Notification.objects.filter(destinataire=user, lu=False).count()

    context = {
        'role'              : role,
        'profil'            : profil,
        'total_contrats'    : contrats.count(),
        'brouillons'        : contrats.filter(statut='brouillon').count(),
        'finalises'         : contrats.filter(statut='finalise').count(),
        'signes'            : contrats.filter(statut='signe').count(),
        'derniers_contrats' : contrats.order_by('-created_at')[:5],
        'total_documents'   : documents.count(),
        'total_dossiers'    : dossiers.count(),
        'dossiers_en_attente': dossiers.filter(statut='en_attente').count(),
        'total_declarations': declarations.count(),
        'echeances_urgentes': echeances_urgentes,
        'non_lus'           : non_lus,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profil(request):
    user = request.user
    profil_obj, _ = Profil.objects.get_or_create(utilisateur=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        user.email      = request.POST.get('email', '').strip()
        user.save()

        profil_obj.telephone  = request.POST.get('telephone', '').strip()
        profil_obj.entreprise = request.POST.get('entreprise', '').strip()
        profil_obj.adresse    = request.POST.get('adresse', '').strip()
        profil_obj.bio        = request.POST.get('bio', '').strip()
        if profil_obj.role == 'expert':
            profil_obj.specialite = request.POST.get('specialite', '')
        profil_obj.save()

        messages.success(request, 'Profil mis à jour avec succès !')
        return redirect('accounts:profil')

    from contrats.models import Contrat
    from documents.models import Document
    from collaboration.models import Dossier
    from fiscalite.models import Declaration

    context = {
        'user'           : user,
        'profil'         : profil_obj,
        'nb_contrats'    : Contrat.objects.filter(proprietaire=user).count(),
        'nb_documents'   : Document.objects.filter(proprietaire=user).count(),
        'nb_dossiers'    : Dossier.objects.filter(client=user).count(),
        'nb_declarations': Declaration.objects.filter(utilisateur=user).count(),
    }
    return render(request, 'accounts/profil.html', context)


@login_required
def admin_users(request):
    profil_obj, _ = Profil.objects.get_or_create(utilisateur=request.user)
    if profil_obj.role != 'admin':
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard')
    users = User.objects.all().select_related('profil').order_by('-date_joined')
    return render(request, 'accounts/admin_users.html', {'users': users})
# Ajoutez dans accounts/views.py

def landing(request):
    """Page d'accueil publique."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'landing.html')

