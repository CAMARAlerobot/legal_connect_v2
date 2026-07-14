import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .classifier import recommander_experts, modele_disponible
from collaboration.models import Dossier


@login_required
def page_recherche(request):
    """Page de recherche d'expert via ML."""
    return render(request, 'ml_recommandation/recherche.html', {
        'modele_actif': modele_disponible(),
    })


@login_required
@require_POST
def ajax_recommander(request):
    """Reçoit texte → retourne experts recommandés en JSON."""
    try:
        data      = json.loads(request.body)
        texte     = data.get('texte', '').strip()
        ville     = data.get('ville', '')
        budget    = data.get('budget_max')

        if len(texte) < 10:
            return JsonResponse(
                {'erreur': 'Description trop courte (minimum 10 caractères).'},
                status=400
            )

        resultats = recommander_experts(texte=texte, ville=ville, limit=3)

        experts_json = []
        for r in resultats['experts']:
            experts_json.append({
                'id':          r['expert'].pk,
                'nom':         r['expert'].get_full_name() or r['expert'].username,
                'email':       r['expert'].email,
                'specialite':  r['profil'].get_specialite_display() if r['profil'].specialite else '',
                'entreprise':  r['profil'].entreprise,
                'telephone':   r['profil'].telephone,
                'bio':         r['profil'].bio[:200] if r['profil'].bio else '',
                'note_moy':    r['note_moy'],
                'nb_avis':     r['nb_avis'],
                'nb_dossiers': r['nb_dossiers'],
                'score':       r['score'],
            })

        return JsonResponse({
            'classification': resultats['classification'],
            'experts':        experts_json,
            'total':          resultats['total_experts'],
        })

    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=500)


@login_required
@require_POST
def creer_dossier_ml(request):
    """Crée un dossier depuis la recommandation et l'assigne à l'expert."""
    try:
        data      = json.loads(request.body)
        expert_id = data.get('expert_id')
        texte     = data.get('texte', '').strip()
        categorie = data.get('categorie', '')
        titre     = (categorie + ' — ' + texte[:60]) if categorie else texte[:80]

        expert  = User.objects.get(pk=expert_id, profil__role='expert')
        dossier = Dossier.objects.create(
            client      = request.user,
            expert      = expert,
            titre       = titre,
            description = texte,
            type_dossier= 'juridique',
            statut      = 'en_cours',
        )

        return JsonResponse({
            'succes':       True,
            'dossier_id':   dossier.pk,
            'redirect_url': f'/collaboration/{dossier.pk}/',
        })

    except User.DoesNotExist:
        return JsonResponse({'erreur': 'Expert introuvable.'}, status=404)
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=500)