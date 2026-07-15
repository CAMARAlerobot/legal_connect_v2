# ⚖️ Légal Connect

> **Plateforme Numérique d'Assistance Juridique et Fiscale pour le Secteur Informel Francophone Africain**

![Django](https://img.shields.io/badge/Django-5.2.1-green?logo=django)
![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-98%25%20Complete-brightgreen)

---

## 📖 Présentation

**Légal Connect** est une plateforme web développée dans le cadre du **Master 1 MIAGE** à l'**Université Nangui Abrogoua (Côte d'Ivoire)** sous la direction du **Dr. ZEZE**.

Elle répond à un besoin concret : les commerçants et prestataires du secteur informel africain n'ont pas accès aux outils juridiques et fiscaux adaptés à leur réalité. Légal Connect leur offre une solution numérique simple, gratuite et en français pour :

- Générer des **contrats professionnels** en quelques minutes
- Calculer leurs **impôts** selon les taux officiels de Côte d'Ivoire
- Collaborer avec des **experts juridiques** qualifiés
- Gérer leurs **documents** en toute sécurité
- Rester informés des **échéances fiscales** importantes

---

## ✨ Fonctionnalités

| Module | Description | Statut |
|--------|-------------|--------|
| 🔐 Authentification | 6 rôles : commerçant, expert, institution, admin, auditeur, prestataire | ✅ |
| 📄 Contrats | 7 types, génération assistée par IA, export PDF | ✅ |
| 📁 Documents | Upload, classement par catégorie, partage sécurisé | ✅ |
| 🧮 Fiscalité | Calculateur TVA/IS/CNPS/BNC/BIC, calendrier, export PDF | ✅ |
| 🤝 Collaboration | Dossiers expert-client, messagerie, validation | ✅ |
| 🔔 Notifications | Alertes automatiques, emails HTML, cloche AJAX | ✅ |
| 👥 Annuaire | Annuaire experts par spécialité, taux de validation | ✅ |
| 🌐 Landing Page | Page d'accueil publique professionnelle | ✅ |
| 📊 Dashboard | Graphiques Chart.js, KPIs, statistiques | ✅ |
| 📑 Pagination | Pagination sur toutes les listes | ✅ |
| 🤖 Chatbot juridique | IA générative (Claude) + RAG sur 9392 lignes d'articles de loi réels | ✅ |
| 🎯 Recommandation d'experts | Classifieur ML (TF-IDF + LinearSVC), F1 = 0.928 | ✅ |
| 💳 Abonnements | Plans par rôle, paiement Mobile Money simulé (CinetPay), espace admin revenus | ✅ |

---

## 🤖 Chatbot juridique — IA générative et RAG

Le chatbot combine deux mécanismes complémentaires plutôt qu'une seule approche :

1. **Génération de réponses** via l'API Claude (Anthropic), guidée par un prompt système qui définit son rôle et ses règles de comportement (`chatbot/moteur_ia.py`).
2. **RAG (Retrieval-Augmented Generation)** : avant chaque réponse, le système cherche par similarité textuelle (TF-IDF + similarité cosinus) les articles de loi les plus pertinents parmi un corpus de **9 512 lignes** (Code Civil, Code du Travail, Code Pénal, OHADA, Accord de Bangui/OAPI, Code de la Construction et de l'Habitat, procédure CEPICI, faits fiscaux TVA/CGI — 3 261 articles/sources uniques), puis les injecte dans le contexte fourni à Claude. Le système classe d'abord la question par domaine juridique (`ml_recommandation`) pour restreindre la recherche à la bonne catégorie et éviter les faux positifs lexicaux entre domaines (ex. « caution » = cautionnement en droit des obligations, vs. dépôt de garantie locatif).

**Mode de repli sans IA** (`chatbot/moteur.py`) : si l'API est indisponible (pas de clé, crédit épuisé, panne réseau), le chatbot bascule automatiquement sur un moteur à règles + la même recherche RAG, sans transmission de données à un tiers — le service continue de fonctionner en mode dégradé plutôt que de tomber en panne.

**Nouveaux lots de données (couvrant les lacunes précédemment documentées)** :
- **Bail à usage d'habitation** — 40 articles **verbatim** du Code de la Construction et de l'Habitat (Loi n°2019-576 du 26 juin 2019), articles 408 à 454, récupérés et vérifiés (dépôt de garantie, révision du loyer, réparations, résiliation, expulsion, droit de préemption). L'ambiguïté « caution » (dépôt de garantie locatif vs. cautionnement du Code Civil) est désormais résolue : une requête comme *« le propriétaire refuse de me rembourser ma caution »* pointe correctement vers l'article 416 (score de similarité 0,88 contre 0,21 avant correction) plutôt que vers un article de cautionnement civil sans rapport.
- **Création de SARL** — procédure réelle du Guichet Unique du CEPICI (5 étapes, 13 documents, frais de 42 000 FCFA, RCCM sous 7 jours ouvrables, IDU sous 14 jours), sourcée sur le portail officiel eRegulations Côte d'Ivoire.
- **TVA / Code Général des Impôts** — ⚠️ *limite assumée* : malgré une dizaine de tentatives sur différentes sources (droit-afrique.com, dgi.gouv.ci, cgici.com, etc.), le texte exact des articles du CGI n'a pas pu être vérifié (accès refusé, sources injoignables ou payantes). Ce lot ne contient donc que des **faits fiscaux confirmés** (taux de 18 % normal / 9 % réduit, seuil d'assujettissement de 50 000 000 FCFA, régimes RRN/RSI, structure des sections du Livre II Titre I), explicitement annotés comme non-verbatim dans leur source — plutôt que d'inventer une citation d'article qui semblerait authentique. Ce choix illustre le principe retenu pour tout le projet : ne jamais fabriquer de texte juridique invérifiable.

**Limites connues, documentées plutôt que masquées** : le Code Civil (droit napoléonien traduit) domine numériquement le corpus et peut faire remonter des articles hors-sujet par polysémie sur d'autres notions ; le lot TVA/CGI reste un résumé de faits et non un texte de loi citable.

Pipeline technique : `chatbot/data/*.csv` (lots de données) → `chatbot/construire_index.py` (indexation TF-IDF) → `chatbot/index/*.pkl` → `chatbot/kb.py` (recherche).

## 🎯 Système de recommandation d'experts — Machine Learning

Classifieur supervisé (TF-IDF + LinearSVC, `ml_recommandation/`) qui devine le domaine juridique d'un problème décrit en langage libre, pour orienter vers le bon type d'expert.

**Méthodologie de validation** (au-delà du score sur split aléatoire, volontairement plus rigoureuse) :
- F1-score pondéré (split 80/20) : **0.959** — validation croisée 5-fold : **0.930** (±0.012)
- Un **jeu de 20 questions réalistes indépendantes**, rédigées spécifiquement pour tester la généralisation (et non issues des données d'entraînement) : **20/20** de bonnes catégories devinées (contre 18-19/20 avant l'ajout des lots bail/SARL/TVA — l'enrichissement en exemples réels sur `droit_immobilier`, `creation_entreprise` et `droit_fiscal` a directement amélioré la généralisation sur ces catégories)
- Un **bug de désynchronisation** entre le nettoyage de texte à l'entraînement et à la prédiction a été détecté puis corrigé au cours de cette validation — sans le jeu de test indépendant, il serait passé inaperçu malgré un bon score apparent

**Choix méthodologique documenté** : seules les reformulations en question (« query_variant ») des lots de données du chatbot sont réutilisées pour l'entraînement, pas le texte de loi brut — trop éloigné du registre d'un utilisateur décrivant son problème. Un plafond de 50 exemples réels par catégorie a été retenu après ablation (150/catégorie diluait et dégradait la généralisation).

---

## 🛠️ Stack Technique

```
Backend    : Django 5.2.1 (MVT) + Python 3.14
Base de données : MySQL 8.0 (prod) / SQLite (dev)
Frontend   : Bootstrap 5.3 + Bootstrap Icons + Chart.js
PDF        : ReportLab (export contrats et déclarations)
Email      : Django EmailMultiAlternatives + templates HTML
Serveur    : Nginx + Gunicorn (production)
```

---

## 🚀 Installation rapide

### Prérequis
- Python 3.10+
- pip
- MySQL 8.0 (optionnel, SQLite par défaut)

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/legal-connect.git
cd legal-connect
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données
```bash
# Copier le fichier de configuration
cp legal_connect/settings_example.py legal_connect/settings_local.py

# Éditer settings_local.py avec vos paramètres BDD
```

### 5. Appliquer les migrations
```bash
python manage.py migrate
```

### 6. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 7. Générer les données de test (optionnel)
```bash
python populate_db.py
```

### 8. Lancer le serveur
```bash
python manage.py runserver
```

Accédez à `http://127.0.0.1:8000` 🎉

---

## 📁 Structure du projet

```
legal_connect_v2/
├── accounts/           # Authentification, profils, dashboard
├── contrats/           # Génération de contrats
├── documents/          # Gestion documentaire
├── fiscalite/          # Calcul fiscal + calendrier
├── collaboration/      # Dossiers expert-client
├── notifications/      # Système de notifications
├── annuaire/           # Annuaire des experts
├── legal_connect/      # Configuration Django
├── templates/          # Templates HTML globaux
├── static/             # CSS, JS, images
├── media/              # Fichiers uploadés
├── populate_db.py      # Script de données de test
└── requirements.txt    # Dépendances Python
```

---

## 🧮 Taux Fiscaux Implémentés (CI 2025-2026)

| Impôt | Taux | Base |
|-------|------|------|
| TVA | 18% flat | Chiffre d'affaires HT |
| IS | 20-25-30% progressif | Bénéfice net (min 500K FCFA) |
| CNPS | 23.2% total | Salaire × nb employés |
| BNC | 20% flat | Bénéfice net |
| BIC | 25% flat | Bénéfice net |

---

## 👥 Comptes de test

Après `python populate_db.py` :

| Compte | Mot de passe | Rôle |
|--------|-------------|------|
| `admin` | `admin123` | Administrateur |
| `expert1` | `expert123` | Expert (droit commercial) |
| `expert2` | `expert123` | Expert (comptabilité) |
| `client1` | `client123` | Commerçant |
| `client2` | `client123` | Prestataire |

---

## 📸 Captures d'écran

| Landing Page | Dashboard | Calculateur Fiscal |
|---|---|---|
| Page d'accueil publique avec hero, features et témoignages | KPIs + graphiques Chart.js + actions rapides | Calcul TVA/IS/CNPS avec export PDF |

---

## 🔒 Confidentialité des données et dépendance à un service tiers

L'intégration de l'intelligence artificielle générative dans le chatbot juridique repose sur l'API d'Anthropic (Claude), un service hébergé hors du territoire ivoirien. Ce choix architectural, motivé par la rapidité de mise en œuvre et la qualité des réponses en langue française, soulève trois questions qu'il convient de traiter explicitement plutôt que de les ignorer.

**Souveraineté des données.** Chaque message soumis par un utilisateur au chatbot — qui peut contenir des informations sensibles sur sa situation personnelle, professionnelle ou financière — est transmis aux serveurs d'Anthropic pour traitement. Cette transmission place les données hors du cadre juridique ivoirien pendant leur traitement, ce qui constitue une limite pour une plateforme destinée à des citoyens et entreprises de Côte d'Ivoire. Une vérification de la politique de traitement et de rétention des données d'Anthropic (disponible sur `anthropic.com/legal`) est recommandée avant tout déploiement en production, ainsi qu'une information claire des utilisateurs sur ce point (mention dans les conditions d'utilisation).

**Résilience architecturale.** Pour limiter cette dépendance, le système a été conçu avec un mode de repli (`chatbot/moteur.py`) qui fonctionne entièrement en local, sans transmission de données à un tiers : il s'appuie sur une base de connaissances juridique constituée d'articles de loi réels (9 392 lignes) interrogée par similarité textuelle (TF-IDF), sans appel à un service externe. Ce mode s'active automatiquement en cas d'indisponibilité de l'API (absence de clé, crédit épuisé, panne réseau), ce qui garantit une continuité de service même en l'absence de connexion à un fournisseur d'IA générative.

**Coût récurrent.** Contrairement au mode de repli, chaque appel à l'API Claude engendre un coût facturé à l'usage (au nombre de jetons traités). Aucun mécanisme de limitation par utilisateur (rate limiting) n'est actuellement en place, ce qui constitue un risque en cas de forte adoption ou d'usage abusif. Ce point est identifié comme un développement prioritaire avant un déploiement à grande échelle.

**Perspective.** Une évolution envisageable pour renforcer la souveraineté numérique du projet serait l'hébergement local d'un modèle de langage open-source (par exemple Llama ou Mistral) sur une infrastructure ivoirienne ou africaine, en complément ou remplacement de l'API Anthropic — au prix d'une complexité d'infrastructure et d'un investissement en calcul plus importants, à mettre en balance avec le gain en maîtrise des données.

---

## 💳 Système d'abonnement

Modèle **freemium par rôle** : chaque rôle (commerçant, prestataire, expert, institution) a ses propres paliers d'abonnement avec des limites d'usage (nombre de contrats/dossiers/messages chatbot par mois), et les experts peuvent souscrire à une mise en avant dans l'annuaire.

**Modèles** (`abonnements/`) : `Plan` (par rôle, prix, limites), `Abonnement` (statut, dates de validité), `Paiement` (moyen, statut, référence de transaction).

**Paiement Mobile Money** : intégration via **CinetPay**, un agrégateur qui couvre Orange Money, MTN Mobile Money, Moov Money, Wave et carte bancaire en une seule API — plus réaliste que d'intégrer chaque opérateur télécom séparément (commission CinetPay ≈ 3,5% par transaction en Côte d'Ivoire, pas d'abonnement fixe). Sans compte marchand actif, le système bascule en **mode simulation** : demande du numéro à débiter, message d'attente de confirmation réaliste, et un bouton de simulation qui reproduit le comportement du vrai webhook — avec un garde-fou testé qui empêche formellement cette simulation de fonctionner si un vrai compte CinetPay venait à être configuré.

**Espace admin** (`/abonnements/admin/`) : revenu total et mensuel, répartition par plan et par moyen de paiement, suivi des abonnements et paiements.

---

## 🧪 Tests

Suite de non-régression (`test_general_app.py`, **28 tests**) couvrant l'ensemble des apps : pages publiques/protégées par rôle, cycles de vie complets (contrats, documents, dossiers de collaboration), chatbot et recommandation de bout en bout, API REST (JWT), et système d'abonnement (souscription, paiement, limites, garde-fou de sécurité).

```bash
python manage.py test test_general_app -v 2 --noinput
```

Utilise la base de données de test Django (créée et détruite automatiquement) — ne touche jamais la base de développement.

---

## 🚢 Déploiement Production

```bash
# Installer Nginx + Gunicorn
pip install gunicorn
sudo apt install nginx

# Configurer les variables d'environnement
export DJANGO_SECRET_KEY="votre-clé-secrète"
export DATABASE_URL="mysql://user:password@localhost/legal_connect"
export DEBUG=False

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer Gunicorn
gunicorn legal_connect.wsgi:application --bind 0.0.0.0:8000

# Configurer Nginx comme reverse proxy
# Voir docs/nginx.conf pour la configuration
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Poussez sur la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

---

## 📜 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👨‍💻 Auteur

**Légal Connect** — Projet de fin d'études Master 1 MIAGE  
Université Nangui Abrogoua — Côte d'Ivoire  
Année universitaire 2025-2026  
Encadrant : **Dr. ZEZE**

---

## 📞 Contact

Pour toute question ou suggestion, ouvrez une [issue GitHub](https://github.com/votre-username/legal-connect/issues).

---

*Légal Connect — Le Droit et la Fiscalité à portée de tous* ⚖️
