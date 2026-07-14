"""
Moteur de classification et recommandation ML — Legal Connect
LinearSVC + TF-IDF (meilleur que Random Forest sur petit dataset NLP)
"""
import re
import pickle
from pathlib import Path
from django.conf import settings

MODEL_DIR = Path(settings.BASE_DIR) / 'ml_recommandation' / 'models'

CATEGORIES_VERS_SPECIALITE = {
    'droit_travail':       'droit_travail',
    'droit_commercial':    'droit_commercial',
    'droit_immobilier':    'droit_immobilier',
    'droit_fiscal':        'droit_fiscal',
    'creation_entreprise': 'comptabilite',
    'droit_famille':       'droit_civil',
    'droit_penal':         'droit_penal',
    'propriete_intel':     'droit_commercial',
}

CATEGORIES_LABELS = {
    'droit_travail':       'Droit du Travail',
    'droit_commercial':    'Droit Commercial',
    'droit_immobilier':    'Droit Immobilier',
    'droit_fiscal':        'Droit Fiscal',
    'creation_entreprise': "Creation d'Entreprise",
    'droit_famille':       'Droit de la Famille',
    'droit_penal':         'Droit Penal',
    'propriete_intel':     'Propriete Intellectuelle',
}

STOPWORDS_FR = {
    "mon","ma","mes","ton","ta","tes","son","sa","ses","le","la","les",
    "un","une","des","du","de","et","en","au","aux","ce","se","que","qui",
    "dont","est","ont","avec","pour","par","sur","dans","ne","pas","mais",
    "me","te","lui","comment","sans","depuis","apres","avant","plus",
    "facon","ete","malgre","quels","quelles","quoi","tres","aussi","tout",
    "tous","car","donc","cela","cet","cette","ces","meme","lors",
}

_vectorizer = None
_classifier = None


def _charger_modeles():
    global _vectorizer, _classifier
    if _vectorizer is not None and _classifier is not None:
        return _vectorizer, _classifier
    vect_path = MODEL_DIR / 'vectorizer.pkl'
    clf_path  = MODEL_DIR / 'classifier.pkl'
    if not vect_path.exists() or not clf_path.exists():
        return None, None
    with open(vect_path, 'rb') as f:
        _vectorizer = pickle.load(f)
    with open(clf_path, 'rb') as f:
        _classifier = pickle.load(f)
    return _vectorizer, _classifier


def nettoyer_texte(texte):
    # Doit rester strictement identique au nettoyage utilise a l'entrainement
    # (ml_recommandation/entrainer.py) : un ecart ici desynchronise le
    # vocabulaire appris et le vocabulaire vu en prediction.
    t = texte.lower()
    t = re.sub(r'[^a-z\s]', ' ', t)
    mots = [m for m in t.split() if len(m) > 2 and m not in STOPWORDS_FR]
    return ' '.join(mots)


def _classifier_mots_cles(texte):
    """Fallback si le modele n'est pas entraine."""
    texte_lower = texte.lower()
    regles = [
        (['salaire','licenci','employeur','travail','patron','cnps','conge','preavis','harcelement'],'droit_travail'),
        (['client','fournisseur','impaye','commerce','facture','contrat','livraison','concurrence'],'droit_commercial'),
        (['loyer','bailleur','caution','bail','immobilier','terrain','parcelle','expulsion','titre'],'droit_immobilier'),
        (['impot','taxe','dgi','tva','fiscal','declaration','redressement','penalite','patente'],'droit_fiscal'),
        (['sarl','societe','entreprise','cepici','creer','creation','statuts','immatriculation'],'creation_entreprise'),
        (['divorce','mariage','heritage','succession','famille','pension','enfant','garde','testament'],'droit_famille'),
        (['plainte','agress','vol','escroquerie','fraude','penal','tribunal','police'],'droit_penal'),
        (['brevet','marque','copyright','propriete','plagiat','oapi','logiciel','contrefacon'],'propriete_intel'),
    ]
    meilleure_cat, meilleur_score = None, 0
    for mots_cles, categorie in regles:
        score = sum(1 for mot in mots_cles if mot in texte_lower)
        if score > meilleur_score:
            meilleur_score, meilleure_cat = score, categorie
    if meilleure_cat and meilleur_score > 0:
        return {'categorie': meilleure_cat,
                'label': CATEGORIES_LABELS[meilleure_cat],
                'specialite': CATEGORIES_VERS_SPECIALITE[meilleure_cat],
                'score_confiance': round(min(meilleur_score / 4.0, 0.85), 3),
                'mode': 'mots_cles'}
    return {'categorie': 'droit_commercial',
            'label': CATEGORIES_LABELS['droit_commercial'],
            'specialite': CATEGORIES_VERS_SPECIALITE['droit_commercial'],
            'score_confiance': 0.35, 'mode': 'defaut'}


def classifier_probleme(texte):
    """
    Classifie un probleme juridique en texte libre.
    Retourne : { categorie, label, specialite, score_confiance, mode }
    """
    if not texte or len(texte.strip()) < 5:
        return _classifier_mots_cles(texte)

    vectorizer, clf = _charger_modeles()
    if vectorizer is None or clf is None:
        return _classifier_mots_cles(texte)

    texte_propre = nettoyer_texte(texte)
    if not texte_propre:
        return _classifier_mots_cles(texte)

    vecteur    = vectorizer.transform([texte_propre])
    prediction = clf.predict(vecteur)[0]

    # LinearSVC n'a pas predict_proba — on utilise decision_function
    try:
        distances  = clf.decision_function(vecteur)[0]
        # Softmax approximation pour avoir un score entre 0 et 1
        import numpy as np
        exp_d = [2.718 ** float(d) for d in distances]
        total = sum(exp_d)
        proba_max = max(exp_d) / total if total > 0 else 0.5
        confiance = round(min(float(proba_max), 0.99), 3)
    except Exception:
        confiance = 0.80

    return {
        'categorie':       prediction,
        'label':           CATEGORIES_LABELS.get(prediction, prediction),
        'specialite':      CATEGORIES_VERS_SPECIALITE.get(prediction, 'droit_commercial'),
        'score_confiance': confiance,
        'mode':            'ml',
    }


def recommander_experts(texte, ville='', budget_max=None, limit=3):
    """Pipeline complet : classifier + filtrer + scorer + top N."""
    from django.contrib.auth.models import User
    from django.db.models import Avg, Count

    classification = classifier_probleme(texte)
    specialite     = classification['specialite']

    experts_qs = User.objects.filter(
        profil__role='expert',
        profil__specialite=specialite,
        is_active=True,
    ).select_related('profil')

    if ville and ville.strip():
        experts_qs = experts_qs.filter(profil__adresse__icontains=ville.strip())

    resultats = []
    for expert in experts_qs:
        try:
            from annuaire.models import AvisExpert
            stats = AvisExpert.objects.filter(expert=expert, valide=True).aggregate(
                note_moy=Avg('note'), nb_avis=Count('id'))
            note_moy = float(stats['note_moy'] or 0)
            nb_avis  = int(stats['nb_avis'] or 0)
        except Exception:
            note_moy, nb_avis = 0.0, 0

        try:
            from collaboration.models import Dossier
            nb_dossiers = Dossier.objects.filter(expert=expert, statut='valide').count()
        except Exception:
            nb_dossiers = 0

        score = round(
            0.50 * (note_moy / 5.0) +
            0.30 * min(nb_dossiers / 20.0, 1.0) +
            0.20 * min(nb_avis / 10.0, 1.0), 3
        )
        resultats.append({
            'expert': expert, 'profil': expert.profil,
            'note_moy': round(note_moy, 1),
            'nb_avis': nb_avis, 'nb_dossiers': nb_dossiers, 'score': score,
        })

    resultats.sort(key=lambda x: (x['score'], x['nb_dossiers']), reverse=True)
    return {'classification': classification, 'experts': resultats[:limit],
            'total_experts': len(resultats)}


def modele_disponible():
    return (MODEL_DIR / 'vectorizer.pkl').exists() and (MODEL_DIR / 'classifier.pkl').exists()