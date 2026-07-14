"""
Construit l'index de recherche juridique du chatbot a partir des CSV
deposes dans chatbot/data/.

A executer chaque fois qu'un lot est ajoute ou modifie :
    python chatbot/construire_index.py
(depuis la racine du projet, avec le venv active)
"""
import os
import pickle
import sys
from collections import Counter
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legal_connect.settings')
django.setup()

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    print("ERREUR : scikit-learn non installe (pip install scikit-learn).")
    sys.exit(1)

from chatbot.kb import DATA_DIR, INDEX_DIR, MATRICE_PATH, META_PATH, VECTORIZER_PATH, charger_lots, nettoyer_texte


def construire():
    lignes = charger_lots(DATA_DIR)
    if not lignes:
        print(f"Aucune ligne trouvee dans {DATA_DIR}. Verifiez que les CSV y sont bien presents.")
        return

    # Article de reference (texte reel a citer) pour chaque source, avec repli sur
    # n'importe quelle ligne si aucune ligne 'article' n'existe pour cette source.
    article_par_source = {}
    for ligne in lignes:
        if ligne['type'] == 'article':
            article_par_source[ligne['source']] = ligne['text']
    for ligne in lignes:
        article_par_source.setdefault(ligne['source'], ligne['text'])

    textes_nettoyes = []
    meta = []
    for ligne in lignes:
        texte_nettoye = nettoyer_texte(ligne['text'])
        if not texte_nettoye:
            continue
        textes_nettoyes.append(texte_nettoye)
        meta.append({
            'source':       ligne['source'],
            'label':        ligne['label'],
            'article_text': article_par_source[ligne['source']],
        })

    print(f"Documents indexes : {len(textes_nettoyes)} (sur {len(lignes)} lignes lues)")
    print(f"Sources uniques    : {len(set(m['source'] for m in meta))}")
    print("Repartition par categorie :")
    for label, n in Counter(m['label'] for m in meta).most_common():
        print(f"  - {label:22s} {n}")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.7,
        sublinear_tf=True,
    )
    matrice = vectorizer.fit_transform(textes_nettoyes)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
    with open(MATRICE_PATH, 'wb') as f:
        pickle.dump(matrice, f)
    with open(META_PATH, 'wb') as f:
        pickle.dump(meta, f)

    print(f"\nIndex construit et enregistre dans {INDEX_DIR}")
    print(f"Vocabulaire : {len(vectorizer.vocabulary_)} termes")


if __name__ == '__main__':
    construire()
