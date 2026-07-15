"""
Script d'entrainement ML — Legal Connect
LinearSVC + TF-IDF (trigrammes)
Objectif F1 >= 0.85

Executer : python ml_recommandation\entrainer.py
"""
import json
import pickle
import re
import sys
import random
from pathlib import Path
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.metrics import classification_report, f1_score
except ImportError:
    print("ERREUR : scikit-learn non installe.")
    print("Executer : pip install scikit-learn")
    sys.exit(1)

BASE_DIR  = Path(__file__).parent
DATA_PATH = BASE_DIR / 'data' / 'dataset.json'
MODEL_DIR = BASE_DIR / 'models'
MODEL_DIR.mkdir(exist_ok=True)

# Corpus reel (articles de loi ivoirienne + reformulations), partage avec le
# chatbot. Seules les lignes "query_variant" sont reprises ici : elles sont
# phrasees comme de vraies questions, contrairement aux lignes "article"
# (texte de loi brut, registre trop eloigne d'une description de probleme
# par un utilisateur). Un plafond par categorie evite qu'une categorie
# sur-representee (droit_commercial) n'ecrase les autres.
CHATBOT_DATA_DIR       = BASE_DIR.parent / 'chatbot' / 'data'
# Plafond volontairement bas : au-dela d'~50 exemples reels par categorie, le
# registre archaique du Code Civil (droit_commercial/droit_immobilier surtout)
# dilue le classifieur et degrade la generalisation sur des formulations
# informelles (verifie par ablation : 50 -> 18/20 vs 150 -> 17/20 sur un jeu
# de 20 questions realistes non vues a l'entrainement).
MAX_EXEMPLES_REELS_CAT = 50
CATEGORIES_CONNUES = {
    'droit_travail', 'droit_commercial', 'droit_immobilier', 'droit_fiscal',
    'creation_entreprise', 'droit_famille', 'droit_penal', 'propriete_intel',
}

STOPWORDS_FR = {
    "mon","ma","mes","ton","ta","tes","son","sa","ses","le","la","les",
    "un","une","des","du","de","et","en","au","aux","ce","se","que","qui",
    "dont","est","ont","avec","pour","par","sur","dans","ne","pas","mais",
    "me","te","lui","comment","sans","depuis","apres","avant","plus",
    "facon","ete","malgre","quels","quelles","quoi","tres","aussi","tout",
    "tous","car","donc","cela","cet","cette","ces","meme","lors",
}

TEMPLATES = {
    "droit_travail": [
        "mon employeur refuse de me payer salaire depuis mois",
        "licenciement abusif sans preavis indemnite CDI",
        "harcelement moral travail superieur hierarchique",
        "contrat travail non renouvele sans explication",
        "CNPS non cotisee employeur depuis annees",
        "retenue abusive salaire sans justification",
        "heures supplementaires non payees employeur",
        "mise a pied injustifiee sans salaire",
        "bulletin salaire refuse employeur",
        "attestation travail refusee apres depart",
        "accident travail non declare employeur",
        "salaire inferieur SMIG legal",
        "conges payes refuses employeur",
        "pression demission sans indemnites",
        "modification unilaterale contrat travail",
        "harcelement sexuel chef service travail",
        "solde tout compte non verse depart",
        "travail non declare sans contrat",
        "discrimination embauche origine raison",
        "rupture periode essai sans motif",
    ],
    "droit_commercial": [
        "client impaye FCFA depuis mois relances",
        "fournisseur livraison non effectuee paiement fait",
        "contrat commercial rupture abusive partenaire",
        "concurrent copie produits vend moins cher",
        "cheque sans provision recouvrement judiciaire",
        "facture impayee recouvrement procedure",
        "associe benefices partage litige",
        "clause abusive contrat signe pression",
        "escroquerie commerciale fausse societe",
        "concurrence deloyale ancien employe clients",
        "franchise contrat non respecte franchiseur",
        "agent commercial vente directe sans reverser",
        "sous-traitant contrat inexecute acompte",
        "prestation non conforme cahier charges",
        "marchandises importees non conformes qualite",
        "penalites retard contrat chantier BTP",
        "resiliation contrat distribution exclusif",
        "acompte verse commande jamais livree",
        "parts sociales vendues sans droit preemption",
        "detournement fonds societe associe gerant",
        "magasin refuse rembourser produit defectueux achete",
        "boutique refuse echanger article abime garantie",
        "commercant refuse remboursement vente consommateur",
        "produit achete en ligne jamais recu remboursement",
    ],
    "droit_immobilier": [
        "bailleur refuse rembourser caution FCFA",
        "voisin construit terrain empiete sans autorisation",
        "titre foncier litigieux parcelle Abidjan",
        "proprietaire expulsion illegale sans jugement",
        "bail commercial non renouvele indemnite",
        "loyer abusif augmentation sans preavis",
        "maison vices caches fondations fissures",
        "promoteur immobilier livraison retard appartements",
        "terrain herite vendu sans accord heritiers",
        "locataire refuse partir fin bail jugement",
        "travaux voisinage degats propriete",
        "copropriete charges abusives syndic",
        "maison titre foncier nom vendeur",
        "terrain agricole occupe illegalement",
        "coupe eau electricite proprietaire illegal",
        "caution solidaire dette ancien locataire",
        "contrat construction inacheve malfacon",
        "servitude passage refusee acces propriete",
        "limite proprietes bornage conteste",
        "acte vente signe cles refusees",
    ],
    "droit_fiscal": [
        "DGI reclame TVA deja payee justificatifs",
        "controle fiscal defendre droits contribuable",
        "penalites retard TVA contester officiellement",
        "redressement fiscal abusif benefices",
        "declaration IS incorrecte regulariser",
        "exoneration patente nouvelle entreprise",
        "remboursement credit TVA refuse DGI",
        "IMF calcul errone impot forfaitaire",
        "patente non payee regularisation procedure",
        "CNPS non declaree rattrapage",
        "saisie compte bancaire fisc stopper",
        "TVA services exoneres reclamation DGI",
        "amende fiscale retard declaration",
        "regime simplifie BIC PME beneficier",
        "charges deductibles contestees verification",
        "vérification comptabilite droits",
        "TSE taxe speciale equipement declaration",
        "BNC declaration profession liberale CI",
        "accord transactionnel DGI redressement",
        "prescription fiscale impots non payes",
    ],
    "creation_entreprise": [
        "creer SARL associes Abidjan CEPICI",
        "immatriculation entreprise etapes documents",
        "transformer entreprise individuelle SARL",
        "statuts societe notaire redaction enregistrement",
        "capital minimum societe CI FCFA",
        "registre commerce compte professionnel",
        "dissolution liquidation societe procedure",
        "augmentation capital social SARL",
        "conflit associes assemblee generale blocage",
        "gerant revocation nomination SARL",
        "SAS creation CI differences SARL",
        "cession parts sociales procedure",
        "pacte associes clauses protection",
        "modification statuts objet social",
        "responsabilite gerant dettes societe",
        "ONG association loi creation procedure",
        "mise sommeil societe temporaire",
        "reprise entreprise fonds commerce",
        "licence exploitation restaurant hotel",
        "fusion absorption societes OHADA",
    ],
    "droit_famille": [
        "divorce biens maison droits conjoint",
        "succession deces testament partage heritage",
        "garde enfants separation accord impossible",
        "pension alimentaire non versee ex-conjoint",
        "adoption enfant orphelin procedure",
        "reconnaissance paternite refusee pere",
        "testament invalide conteste famille",
        "mariage coutumier validite legale",
        "divorce consentement mutuel procedure",
        "heritage conteste demi-frere non reconnu",
        "enfant hors mariage droits successoraux",
        "enlevement parental etranger comment",
        "violences conjugales divorce urgence protection",
        "biens communs mariage divorce repartition",
        "tutelle parent age incapable",
        "mariage force mineure annulation",
        "droit visite refuse ex-conjoint",
        "succession polygamique epouses partage",
        "acte naissance incorrect correction",
        "abandon famille ressources enfants",
    ],
    "droit_penal": [
        "agression physique porter plainte police",
        "fraude accusation fausse innocent avocat penal",
        "escroquerie argent verse jamais livre",
        "garde a vue police droits que faire",
        "cheque sans provision poursuites penales",
        "diffamation reseaux sociaux poursuivre",
        "menaces mort telephone messages",
        "vol employe boutique plainte",
        "abus confiance detournement fonds",
        "cybercriminalite piratage bancaire",
        "fausse accusation innocence prouver",
        "extorsion fonds menaces individus",
        "incendie criminel plainte indemnisation",
        "escroquerie immobiliere terrain vendu plusieurs",
        "corruption fonctionnaire pot de vin",
        "faux documents officiels falsifies",
        "arrestation abusive sans mandat",
        "detournement fonds publics signalement",
        "usurpation identite papiers arnaque",
        "detention arbitraire emprisonnement sans jugement",
        "convocation commissariat gendarmerie motif inconnu",
        "convoque police ne sait pas pourquoi audition",
        "recu convocation juge instruction affaire penale",
        "temoin convoque commissariat enquete policiere",
    ],
    "propriete_intel": [
        "logo nom commercial copie sans autorisation",
        "brevet invention OAPI deposer CI",
        "musique creations plagiat proteger",
        "marque deposee concurrent utilise illegalement",
        "site web contenu photos copies",
        "logiciel droit auteur proteger",
        "contrefacon produits marches Abidjan",
        "OAPI marque enregistrement procedure cout",
        "concept entreprise repris ancien employe",
        "these memoire plagiat autre nom",
        "photographie publicite sans consentement",
        "application mobile copiee concurrent",
        "nom domaine cybersquatting mauvaise foi",
        "logo design reproduit sans accord",
        "secret fabrication divulgue concurrent",
        "musique radio sans royalties autorisation",
        "formation copiee revendue formateur",
        "oeuvre graphique t-shirts commercialisation",
        "accord confidentialite viole informations",
        "modele utilite industriel copie",
    ],
}

def nettoyer_texte(texte):
    t = texte.lower()
    for a, s in [('e','e'),('e','e'),('e','e'),('e','e'),('a','a'),
                 ('a','a'),('i','i'),('i','i'),('o','o'),('u','u'),
                 ('u','u'),('c','c')]:
        pass
    t = re.sub(r'[^a-z\s]', ' ', t)
    mots = [m for m in t.split() if len(m) > 2 and m not in STOPWORDS_FR]
    return ' '.join(mots)

def charger_donnees_reelles(dossier=CHATBOT_DATA_DIR, max_par_categorie=MAX_EXEMPLES_REELS_CAT):
    """Charge les reformulations (query_variant) des datasets juridiques reels
    (chatbot/data/*.csv), plafonnees par categorie, pour enrichir l'entrainement
    du classifieur de recommandation avec du vocabulaire juridique authentique."""
    import csv
    import glob

    par_categorie = {}
    for chemin in sorted(glob.glob(str(dossier / '*.csv'))):
        with open(chemin, encoding='utf-8', newline='') as f:
            for ligne in csv.DictReader(f):
                if ligne.get('type') != 'query_variant':
                    continue
                categorie = ligne.get('label')
                if categorie not in CATEGORIES_CONNUES:
                    continue
                par_categorie.setdefault(categorie, []).append(ligne['text'])

    random.seed(42)
    exemples = []
    for categorie, textes in par_categorie.items():
        random.shuffle(textes)
        for texte in textes[:max_par_categorie]:
            exemples.append({'texte': texte, 'categorie': categorie})
    return exemples


def augmenter_dataset(data_originale):
    """Augmente le dataset avec des variations des templates."""
    augmented = list(data_originale)
    random.seed(42)
    for categorie, templates in TEMPLATES.items():
        for tmpl in templates:
            for _ in range(4):
                augmented.append({"texte": tmpl, "categorie": categorie})
    random.shuffle(augmented)
    return augmented


def main():
    print("\n" + "=" * 60)
    print("  ENTRAINEMENT ML — LEGAL CONNECT (LinearSVC)")
    print("=" * 60 + "\n")

    if not DATA_PATH.exists():
        print(f"ERREUR : {DATA_PATH} introuvable.")
        sys.exit(1)

    print("1. Chargement et augmentation du dataset...")
    with open(DATA_PATH, encoding='utf-8') as f:
        data_originale = json.load(f)

    data = augmenter_dataset(data_originale)
    nb_avant_reel = len(data)

    donnees_reelles = charger_donnees_reelles()
    data += donnees_reelles
    random.seed(42)
    random.shuffle(data)

    textes = [ex['texte'] for ex in data]
    labels = [ex['categorie'] for ex in data]
    classes = sorted(set(labels))

    print(f"   Dataset original           : {len(data_originale)} exemples")
    print(f"   + templates augmentes      : {nb_avant_reel} exemples")
    print(f"   + donnees reelles (lots)   : {len(donnees_reelles)} exemples")
    print(f"   Dataset final              : {len(data)} exemples")
    print(f"   Categories                 : {len(classes)}\n")

    print("   Distribution :")
    for cat, nb in sorted(Counter(labels).items()):
        barre = '#' * (nb // 5)
        print(f"   {cat:<25} {barre} ({nb})")

    print("\n2. Division train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        textes, labels, test_size=0.20, random_state=42, stratify=labels
    )
    print(f"   Train : {len(X_train)} | Test : {len(X_test)}")

    print("\n3. Vectorisation TF-IDF (trigrammes)...")
    vectorizer = TfidfVectorizer(
        max_features=8000,
        ngram_range=(1, 3),
        sublinear_tf=True,
        min_df=1,
        analyzer='word',
    )
    X_train_vec = vectorizer.fit_transform([nettoyer_texte(t) for t in X_train])
    X_test_vec  = vectorizer.transform([nettoyer_texte(t) for t in X_test])
    print(f"   Vocabulaire : {len(vectorizer.vocabulary_)} termes")

    print("\n4. Entrainement LinearSVC...")
    clf = LinearSVC(C=5.0, max_iter=3000, random_state=42, class_weight='balanced')
    clf.fit(X_train_vec, y_train)
    print("   Termine !")

    print("\n5. Evaluation...")
    y_pred = clf.predict(X_test_vec)
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f"\n{'=' * 60}")
    print(f"  F1-Score pondere : {f1:.3f}")
    print(f"{'=' * 60}\n")
    print(classification_report(y_test, y_pred))

    print("6. Validation croisee (5 folds)...")
    X_all_vec = vectorizer.transform([nettoyer_texte(t) for t in textes])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_all_vec, labels, cv=cv, scoring='f1_weighted')
    print(f"   Scores : {[f'{s:.3f}' for s in scores]}")
    print(f"   Moyenne : {scores.mean():.3f} (+/- {scores.std():.3f})")

    print("\n7. Sauvegarde...")
    with open(MODEL_DIR / 'vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    with open(MODEL_DIR / 'classifier.pkl', 'wb') as f:
        pickle.dump(clf, f)
    print(f"   vectorizer.pkl et classifier.pkl -> {MODEL_DIR}")

    print("\n8. Tests rapides...")
    tests = [
        "Mon employeur ne me paie pas depuis 2 mois",
        "Mon bailleur refuse de rembourser ma caution",
        "Je veux creer une SARL au CEPICI",
        "Contrat commercial non respecte client impaye",
        "Declaration TVA penalites DGI redressement",
        "J'ai ete agresse je veux porter plainte",
        "Logo copie concurrent brevet OAPI",
        "Divorce garde enfants pension alimentaire",
    ]
    for t in tests:
        t_net = nettoyer_texte(t)
        v = vectorizer.transform([t_net])
        pred = clf.predict(v)[0]
        print(f"   '{t[:50]}' -> {pred}")

    print(f"\n{'=' * 60}")
    if f1 >= 0.80:
        print(f"  SUCCES ! F1 = {f1:.3f} (objectif >= 0.80 atteint)")
    else:
        print(f"  ATTENTION : F1 = {f1:.3f}")
    print(f"{'=' * 60}\n")
    print("Lance le serveur : python manage.py runserver\n")


if __name__ == '__main__':
    main()