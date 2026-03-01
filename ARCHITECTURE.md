# 🏗️ Architecture Légal Connect — Communication entre Fichiers

## Vue d'ensemble

Légal Connect suit le pattern **MVT (Model-View-Template)** de Django.
Chaque requête HTTP suit ce flux :

```
Navigateur → urls.py → views.py → models.py → views.py → template.html → Navigateur
```

---

## 📁 Structure du Projet

```
legal_connect_v2/
│
├── legal_connect/              # Projet Django principal
│   ├── settings.py             # Configuration globale
│   ├── urls.py                 # Routeur principal
│   └── wsgi.py                 # Point d'entrée WSGI
│
├── accounts/                   # Authentification & Profils
│   ├── models.py               # Modèle Profil (OneToOne User)
│   ├── views.py                # Vues : login, inscription, dashboard, profil
│   ├── urls.py                 # Routes /accounts/
│   ├── forms.py                # Formulaires inscription/profil
│   └── templates/accounts/
│       ├── login.html
│       ├── inscription.html
│       ├── dashboard.html
│       └── profil.html
│
├── contrats/                   # Génération de contrats
│   ├── models.py               # ModeleContrat, Contrat
│   ├── views.py                # CRUD contrats + export PDF ReportLab
│   ├── urls.py                 # Routes /contrats/
│   └── templates/contrats/
│       ├── liste.html
│       ├── creer.html
│       ├── modifier.html
│       └── detail.html
│
├── documents/                  # Gestion documentaire
│   ├── models.py               # Document (upload, catégorie, partage)
│   ├── views.py                # Upload, liste, partage, téléchargement
│   ├── urls.py                 # Routes /documents/
│   └── templates/documents/
│
├── fiscalite/                  # Calcul fiscal
│   ├── models.py               # Declaration, Echeance
│   ├── views.py                # Calculateur, historique, PDF, calendrier
│   ├── calculateur.py          # Logique de calcul TVA/IS/CNPS/BNC/BIC
│   ├── urls.py                 # Routes /fiscalite/
│   └── templates/fiscalite/
│
├── collaboration/              # Dossiers expert-client
│   ├── models.py               # Dossier, Message, Commentaire
│   ├── views.py                # Création dossier, messagerie, validation
│   ├── urls.py                 # Routes /collaboration/
│   └── templates/collaboration/
│
├── notifications/              # Système de notifications
│   ├── models.py               # Notification
│   ├── views.py                # Liste, marquer lu, AJAX
│   ├── signals.py              # Signaux Django (déclencheurs automatiques)
│   ├── urls.py                 # Routes /notifications/
│   └── templates/notifications/
│
├── annuaire/                   # Annuaire des experts
│   ├── views.py                # Liste experts, profil expert
│   ├── urls.py                 # Routes /annuaire/
│   └── templates/annuaire/
│
└── templates/                  # Templates globaux
    ├── base.html               # Template parent (navbar, sidebar, scripts)
    ├── landing.html            # Page d'accueil publique
    └── includes/
        └── pagination.html     # Composant pagination réutilisable
```

---

## 🔄 Communication entre Fichiers

### 1. `legal_connect/urls.py` — Le Chef d'Orchestre

C'est le **point d'entrée** de toutes les URLs. Il délègue à chaque application.

```python
# legal_connect/urls.py
urlpatterns = [
    path('accounts/',      include('accounts.urls')),      # → accounts/urls.py
    path('contrats/',      include('contrats.urls')),      # → contrats/urls.py
    path('fiscalite/',     include('fiscalite.urls')),     # → fiscalite/urls.py
    path('collaboration/', include('collaboration.urls')), # → collaboration/urls.py
    path('notifications/', include('notifications.urls')), # → notifications/urls.py
    path('annuaire/',      include('annuaire.urls')),      # → annuaire/urls.py
    path('',               accounts_views.landing),        # → Landing page
]
```

**Pourquoi ce fichier ?** Sans lui, Django ne sait pas quelle vue appeler pour quelle URL.

---

### 2. `accounts/models.py` → Utilisé par TOUS les modules

Le modèle `Profil` est au cœur de l'application. Il étend `User` de Django.

```python
# accounts/models.py
class Profil(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    role        = models.CharField(choices=ROLES)       # commercant, expert, admin...
    specialite  = models.CharField(choices=SPECIALITES) # droit_commercial, comptabilite...
    telephone   = models.CharField()
    entreprise  = models.CharField()
    adresse     = models.CharField()
    bio         = models.TextField()
```

**Qui l'utilise ?**
- `collaboration/views.py` → vérifie `profil.role` pour autoriser les actions
- `annuaire/views.py` → filtre les experts par `profil.role == 'expert'`
- `notifications/signals.py` → récupère le destinataire via `profil`
- `contrats/views.py` → associe le contrat au `proprietaire` (User)

---

### 3. `notifications/signals.py` → Déclenché automatiquement

Les signaux Django écoutent les événements des autres modèles.

```
Dossier.save()          →  signal post_save  →  Notification.objects.create()
Contrat.save()          →  signal post_save  →  Notification.objects.create()
Echeance (< 7 jours)    →  tâche planifiée   →  Notification.objects.create()
```

**Pourquoi ce fichier ?** Il permet la communication entre modules sans couplage direct.
`collaboration` ne connaît pas `notifications` — c'est le signal qui fait le lien.

---

### 4. `base.html` → Parent de tous les templates

Tous les templates héritent de `base.html` via `{% extends 'base.html' %}`.

```
base.html
├── accounts/dashboard.html     {% extends 'base.html' %}
├── contrats/liste.html         {% extends 'base.html' %}
├── documents/liste.html        {% extends 'base.html' %}
├── fiscalite/dashboard.html    {% extends 'base.html' %}
├── collaboration/liste.html    {% extends 'base.html' %}
└── annuaire/liste.html         {% extends 'base.html' %}
```

`base.html` contient : navbar, sidebar, CSS Bootstrap, scripts JS, bloc notifications AJAX.

---

### 5. `fiscalite/calculateur.py` → Module de calcul isolé

La logique métier est isolée dans un fichier dédié, appelé par `views.py`.

```python
# fiscalite/views.py
from . import calculateur

resultat = calculateur.calculer('tva', {'chiffre_affaires': 5000000})
# → {'montant_impot': 900000, 'taux': 18, 'base': 5000000}
```

**Pourquoi ce fichier séparé ?** Réutilisabilité, testabilité, séparation des responsabilités.

---

### 6. `includes/pagination.html` → Composant réutilisable

```html
<!-- Dans contrats/liste.html, documents/liste.html, etc. -->
{% include 'includes/pagination.html' %}
```

Ce composant lit `page_obj` passé par la vue et génère la navigation automatiquement.

---

## 🗺️ Schéma de Communication

```
                    ┌─────────────────┐
                    │   Navigateur    │
                    └────────┬────────┘
                             │ HTTP Request
                    ┌────────▼────────┐
                    │  urls.py        │ ← Point d'entrée
                    │  (routeur)      │
                    └────────┬────────┘
                             │ dispatch
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │views.py  │  │views.py  │  │views.py  │
        │accounts  │  │contrats  │  │fiscalite │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
        ┌────▼──────────────▼──────────────▼────┐
        │           models.py (ORM Django)       │
        │  Profil  Contrat  Document  Dossier    │
        │  Declaration  Notification  Echeance   │
        └────────────────────┬──────────────────┘
                             │ SQL
                    ┌────────▼────────┐
                    │   Base MySQL    │
                    └────────┬────────┘
                             │ données
                    ┌────────▼────────┐
                    │  templates/     │
                    │  *.html         │ ← Rendu HTML
                    └────────┬────────┘
                             │ HTTP Response
                    ┌────────▼────────┐
                    │   Navigateur    │
                    └─────────────────┘


  signals.py ──────────────────────────────────►  Notification
  (post_save)   écoute Dossier, Contrat, Echeance   auto-créée
```

---

## 📋 Rôle de chaque fichier clé

| Fichier | Rôle | Pourquoi |
|---|---|---|
| `settings.py` | Configuration Django (BDD, apps, email) | Django ne fonctionne pas sans lui |
| `urls.py` (projet) | Routeur principal | Dispatch les requêtes vers les apps |
| `urls.py` (app) | Routes de l'application | Isole les URLs par module |
| `models.py` | Structure des données + ORM | Définit les tables MySQL |
| `views.py` | Logique métier | Traite les requêtes, prépare le contexte |
| `forms.py` | Validation des formulaires | Sécurise les données entrantes |
| `signals.py` | Événements automatiques | Découple les modules entre eux |
| `calculateur.py` | Logique fiscale isolée | Séparation des responsabilités |
| `base.html` | Template parent | Évite la duplication HTML |
| `pagination.html` | Composant réutilisable | DRY (Don't Repeat Yourself) |
