"""
Base de connaissances juridique du chatbot — Legal Connect
Recherche par similarite TF-IDF sur un corpus d'articles de loi reels
(Code civil, Code du travail, Code penal, OHADA, OAPI...).

Chaque "lot" de donnees est un CSV pose dans chatbot/data/, avec les
colonnes : text, label, source, type (type = "article" ou "query_variant").
Ajouter un nouveau lot = deposer un nouveau fichier dataset_*.csv dans
chatbot/data/ puis relancer construire_index.py. Aucune modification de
code n'est necessaire.
"""
import csv
import glob
import os
import pickle
import re
import unicodedata
from pathlib import Path

from django.conf import settings

DATA_DIR  = Path(settings.BASE_DIR) / 'chatbot' / 'data'
INDEX_DIR = Path(settings.BASE_DIR) / 'chatbot' / 'index'

VECTORIZER_PATH = INDEX_DIR / 'kb_vectorizer.pkl'
MATRICE_PATH    = INDEX_DIR / 'kb_matrice.pkl'
META_PATH       = INDEX_DIR / 'kb_meta.pkl'

STOPWORDS_FR = {
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "le", "la", "les",
    "un", "une", "des", "du", "de", "et", "en", "au", "aux", "ce", "se", "que", "qui",
    "dont", "est", "ont", "avec", "pour", "par", "sur", "dans", "ne", "pas", "mais",
    "me", "te", "lui", "comment", "sans", "depuis", "apres", "avant", "plus",
    "facon", "ete", "malgre", "quels", "quelles", "quoi", "tres", "aussi", "tout",
    "tous", "car", "donc", "cela", "cet", "cette", "ces", "meme", "lors", "peux",
    "expliquer", "prevoit", "civil", "dit", "loi", "ivoirien", "ivoirienne",
}


def nettoyer_texte(texte):
    """Minuscule, supprime les accents, ne garde que les lettres, filtre les mots courts/stopwords."""
    t = unicodedata.normalize('NFKD', texte.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r'[^a-z\s]', ' ', t)
    mots = [m for m in t.split() if len(m) > 2 and m not in STOPWORDS_FR]
    return ' '.join(mots)


def charger_lots(dossier=None):
    """Lit tous les CSV de chatbot/data/ et retourne la liste des lignes (dicts)."""
    dossier = dossier or DATA_DIR
    lignes = []
    for chemin in sorted(glob.glob(str(dossier / '*.csv'))):
        with open(chemin, encoding='utf-8', newline='') as f:
            for ligne in csv.DictReader(f):
                if ligne.get('text') and ligne.get('source'):
                    lignes.append(ligne)
    return lignes


_vectorizer = None
_matrice    = None
_meta       = None


def _charger_index():
    """Charge en memoire (une seule fois par processus) l'index pre-construit."""
    global _vectorizer, _matrice, _meta
    if _vectorizer is not None:
        return _vectorizer, _matrice, _meta
    if not (VECTORIZER_PATH.exists() and MATRICE_PATH.exists() and META_PATH.exists()):
        return None, None, None
    with open(VECTORIZER_PATH, 'rb') as f:
        _vectorizer = pickle.load(f)
    with open(MATRICE_PATH, 'rb') as f:
        _matrice = pickle.load(f)
    with open(META_PATH, 'rb') as f:
        _meta = pickle.load(f)
    return _vectorizer, _matrice, _meta


def rechercher(question, top_k=3, seuil=0.15, categorie=None):
    """
    Cherche les articles de loi les plus proches de `question`.
    Retourne une liste de dicts {texte, source, label, score}, triee par score decroissant,
    dedupliquee par source (un seul resultat par article, meme s'il matche via sa propre
    fiche 'article' et via une de ses reformulations 'query_variant').
    Liste vide si l'index n'est pas construit ou si rien ne depasse le seuil.

    Si `categorie` est fourni, ne cherche que parmi les articles de cette
    categorie (label) — utile pour eviter les faux amis lexicaux entre
    domaines du droit (ex. "caution" en droit civil des obligations vs.
    depot de garantie locatif).
    """
    vectorizer, matrice, meta = _charger_index()
    if vectorizer is None:
        return []

    texte_nettoye = nettoyer_texte(question)
    if not texte_nettoye:
        return []

    vecteur_question = vectorizer.transform([texte_nettoye])
    scores = (matrice @ vecteur_question.T).toarray().ravel()

    ordre = scores.argsort()[::-1]
    resultats = []
    sources_vues = set()
    for i in ordre:
        score = float(scores[i])
        if score < seuil:
            break
        info = meta[i]
        if categorie and info['label'] != categorie:
            continue
        if info['source'] in sources_vues:
            continue
        sources_vues.add(info['source'])
        resultats.append({
            'texte':  info['article_text'],
            'source': info['source'],
            'label':  info['label'],
            'score':  round(score, 3),
        })
        if len(resultats) >= top_k:
            break
    return resultats


def _categorie_probable(question, seuil_confiance=0.25):
    """
    Devine la categorie juridique de la question via le classifieur deja
    entraine pour la recommandation d'experts (ml_recommandation), qui
    partage exactement les memes 8 categories que les lots de donnees du
    chatbot. Retourne None si le module est indisponible ou si la confiance
    est trop faible (mieux vaut chercher sans filtre que de filtrer sur une
    mauvaise categorie).
    """
    try:
        from ml_recommandation.classifier import classifier_probleme
    except Exception:
        return None
    resultat = classifier_probleme(question)
    if resultat.get('score_confiance', 0) < seuil_confiance:
        return None
    return resultat.get('categorie')


def meilleur_article(question, seuil=0.20):
    """
    Raccourci : ne retourne que le meilleur resultat, ou None.

    Recherche strictement dans la categorie devinee, sans repli sur le
    corpus entier : ce resultat est cite tel quel a l'utilisateur (par
    moteur.py) sans qu'un LLM ne puisse en juger la pertinence, donc on
    prefere ne rien citer plutot que de citer un article d'une autre
    categorie qui matche par simple coincidence lexicale (ex. "caution" =
    cautionnement en droit des obligations, pas depot de garantie locatif).
    """
    categorie = _categorie_probable(question)
    resultats = rechercher(question, top_k=1, seuil=seuil, categorie=categorie)
    return resultats[0] if resultats else None


def contexte_pour_llm(question, top_k=3, seuil=0.12):
    """
    Formate les meilleurs articles trouves en un bloc de contexte texte,
    destine a etre injecte dans le prompt d'un LLM (RAG). Chaine vide si rien de pertinent.

    Ici, contrairement a meilleur_article, on se permet un repli sur le
    corpus entier si la categorie devinee ne donne rien : le LLM qui reçoit
    ce contexte a pour instruction de l'ignorer si non pertinent, le risque
    d'une fausse piste est donc moindre que pour une citation affichee telle quelle.
    """
    categorie = _categorie_probable(question)
    resultats = rechercher(question, top_k=top_k, seuil=seuil, categorie=categorie)
    if not resultats and categorie:
        resultats = rechercher(question, top_k=top_k, seuil=seuil)
    if not resultats:
        return ''
    blocs = []
    for r in resultats:
        extrait = r['texte'].strip()
        if len(extrait) > 600:
            extrait = extrait[:600].rsplit(' ', 1)[0] + '...'
        blocs.append(f"- ({r['source']}) {extrait}")
    return '\n'.join(blocs)
