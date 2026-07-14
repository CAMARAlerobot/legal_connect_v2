# moteur chatbot - voir contenu complet ci-dessous
BASE = {
    'salaire_impaye': {
        'mots_cles': ['salaire', 'paye', 'paie', 'employeur', 'remuneration', 'virement', 'bulletin', 'mensuel', 'impaye'],
        'reponse': (
            "En Cote d'Ivoire, le Code du Travail (art. 19) oblige l'employeur "
            "a verser le salaire aux dates convenues. En cas de non-paiement :\n\n"
            "1. Envoyez une mise en demeure par courrier recommande (delai 8 jours).\n"
            "2. Saisissez l'Inspection du Travail d'Abidjan (gratuit et rapide).\n"
            "3. En dernier recours, saisissez le Tribunal du Travail.\n\n"
            "Avez-vous un contrat ecrit et des fiches de paie ?"
        ),
        'intention': 'litige_salaire',
        'escalade': False,
        'suggestions': [
            "Oui, j'ai mon contrat et mes fiches de paie",
            "Non, je n'ai pas de contrat ecrit",
            "Parler a un avocat specialise",
        ],
    },
    'licenciement': {
        'mots_cles': ['licenci', 'renvoy', 'congedi', 'preavis', 'indemnit', 'chomage', 'rupture contrat'],
        'reponse': (
            "Un licenciement en Cote d'Ivoire doit respecter :\n\n"
            "- Convocation a entretien prealable (obligatoire)\n"
            "- Respect du preavis selon l'anciennete (1 a 3 mois)\n"
            "- Indemnite de licenciement si anciennete >= 1 an\n\n"
            "Si ces regles n'ont pas ete respectees, votre licenciement "
            "est potentiellement abusif et vous ouvre droit a des dommages.\n\n"
            "Depuis combien de temps etiez-vous dans cette entreprise ?"
        ),
        'intention': 'licenciement_abusif',
        'escalade': False,
        'suggestions': [
            "Moins d'1 an",
            "Entre 1 et 5 ans",
            "Plus de 5 ans",
            "Consulter un avocat du travail",
        ],
    },
    'caution': {
        'mots_cles': ['caution', 'bailleur', 'loyer', 'locataire', 'appartement', 'rembours', 'depot garantie', 'bail'],
        'reponse': (
            "En Cote d'Ivoire, la caution doit etre restituee dans un delai "
            "d'un mois apres la remise des cles.\n\n"
            "Si votre bailleur refuse :\n\n"
            "1. Envoyez une mise en demeure par lettre recommandee\n"
            "2. Saisissez la Commission de conciliation (gratuit)\n"
            "3. Portez l'affaire au Tribunal de Premiere Instance\n\n"
            "Avez-vous un etat des lieux de sortie signe ?"
        ),
        'intention': 'litige_locatif',
        'escalade': False,
        'suggestions': [
            "Oui, j'ai l'etat des lieux signe",
            "Non, pas d'etat des lieux",
            "Trouver un avocat immobilier",
        ],
    },
    'creation_entreprise': {
        'mots_cles': ['creer', 'sarl', 'societe', 'entreprise', 'cepici', 'immatriculation', 'statuts', 'capital', 'registre'],
        'reponse': (
            "Pour creer une entreprise en Cote d'Ivoire via le CEPICI :\n\n"
            "Documents necessaires :\n"
            "- Piece d'identite des associes\n"
            "- Statuts rediges par un notaire\n"
            "- Capital minimum : 100 000 FCFA pour une SARL\n"
            "- Attestation de domiciliation\n\n"
            "Cout estimatif : 50 000 a 200 000 FCFA\n"
            "Delai : 48h a 72h au guichet unique CEPICI\n\n"
            "Quel type de structure souhaitez-vous creer ?"
        ),
        'intention': 'creation_entreprise',
        'escalade': False,
        'suggestions': [
            'SARL (2 associes minimum)',
            'Entreprise individuelle',
            'SAS',
            "Conseils d'un expert-comptable",
        ],
    },
    'tva': {
        'mots_cles': ['tva', 'taxe valeur', 'declaration tva', 'dgi', 'impot', 'fiscal', 'redressement', 'patente'],
        'reponse': (
            "La TVA en Cote d'Ivoire est a 18% (taux normal).\n\n"
            "Regimes :\n"
            "- CA < 150M FCFA : Regime simplifie (declaration trimestrielle)\n"
            "- CA >= 150M FCFA : Regime reel normal (mensuel)\n\n"
            "Delai de declaration : avant le 15 du mois suivant.\n"
            "Penalite de retard : 10% + 1% par mois.\n\n"
            "Souhaitez-vous calculer votre TVA ou resoudre un litige avec la DGI ?"
        ),
        'intention': 'question_fiscale',
        'escalade': False,
        'suggestions': [
            'Calculer ma TVA',
            'Litige avec la DGI',
            "Conseil d'un fiscaliste",
        ],
    },
    'titre_foncier': {
        'mots_cles': ['titre foncier', 'terrain', 'parcelle', 'immobilier', 'propriete', 'voisin', 'expulsion', 'bail commercial'],
        'reponse': (
            "Les litiges fonciers en Cote d'Ivoire sont frequents.\n\n"
            "Probleme de titre foncier :\n"
            "-> Direction des Affaires Domaniales et Foncieres (DADF)\n\n"
            "Expulsion illegale :\n"
            "-> Ordonnance de refere (decision rapide du tribunal)\n\n"
            "Litige avec un voisin :\n"
            "-> Tentative de conciliation, puis Tribunal de Premiere Instance\n\n"
            "Quel est precisement votre probleme ?"
        ),
        'intention': 'litige_immobilier',
        'escalade': False,
        'suggestions': [
            'Probleme de titre foncier',
            'Expulsion illegale',
            'Litige avec un voisin',
            'Bail non renouvele',
        ],
    },
    'plainte': {
        'mots_cles': ['plainte', 'agress', 'vol', 'escroquerie', 'fraude', 'penal', 'tribunal', 'police', 'gendarmerie', 'victime'],
        'reponse': (
            "Pour deposer une plainte en Cote d'Ivoire :\n\n"
            "Option 1 - Commissariat ou Gendarmerie (gratuit)\n"
            "Presentez-vous avec votre piece d'identite et exposez les faits.\n"
            "Demandez un recepisse de depot de plainte.\n\n"
            "Option 2 - Plainte avec constitution de partie civile\n"
            "Via un avocat devant le Doyen des Juges d'Instruction.\n"
            "Recommande pour les infractions graves.\n\n"
            "Rassemblez toutes les preuves : temoins, photos, messages, documents.\n\n"
            "Voulez-vous etre mis en relation avec un avocat ?"
        ),
        'intention': 'droit_penal',
        'escalade': True,
        'suggestions': [
            'Oui, trouver un avocat penal',
            'Non merci, je gere seul',
        ],
    },
    'divorce': {
        'mots_cles': ['divorce', 'mariage', 'separation', 'conjoint', 'epoux', 'pension', 'garde enfant', 'succession', 'heritage'],
        'reponse': (
            "En matiere de droit de la famille en Cote d'Ivoire :\n\n"
            "Divorce :\n"
            "Peut etre prononce par consentement mutuel ou pour faute.\n"
            "Necessite obligatoirement le passage devant un juge.\n\n"
            "Garde des enfants :\n"
            "Le juge decide en fonction de l'interet superieur de l'enfant.\n\n"
            "Partage des biens :\n"
            "Depend du regime matrimonial choisi lors du mariage.\n\n"
            "Je vous recommande de consulter un avocat specialise. Souhaitez-vous etre mis en relation ?"
        ),
        'intention': 'droit_famille',
        'escalade': True,
        'suggestions': [
            'Trouver un avocat famille',
            'En savoir plus sur le divorce',
            'Question sur la garde des enfants',
        ],
    },
    'contrat_commercial': {
        'mots_cles': ['contrat', 'client', 'fournisseur', 'impaye', 'facture', 'livraison', 'commercial', 'cheque', 'recouvrement'],
        'reponse': (
            "Pour un litige commercial en Cote d'Ivoire :\n\n"
            "Si vous avez un contrat ecrit :\n"
            "-> Envoyez une mise en demeure (courrier recommande)\n"
            "-> Saisissez le Tribunal de Commerce d'Abidjan\n\n"
            "Pour recuperer une creance :\n"
            "-> Procedure d'injonction de payer (rapide et peu couteuse)\n"
            "-> Saisie des biens du debiteur via un huissier\n\n"
            "Delai de prescription : 5 ans pour les creances commerciales.\n\n"
            "Quel est le montant en jeu et avez-vous un contrat ecrit ?"
        ),
        'intention': 'litige_commercial',
        'escalade': False,
        'suggestions': [
            "Oui, j'ai un contrat ecrit",
            "Non, accord verbal uniquement",
            'Trouver un avocat commercial',
        ],
    },
}

REPONSE_DEFAUT = (
    "Je comprends votre situation. Pour vous donner les conseils "
    "les plus precis possible, pourriez-vous decrire votre probleme "
    "plus en detail ?\n\n"
    "Legale Connect met en relation des citoyens avec des avocats, "
    "fiscalistes, comptables et notaires disponibles en Cote d'Ivoire."
)

SUGGESTIONS_DEFAUT = [
    "Probleme de salaire impaye",
    "Litige commercial",
    "Question TVA / DGI",
    "Creer une entreprise",
    "Probleme de caution",
    "Porter plainte",
    "Divorce / famille",
]


def _chercher_reference_legale(message):
    """
    Cherche, dans la base de connaissances (chatbot/data + index TF-IDF),
    un article de loi reel proche du message. Seuil volontairement eleve
    (0.30) pour ne citer que des correspondances tres probables : mieux
    vaut ne rien citer qu'un article hors sujet.
    """
    try:
        from .kb import meilleur_article
    except Exception:
        return None
    return meilleur_article(message, seuil=0.30)


def _formater_reference(article):
    """
    Le texte de loi brut (souvent redige en francais juridique ancien) n'est
    pas comprehensible tel quel par un non-juriste. On le presente donc
    explicitement comme une source secondaire a faire lire a un professionnel,
    jamais comme une explication suffisante en elle-meme.
    """
    extrait = article['texte'].strip()
    if len(extrait) > 350:
        extrait = extrait[:350].rsplit(' ', 1)[0] + '...'
    return (
        f"\n\n📖 Pour info, voici le texte exact de la loi qui s'applique "
        f"({article['source']}) — il est ecrit en langage juridique, "
        f"un professionnel pourra vous en traduire le sens concret :\n« {extrait} »"
    )


def detecter_intention(message):
    message_lower = message.lower()
    meilleure_cle  = None
    meilleur_score = 0
    for cle, info in BASE.items():
        score = sum(1 for mot in info['mots_cles'] if mot in message_lower)
        if score > meilleur_score:
            meilleur_score = score
            meilleure_cle  = cle
    return meilleure_cle, meilleur_score


def traiter_message(message, historique=None):
    """
    Traite un message utilisateur et retourne une reponse.
    Retourne : reponse, intention, confiance, escalade, suggestions
    """
    if not message or len(message.strip()) < 2:
        return {
            'reponse':     "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            'intention':   'accueil',
            'confiance':   1.0,
            'escalade':    False,
            'suggestions': SUGGESTIONS_DEFAUT,
        }

    salutations = ['bonjour', 'bonsoir', 'salut', 'hello', 'bonne journee']
    if any(s in message.lower() for s in salutations) and len(message) < 30:
        return {
            'reponse': (
                "Bonjour ! Je suis l'assistant juridique de Legale Connect. "
                "Je suis disponible 24h/24 pour repondre a vos questions "
                "sur le droit ivoirien.\n\n"
                "Decrivez votre situation et je vous orienterai vers "
                "les meilleures demarches ou le bon professionnel."
            ),
            'intention':   'salutation',
            'confiance':   1.0,
            'escalade':    False,
            'suggestions': SUGGESTIONS_DEFAUT,
        }

    cle, score = detecter_intention(message)
    article = _chercher_reference_legale(message)

    if cle and score > 0:
        info = BASE[cle]
        reponse = info['reponse']
        if article:
            reponse += _formater_reference(article)
        return {
            'reponse':     reponse,
            'intention':   info['intention'],
            'confiance':   round(min(score / 3.0, 1.0), 2),
            'escalade':    info['escalade'],
            'suggestions': info.get('suggestions', SUGGESTIONS_DEFAUT),
        }

    if article:
        extrait = article['texte'].strip()
        if len(extrait) > 350:
            extrait = extrait[:350].rsplit(' ', 1)[0] + '...'
        return {
            'reponse': (
                f"Votre situation semble concernee par un texte precis "
                f"({article['source']}) :\n\n« {extrait} »\n\n"
                "C'est le texte exact de la loi, mais il est ecrit en langage "
                "juridique et peut avoir des nuances importantes selon votre cas. "
                "Le mieux est d'en parler a un professionnel qui pourra vous "
                "expliquer concretement ce que cela change pour vous. "
                "Souhaitez-vous etre mis en relation ?"
            ),
            'intention':   f"reference_{article['label']}",
            'confiance':   article['score'],
            'escalade':    False,
            'suggestions': SUGGESTIONS_DEFAUT,
        }

    return {
        'reponse':     REPONSE_DEFAUT,
        'intention':   'inconnu',
        'confiance':   0.2,
        'escalade':    False,
        'suggestions': SUGGESTIONS_DEFAUT,
    }