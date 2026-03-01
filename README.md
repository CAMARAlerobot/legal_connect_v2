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
