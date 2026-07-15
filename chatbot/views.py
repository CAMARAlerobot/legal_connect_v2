import json
import uuid
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ConversationChatbot, MessageChatbot
from .moteur_ia import appeler_claude
from abonnements.services import limite_atteinte, limite_pour


@login_required
def page_chatbot(request):
    return render(request, 'chatbot/chatbot.html', {
        'api_active': bool(getattr(settings, 'ANTHROPIC_API_KEY', '')),
    })


@login_required
@require_POST
def ajax_message(request):
    try:
        data       = json.loads(request.body)
        message    = data.get('message', '').strip()
        session_id = data.get('session_id') or str(uuid.uuid4())

        if not message:
            return JsonResponse({'erreur': 'Message vide.'}, status=400)

        if len(message) > 2000:
            return JsonResponse({'erreur': 'Message trop long (max 2000 caractères).'}, status=400)

        messages_du_user = MessageChatbot.objects.filter(
            conversation__utilisateur=request.user,
            expediteur=MessageChatbot.Expediteur.UTILISATEUR,
        )
        if limite_atteinte(request.user, 'max_messages_chatbot_mois', messages_du_user, champ_date='cree_le'):
            limite = limite_pour(request.user, 'max_messages_chatbot_mois')
            return JsonResponse({
                'erreur': f"Vous avez atteint votre limite de {limite} messages ce mois-ci. "
                          "Passez à un plan supérieur pour continuer.",
                'limite_atteinte': True,
            }, status=403)

        # Récupérer ou créer la conversation
        conversation, _ = ConversationChatbot.objects.get_or_create(
            session_id=session_id,
            defaults={'utilisateur': request.user}
        )

        # Construire l'historique avant de sauvegarder le nouveau message
        messages_precedents = list(
            MessageChatbot.objects.filter(conversation=conversation)
            .order_by('cree_le')
            .values_list('expediteur', 'contenu')
        )
        # Garder seulement les 30 derniers
        messages_precedents = messages_precedents[-30:]

        # Sauvegarder le message utilisateur
        MessageChatbot.objects.create(
            conversation=conversation,
            expediteur=MessageChatbot.Expediteur.UTILISATEUR,
            contenu=message,
        )

        historique_claude = []
        for expediteur, contenu in messages_precedents:
            role = 'user' if expediteur == MessageChatbot.Expediteur.UTILISATEUR else 'assistant'
            historique_claude.append({'role': role, 'content': contenu})

        # Appeler Claude (ou fallback)
        resultat = appeler_claude(historique_claude, message)

        # Sauvegarder la réponse du bot
        MessageChatbot.objects.create(
            conversation=conversation,
            expediteur=MessageChatbot.Expediteur.BOT,
            contenu=resultat['reponse'],
            intention=resultat.get('intention', 'ia'),
            escalade=resultat.get('escalade', False),
        )

        return JsonResponse({
            'reponse':     resultat['reponse'],
            'escalade':    resultat.get('escalade', False),
            'suggestions': resultat.get('suggestions', []),
            'mode':        resultat.get('mode', 'ia'),
            'session_id':  session_id,
        })

    except Exception as e:
        return JsonResponse({'erreur': f'Erreur serveur : {str(e)}'}, status=500)
