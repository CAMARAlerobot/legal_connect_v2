# 🗄️ Base de Données — Légal Connect

## Technologie

- **SGBD** : MySQL 8.0 (production) / SQLite 3 (développement)
- **ORM** : Django ORM (pas de SQL brut)
- **Migrations** : `python manage.py migrate`

---

## 📊 Schéma des Tables (MCD simplifié)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        auth_user (Django)                           │
│  id | username | email | first_name | last_name | password | ...    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ 1
                           │ OneToOne
                           ▼ 1
┌──────────────────────────────────────────────────────────────────────┐
│                           accounts_profil                            │
│  id | utilisateur_id | role | specialite | telephone | entreprise   │
│       adresse | bio                                                  │
└──────────────────────────────────────────────────────────────────────┘
         │                          │
         │ 1                        │ 1
         │                          │
         ▼ N                        ▼ N
┌─────────────────┐      ┌──────────────────────────────┐
│ contrats_contrat│      │   collaboration_dossier       │
│ id              │      │   id                         │
│ proprietaire_id │      │   client_id (FK → User)      │
│ modele_id       │      │   expert_id (FK → User)      │
│ type_contrat    │      │   titre                      │
│ titre           │      │   description                │
│ nom_client      │      │   type_dossier               │
│ email_client    │      │   statut                     │
│ nom_prestataire │      │   priorite                   │
│ objet           │      │   note_expert                │
│ montant         │      │   created_at                 │
│ date_debut      │      └──────────────┬───────────────┘
│ date_fin        │                     │ 1
│ statut          │                     │
│ contenu_final   │             ┌───────┴────────────────┐
│ created_at      │             │                        │
└─────────────────┘             ▼ N                      ▼ N
         │                ┌──────────────────┐  ┌────────────────────┐
         │                │collaboration_    │  │collaboration_      │
         ▼ N              │message           │  │commentaire         │
┌──────────────────┐      │ id               │  │ id                 │
│contrats_modele   │      │ dossier_id       │  │ dossier_id         │
│ id               │      │ auteur_id        │  │ auteur_id          │
│ nom              │      │ contenu          │  │ contenu            │
│ type_contrat     │      │ lu               │  │ created_at         │
│ contenu_template │      │ created_at       │  └────────────────────┘
│ created_at       │      └──────────────────┘
└──────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       documents_document                          │
│  id | proprietaire_id | titre | fichier | categorie | statut    │
│       taille | type_fichier | description | created_at           │
└──────────────────────────────────────────────────────────────────┘
                    │ N
                    │ ManyToMany
                    ▼ N
              [utilisateurs partagés]

┌──────────────────────────────────────────────────────────────────┐
│                      fiscalite_declaration                        │
│  id | utilisateur_id | type_impot | periode | annee | mois       │
│       chiffre_affaires | charges | benefice_net | taux_applique  │
│       montant_impot | statut | created_at                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                       fiscalite_echeance                          │
│  id | utilisateur_id | titre | type_impot | date_limite          │
│       montant | statut | notes | created_at                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    notifications_notification                     │
│  id | destinataire_id | type_notif | titre | message             │
│       lu | lien | created_at                                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📋 Description détaillée des tables

### `auth_user` — Utilisateurs Django (natif)
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| username | VARCHAR(150) | Nom d'utilisateur |
| email | VARCHAR(254) | Adresse email |
| first_name | VARCHAR(150) | Prénom |
| last_name | VARCHAR(150) | Nom de famille |
| password | VARCHAR(128) | Mot de passe hashé (PBKDF2) |
| is_active | BOOLEAN | Compte actif |
| date_joined | DATETIME | Date de création |

---

### `accounts_profil` — Profils utilisateurs
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| utilisateur_id | FK → auth_user | Lien OneToOne avec User |
| role | VARCHAR(20) | commercant, expert, institution, admin, auditeur, prestataire |
| specialite | VARCHAR(30) | droit_commercial, comptabilite, droit_fiscal... (experts) |
| telephone | VARCHAR(20) | Numéro de téléphone |
| entreprise | VARCHAR(200) | Nom de l'entreprise ou du cabinet |
| adresse | VARCHAR(300) | Adresse physique |
| bio | TEXT | Présentation / biographie |

---

### `contrats_modelecontrat` — Modèles de contrats
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| nom | VARCHAR(200) | Nom du modèle |
| type_contrat | VARCHAR(30) | prestation, vente, bail, travail, partenariat, nda, autre |
| description | TEXT | Description du modèle |
| contenu_template | TEXT | Template avec variables `{{nom_client}}` etc. |
| actif | BOOLEAN | Modèle disponible ou non |
| created_at | DATETIME | Date de création |

---

### `contrats_contrat` — Contrats générés
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| proprietaire_id | FK → auth_user | Propriétaire du contrat |
| modele_id | FK → ModeleContrat | Modèle utilisé |
| type_contrat | VARCHAR(30) | Type de contrat |
| titre | VARCHAR(200) | Titre du contrat |
| nom_client | VARCHAR(200) | Nom de la partie cliente |
| email_client | VARCHAR(254) | Email client |
| telephone_client | VARCHAR(20) | Téléphone client |
| adresse_client | VARCHAR(300) | Adresse client |
| nom_prestataire | VARCHAR(200) | Nom du prestataire |
| email_prestataire | VARCHAR(254) | Email prestataire |
| objet | TEXT | Objet du contrat |
| montant | DECIMAL(15,2) | Montant en FCFA |
| devise | VARCHAR(10) | FCFA, EUR, USD |
| date_debut | DATE | Date de début |
| date_fin | DATE | Date de fin |
| lieu_signature | VARCHAR(200) | Lieu de signature |
| statut | VARCHAR(20) | brouillon, finalise, signe, archive |
| contenu_final | TEXT | Contenu généré par l'IA |
| clauses_speciales | TEXT | Clauses particulières |
| created_at | DATETIME | Date de création |

---

### `documents_document` — Documents uploadés
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| proprietaire_id | FK → auth_user | Propriétaire |
| titre | VARCHAR(200) | Titre du document |
| fichier | FileField | Chemin du fichier uploadé |
| categorie | VARCHAR(30) | contrat, fiscal, identite, juridique, comptable, autre |
| statut | VARCHAR(20) | actif, archive, partage |
| taille | INT | Taille en octets |
| type_fichier | VARCHAR(10) | pdf, docx, jpg... |
| description | TEXT | Description |
| partage_avec | M2M → auth_user | Utilisateurs ayant accès |
| created_at | DATETIME | Date d'upload |

---

### `fiscalite_declaration` — Déclarations fiscales
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| utilisateur_id | FK → auth_user | Déclarant |
| type_impot | VARCHAR(10) | tva, is, cnps, bnc, bic |
| periode | VARCHAR(20) | mensuel, trimestriel, annuel |
| annee | INT | Année fiscale |
| mois | INT | Mois (1-12, optionnel) |
| trimestre | INT | Trimestre (1-4, optionnel) |
| chiffre_affaires | DECIMAL(15,2) | CA en FCFA |
| charges | DECIMAL(15,2) | Charges déductibles |
| benefice_net | DECIMAL(15,2) | Bénéfice net calculé |
| taux_applique | DECIMAL(5,2) | Taux appliqué (%) |
| montant_impot | DECIMAL(15,2) | Montant de l'impôt |
| statut | VARCHAR(20) | soumise, validee, en_attente, rejetee |
| created_at | DATETIME | Date de déclaration |

---

### `fiscalite_echeance` — Calendrier fiscal
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| utilisateur_id | FK → auth_user | Propriétaire |
| titre | VARCHAR(200) | Titre de l'échéance |
| type_impot | VARCHAR(10) | Type d'impôt concerné |
| date_limite | DATE | Date limite de paiement |
| montant | DECIMAL(15,2) | Montant à payer (optionnel) |
| statut | VARCHAR(20) | a_faire, fait, en_retard |
| notes | TEXT | Notes supplémentaires |
| created_at | DATETIME | Date de création |

---

### `collaboration_dossier` — Dossiers expert-client
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| client_id | FK → auth_user | Client demandeur |
| expert_id | FK → auth_user | Expert assigné (nullable) |
| titre | VARCHAR(200) | Titre du dossier |
| description | TEXT | Description détaillée |
| type_dossier | VARCHAR(30) | juridique, fiscal, contrat, social, autre |
| statut | VARCHAR(20) | en_attente, en_cours, valide, rejete, archive |
| priorite | VARCHAR(20) | basse, normale, haute, urgente |
| note_expert | TEXT | Avis de l'expert |
| created_at | DATETIME | Date de création |

---

### `notifications_notification` — Notifications
| Champ | Type | Description |
|---|---|---|
| id | INT PK | Identifiant unique |
| destinataire_id | FK → auth_user | Destinataire |
| type_notif | VARCHAR(30) | dossier_valide, nouveau_message, echeance_7j, contrat_genere |
| titre | VARCHAR(200) | Titre de la notification |
| message | TEXT | Contenu de la notification |
| lu | BOOLEAN | Lu ou non lu |
| lien | VARCHAR(500) | URL de redirection |
| created_at | DATETIME | Date de création |

---

## 🔗 Relations entre tables (MCD)

```
auth_user ──────────── 1:1 ──────── accounts_profil
auth_user ──────────── 1:N ──────── contrats_contrat (proprietaire)
auth_user ──────────── 1:N ──────── documents_document (proprietaire)
auth_user ──────────── 1:N ──────── fiscalite_declaration (utilisateur)
auth_user ──────────── 1:N ──────── fiscalite_echeance (utilisateur)
auth_user ──────────── 1:N ──────── collaboration_dossier (client)
auth_user ──────────── 1:N ──────── collaboration_dossier (expert)
auth_user ──────────── 1:N ──────── notifications_notification (destinataire)
auth_user ──────────── N:M ──────── documents_document (partage_avec)

contrats_modelecontrat ─ 1:N ──────── contrats_contrat (modele)
collaboration_dossier  ─ 1:N ──────── collaboration_message
collaboration_dossier  ─ 1:N ──────── collaboration_commentaire
```

---

## ⚙️ Taux fiscaux implémentés

| Type | Taux | Formule |
|---|---|---|
| TVA | 18% flat | `CA × 0.18` |
| IS | 20-25-30% progressif | Tranches + min 500K FCFA |
| CNPS | 23.2% total | `(salaire × nb_employes) × 0.232` |
| BNC | 20% flat | `benefice_net × 0.20` |
| BIC | 25% flat | `benefice_net × 0.25` |

---

## 🛠️ Commandes utiles

```bash
# Créer les migrations après modification d'un modèle
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations

# Accéder au shell Django
python manage.py shell

# Générer les données de test
python populate_db.py

# Voir les requêtes SQL générées
python manage.py sqlmigrate app_name 0001
```
