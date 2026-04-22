from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profil
from .forms import InscriptionForm


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
                    'adresse'   : form.cleaned_data.get('adresse', ''),
                    'specialite': form.cleaned_data.get('specialite', ''),
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
    user      = request.user
    profil, _ = Profil.objects.get_or_create(utilisateur=user)
    role      = profil.role

    from contrats.models import Contrat
    from documents.models import Document
    from collaboration.models import Dossier, Message
    from fiscalite.models import Declaration, Echeance
    from notifications.models import Notification
    from django.utils import timezone
    from datetime import timedelta
    aujourd_hui = timezone.now().date()
    non_lus     = Notification.objects.filter(destinataire=user, lu=False).count()

    # ── Contexte commun ─────────────────────────────────────────────────────
    context = {'role': role, 'profil': profil, 'non_lus': non_lus}

    # ── EXPERT ───────────────────────────────────────────────────────────────
    if role == 'expert':
        dossiers       = Dossier.objects.filter(expert=user).select_related('client')
        dossiers_att   = Dossier.objects.filter(statut='en_attente', expert__isnull=True)
        docs_partages  = Document.objects.filter(experts_partage=user).select_related('proprietaire')
        messages_nlus  = Message.objects.filter(
            dossier__expert=user, lu=False
        ).exclude(auteur=user).count()
        nb_total       = dossiers.count()
        nb_valides     = dossiers.filter(statut='valide').count()
        taux           = round((nb_valides / nb_total) * 100) if nb_total > 0 else 0

        context.update({
            'dossiers_assignes'    : dossiers.order_by('-created_at')[:6],
            'dossiers_disponibles' : dossiers_att.order_by('-created_at')[:5],
            'docs_partages'        : docs_partages.order_by('-created_at')[:5],
            'nb_dossiers'          : nb_total,
            'nb_en_attente'        : dossiers.filter(statut='en_attente').count(),
            'nb_en_cours'          : dossiers.filter(statut='en_cours').count(),
            'nb_valides'           : nb_valides,
            'nb_rejetes'           : dossiers.filter(statut='rejete').count(),
            'taux_validation'      : taux,
            'messages_non_lus'     : messages_nlus,
            'nb_docs_partages'     : docs_partages.count(),
        })
        return render(request, 'accounts/dashboard_expert.html', context)

    # ── ADMIN / INSTITUTION ───────────────────────────────────────────────────
    if role in ['admin', 'institution']:
        from django.contrib.auth.models import User as UserModel
        all_users    = UserModel.objects.select_related('profil').order_by('-date_joined')
        all_dossiers = Dossier.objects.select_related('client', 'expert')
        all_contrats = Contrat.objects.all()
        all_decl     = Declaration.objects.all()

        context.update({
            'total_users'           : all_users.count(),
            'users_experts'         : all_users.filter(profil__role='expert').count(),
            'users_commercants'     : all_users.filter(profil__role='commercant').count(),
            'derniers_users'        : all_users[:6],
            'total_contrats'        : all_contrats.count(),
            'total_dossiers'        : all_dossiers.count(),
            'dossiers_en_attente'   : all_dossiers.filter(statut='en_attente').count(),
            'dossiers_sans_expert'  : all_dossiers.filter(statut='en_attente', expert__isnull=True),
            'total_declarations'    : all_decl.count(),
            'total_documents'       : Document.objects.count(),
            'derniers_dossiers'     : all_dossiers.order_by('-created_at')[:5],
        })
        return render(request, 'accounts/dashboard_admin.html', context)

    # ── COMMERÇANT / PRESTATAIRE (défaut) ────────────────────────────────────
    contrats     = Contrat.objects.filter(proprietaire=user)
    documents    = Document.objects.filter(proprietaire=user)
    declarations = Declaration.objects.filter(utilisateur=user)
    dossiers     = Dossier.objects.filter(client=user)
    docs_expires = documents.filter(date_expiration__lt=aujourd_hui).count()
    docs_bientot = documents.filter(
        date_expiration__gte=aujourd_hui,
        date_expiration__lte=aujourd_hui + timedelta(days=30)
    ).count()

    echeances_urgentes = Echeance.objects.filter(
        utilisateur=user,
        date_limite__gte=aujourd_hui,
        date_limite__lte=aujourd_hui + timedelta(days=7),
        statut='a_faire'
    ).count()

    prochaines_echeances = Echeance.objects.filter(
        utilisateur=user,
        date_limite__gte=aujourd_hui,
        statut='a_faire'
    ).order_by('date_limite')[:4]

    context.update({
        'total_contrats'      : contrats.count(),
        'brouillons'          : contrats.filter(statut='brouillon').count(),
        'finalises'           : contrats.filter(statut='finalise').count(),
        'signes'              : contrats.filter(statut='signe').count(),
        'derniers_contrats'   : contrats.order_by('-created_at')[:5],
        'total_documents'     : documents.count(),
        'docs_expires'        : docs_expires,
        'docs_bientot'        : docs_bientot,
        'derniers_documents'  : documents.order_by('-created_at')[:4],
        'total_dossiers'      : dossiers.count(),
        'dossiers_en_attente' : dossiers.filter(statut='en_attente').count(),
        'dossiers_en_cours'   : dossiers.filter(statut='en_cours').count(),
        'derniers_dossiers'   : dossiers.order_by('-created_at')[:3],
        'total_declarations'  : declarations.count(),
        'echeances_urgentes'  : echeances_urgentes,
        'prochaines_echeances': prochaines_echeances,
    })
    return render(request, 'accounts/dashboard_commercant.html', context)


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

