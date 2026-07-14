"""
Moteur IA du chatbot — propulsé par Claude claude-haiku-4-5 (Anthropic)
Fallback intelligent sur le moteur à règles si pas de clé API.
"""
import anthropic
from django.conf import settings

SYSTEM_PROMPT = """Tu es LegalBot, l'assistant juridique intelligent de la plateforme Légal Connect.
Légal Connect est une plateforme ivoirienne qui aide les commerçants, prestataires et entreprises à gérer leurs contrats, documents légaux, déclarations fiscales et dossiers juridiques.

## Qui tu es
- Un assistant juridique et fiscal expert, spécialisé dans la législation de la Côte d'Ivoire
- Chaleureux, humain, professionnel — tu réponds à TOUTES les questions, qu'elles soient juridiques ou générales
- Tu parles toujours en français
- Tu es disponible 24h/24 pour aider les utilisateurs

## Ce que tu sais faire
- Répondre aux questions générales (salutations, comment tu vas, aide générale)
- Expliquer le droit ivoirien : Code du Travail, Code de Commerce, Code Pénal, droit civil, droit immobilier
- Calculer et expliquer les impôts : TVA (18%), Impôt sur les Sociétés (20-30%), CNPS (23,2%), BIC (25%), BNC (20%), Patente, TPS
- Guider dans les démarches : création d'entreprise au CEPICI, dépôt de plainte, procédures judiciaires, tribunal de commerce
- Rédiger et expliquer des modèles de contrats, baux, lettres de mise en demeure
- Orienter vers les bonnes institutions : CNPS, DGI, CEPICI, RCCM, Tribunal de Commerce d'Abidjan, Barreau de CI
- Expliquer les délais légaux, les recours, les droits des travailleurs et employeurs
- Aider sur les litiges commerciaux, les impayés, les licenciements, les créations de SARL/SA

## Taux fiscaux CI 2026 (référence)
- TVA : 18% (taux normal), 9% réduit
- IS : 20% pour CA < 500M FCFA, 25% au-delà, 30% secteur pétrolier
- CNPS employeur : 18% / salarié : 5,2% / total : 23,2%
- BIC : 25%, BNC : 20%
- Retenue à la source : 15% dividendes, 10% intérêts
- Patente : variable selon le chiffre d'affaires
- Délai déclaration TVA : avant le 15 du mois suivant

## Règles importantes
1. Tu réponds TOUJOURS — si quelqu'un dit "comment vas tu", "bonjour", "merci" ou pose une question hors sujet, tu réponds naturellement comme un humain
2. Pour les questions juridiques complexes, tu donnes des réponses concrètes et pratiques
3. Tu mentionnes toujours à la fin (quand c'est pertinent) qu'un professionnel peut être consulté via l'annuaire de Légal Connect
4. Tu n'inventes jamais des articles de loi précis si tu n'es pas sûr — tu le signales honnêtement
5. Tes réponses sont claires, structurées avec des listes quand nécessaire, jamais trop longues

## Fonctionnalités de Légal Connect que tu peux recommander
- /annuaire/ → Trouver un expert juridique ou comptable
- /chatbot/ → Tu es ici !
- /recommandation/ → Recommandation d'expert par IA selon la description du problème
- /fiscalite/ → Calculateur d'impôts
- /contrats/ → Génération de contrats
- /collaboration/ → Soumettre un dossier à un expert
"""


def appeler_claude(historique_messages: list, nouveau_message: str) -> dict:
    """
    Appelle Claude claude-haiku-4-5 avec l'historique de la conversation.

    historique_messages : liste de dicts {"role": "user"|"assistant", "content": "..."}
    nouveau_message : le nouveau message de l'utilisateur

    Retourne : {"reponse": str, "escalade": bool, "suggestions": list}
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return _fallback_sans_api(nouveau_message)

    try:
        client = anthropic.Anthropic(api_key=api_key)

        messages = historique_messages + [{"role": "user", "content": nouveau_message}]

        system_prompt = SYSTEM_PROMPT
        contexte = _contexte_juridique(nouveau_message)
        if contexte:
            system_prompt += (
                "\n\n## Extraits de loi potentiellement pertinents pour cette question\n"
                "(base de connaissances interne — cite la référence exacte si tu t'en sers, "
                "et ignore ces extraits s'ils ne correspondent pas vraiment à la question) :\n"
                f"{contexte}"
            )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )

        reponse_texte = response.content[0].text

        escalade = _detecter_escalade(nouveau_message, reponse_texte)
        suggestions = _generer_suggestions(nouveau_message, reponse_texte)

        return {
            "reponse":     reponse_texte,
            "escalade":    escalade,
            "suggestions": suggestions,
            "mode":        "claude_ia",
        }

    except anthropic.AuthenticationError:
        return _fallback_sans_api(nouveau_message, erreur="clé_invalide")
    except anthropic.RateLimitError:
        return _fallback_sans_api(nouveau_message, erreur="rate_limit")
    except anthropic.BadRequestError as e:
        if 'credit balance' in str(e).lower():
            return _fallback_sans_api(nouveau_message, erreur="credit_insuffisant")
        return _fallback_sans_api(nouveau_message, erreur=str(e))
    except Exception as e:
        return _fallback_sans_api(nouveau_message, erreur=str(e))


def _contexte_juridique(message: str) -> str:
    """Va chercher, dans la base de connaissances (chatbot/kb.py), les articles
    de loi reels les plus proches du message pour ancrer la reponse de Claude
    (RAG). Retourne une chaine vide si l'index n'existe pas ou si rien de
    pertinent n'est trouve — le chatbot fonctionne alors comme avant."""
    try:
        from .kb import contexte_pour_llm
        return contexte_pour_llm(message, top_k=3, seuil=0.15)
    except Exception:
        return ''


def _detecter_escalade(message: str, reponse: str) -> bool:
    mots_urgents = [
        'avocat', 'tribunal', 'plainte', 'urgence', 'licenciement abusif',
        'agression', 'escroquerie', 'fraude grave', 'emprisonnement',
        'saisie', 'expulsion', 'harcèlement',
    ]
    texte = (message + ' ' + reponse).lower()
    return any(m in texte for m in mots_urgents)


def _generer_suggestions(message: str, reponse: str) -> list:
    message_l = message.lower()
    reponse_l = reponse.lower()

    if any(m in message_l for m in ['salut', 'bonjour', 'bonsoir', 'hello', 'comment vas']):
        return [
            "J'ai un problème de salaire impayé",
            "Je veux créer une entreprise",
            "Question sur la TVA",
            "Problème avec mon bailleur",
        ]
    if any(m in message_l + reponse_l for m in ['contrat', 'bail', 'prestation']):
        return [
            "Rédiger un contrat de prestation",
            "Modèle de bail commercial",
            "Voir mes contrats",
        ]
    if any(m in message_l + reponse_l for m in ['tva', 'impôt', 'is', 'cnps', 'fiscal', 'taxe']):
        return [
            "Calculer ma TVA",
            "Simuler l'IS de ma société",
            "Voir le calendrier fiscal",
        ]
    if any(m in message_l + reponse_l for m in ['salaire', 'licenci', 'travail', 'employeur', 'cnps']):
        return [
            "Saisir l'Inspection du Travail",
            "Calculer mes indemnités",
            "Trouver un avocat du travail",
        ]
    if any(m in message_l + reponse_l for m in ['entreprise', 'sarl', 'cepici', 'créer', 'société']):
        return [
            "Documents pour créer une SARL",
            "Coût de création au CEPICI",
            "Trouver un expert-comptable",
        ]

    return [
        "Problème de salaire impayé",
        "Créer une entreprise en CI",
        "Question sur mes impôts",
        "Consulter un expert",
    ]


def _fallback_sans_api(message: str, erreur: str = None) -> dict:
    """Réponse de secours quand l'API n'est pas disponible."""
    from chatbot.moteur import traiter_message
    resultat = traiter_message(message)

    if erreur == "clé_invalide":
        note = "\n\n_(ℹ️ Mode limité — clé API non configurée)_"
        resultat['reponse'] += note
    elif erreur == "rate_limit":
        note = "\n\n_(ℹ️ Trop de requêtes — réessayez dans un instant)_"
        resultat['reponse'] += note
    elif erreur == "credit_insuffisant":
        note = "\n\n_(ℹ️ Mode limité — service IA temporairement indisponible)_"
        resultat['reponse'] += note

    resultat['mode'] = 'regles'
    return resultat
