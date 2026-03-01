"""
Script de données de test — Légal Connect
Exécuter avec : python manage.py shell < populate_db.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legal_connect.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profil
from contrats.models import ModeleContrat, Contrat
from documents.models import Document
from fiscalite.models import Declaration, Echeance
from collaboration.models import Dossier, Message, Commentaire
from notifications.models import Notification
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

print("🚀 Création des données de test...")

# ── 1. UTILISATEURS ────────────────────────────────────────────────

# Superadmin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin', password='admin123',
        email='admin@legalconnect.ci',
        first_name='Super', last_name='Admin'
    )
    Profil.objects.filter(utilisateur=admin).update(role='admin')
    print("✓ Admin créé — login: admin / admin123")
else:
    admin = User.objects.get(username='admin')
    print("✓ Admin existant")

# Expert 1
if not User.objects.filter(username='expert1').exists():
    expert1 = User.objects.create_user(
        username='expert1', password='expert123',
        email='expert1@legalconnect.ci',
        first_name='Kouassi', last_name='BAMBA'
    )
    p, _ = Profil.objects.get_or_create(utilisateur=expert1)
    p.role       = 'expert'
    p.specialite = 'droit_commercial'
    p.entreprise = 'Cabinet BAMBA & Associés'
    p.telephone  = '+225 07 00 11 22 33'
    p.adresse    = 'Plateau, Abidjan'
    p.bio        = 'Avocat spécialisé en droit commercial et droit des affaires avec 10 ans d\'expérience. Expert en rédaction de contrats commerciaux et résolution de litiges.'
    p.save()
    print("✓ Expert 1 créé — login: expert1 / expert123")
else:
    expert1 = User.objects.get(username='expert1')
    print("✓ Expert 1 existant")

# Expert 2
if not User.objects.filter(username='expert2').exists():
    expert2 = User.objects.create_user(
        username='expert2', password='expert123',
        email='expert2@legalconnect.ci',
        first_name='Aminata', last_name='COULIBALY'
    )
    p, _ = Profil.objects.get_or_create(utilisateur=expert2)
    p.role       = 'expert'
    p.specialite = 'comptabilite'
    p.entreprise = 'Cabinet Comptable COULIBALY'
    p.telephone  = '+225 05 44 55 66 77'
    p.adresse    = 'Cocody, Abidjan'
    p.bio        = 'Expert-comptable certifiée spécialisée en fiscalité des PME et du secteur informel. 8 ans d\'expérience en comptabilité et conseil fiscal.'
    p.save()
    print("✓ Expert 2 créé — login: expert2 / expert123")
else:
    expert2 = User.objects.get(username='expert2')
    print("✓ Expert 2 existant")

# Commerçant 1
if not User.objects.filter(username='client1').exists():
    client1 = User.objects.create_user(
        username='client1', password='client123',
        email='client1@gmail.com',
        first_name='Kofi', last_name='ASANTE'
    )
    p, _ = Profil.objects.get_or_create(utilisateur=client1)
    p.role      = 'commercant'
    p.entreprise= 'Boutique ASANTE'
    p.telephone = '+225 01 22 33 44 55'
    p.adresse   = 'Adjamé, Abidjan'
    p.bio       = 'Commerçant spécialisé dans la vente de textiles et prêt-à-porter.'
    p.save()
    print("✓ Client 1 créé — login: client1 / client123")
else:
    client1 = User.objects.get(username='client1')
    print("✓ Client 1 existant")

# Commerçant 2
if not User.objects.filter(username='client2').exists():
    client2 = User.objects.create_user(
        username='client2', password='client123',
        email='client2@gmail.com',
        first_name='Fatou', last_name='DIALLO'
    )
    p, _ = Profil.objects.get_or_create(utilisateur=client2)
    p.role      = 'prestataire'
    p.entreprise= 'DIALLO Services Informatiques'
    p.telephone = '+225 07 88 99 00 11'
    p.adresse   = 'Yopougon, Abidjan'
    p.bio       = 'Prestataire de services informatiques : développement web, maintenance et formation.'
    p.save()
    print("✓ Client 2 créé — login: client2 / client123")
else:
    client2 = User.objects.get(username='client2')
    print("✓ Client 2 existant")

# ── 2. MODELES DE CONTRATS ─────────────────────────────────────────

modeles_data = [
    {
        'titre'        : 'Contrat de Prestation de Services',
        'type_contrat' : 'prestation',
        'description'  : 'Modèle standard pour les prestations de services entre professionnels.',
        'contenu'      : """CONTRAT DE PRESTATION DE SERVICES

Entre les soussignés :

{{CLIENT_NOM}}, ci-après dénommé "Le Client"
Et
{{PRESTATAIRE_NOM}}, ci-après dénommé "Le Prestataire"

Il a été convenu ce qui suit :

Article 1 — Objet du contrat
Le Prestataire s'engage à fournir les services suivants : {{DESCRIPTION_SERVICE}}

Article 2 — Durée
Le présent contrat prend effet le {{DATE_DEBUT}} et se termine le {{DATE_FIN}}.

Article 3 — Rémunération
En contrepartie des services, le Client versera la somme de {{MONTANT}} FCFA selon les modalités suivantes : {{MODALITES_PAIEMENT}}.

Article 4 — Obligations du Prestataire
Le Prestataire s'engage à exécuter les missions avec professionnalisme et diligence.

Article 5 — Obligations du Client
Le Client s'engage à fournir toutes les informations nécessaires et à régler les factures dans les délais convenus.

Article 6 — Résiliation
Chaque partie peut résilier le présent contrat avec un préavis de {{PREAVIS}} jours.

Fait à {{LIEU}}, le {{DATE_SIGNATURE}}

Le Client                          Le Prestataire
{{CLIENT_NOM}}                     {{PRESTATAIRE_NOM}}""",
    },
    {
        'titre'        : 'Contrat de Vente',
        'type_contrat' : 'vente',
        'description'  : 'Modèle de contrat pour la vente de biens entre particuliers ou professionnels.',
        'contenu'      : """CONTRAT DE VENTE

Entre les soussignés :

{{VENDEUR_NOM}}, ci-après dénommé "Le Vendeur"
Et
{{ACHETEUR_NOM}}, ci-après dénommé "L'Acheteur"

Article 1 — Objet
Le Vendeur cède à l'Acheteur le bien suivant : {{DESCRIPTION_BIEN}}

Article 2 — Prix
Le prix de vente est fixé à {{PRIX}} FCFA, payable selon les modalités suivantes : {{MODALITES_PAIEMENT}}.

Article 3 — Livraison
La livraison aura lieu le {{DATE_LIVRAISON}} à {{LIEU_LIVRAISON}}.

Article 4 — Garanties
Le Vendeur garantit que le bien est exempt de tout vice caché et de toute servitude non déclarée.

Fait à {{LIEU}}, le {{DATE_SIGNATURE}}

Le Vendeur                         L'Acheteur
{{VENDEUR_NOM}}                    {{ACHETEUR_NOM}}""",
    },
    {
        'titre'        : 'Contrat de Bail Commercial',
        'type_contrat' : 'bail',
        'description'  : 'Modèle de bail pour les locaux commerciaux.',
        'contenu'      : """CONTRAT DE BAIL COMMERCIAL

Entre les soussignés :

{{BAILLEUR_NOM}}, ci-après dénommé "Le Bailleur"
Et
{{LOCATAIRE_NOM}}, ci-après dénommé "Le Locataire"

Article 1 — Désignation des locaux
Le Bailleur donne en location les locaux situés à : {{ADRESSE_LOCAUX}}
Surface approximative : {{SURFACE}} m²

Article 2 — Durée du bail
Le bail est consenti pour une durée de {{DUREE}} ans, à compter du {{DATE_DEBUT}}.

Article 3 — Loyer
Le loyer mensuel est fixé à {{LOYER}} FCFA, payable le {{JOUR_PAIEMENT}} de chaque mois.

Article 4 — Dépôt de garantie
Un dépôt de garantie de {{DEPOT_GARANTIE}} FCFA est versé à la signature.

Article 5 — Destination des locaux
Les locaux sont loués exclusivement pour l'exercice d'une activité commerciale de : {{ACTIVITE}}.

Fait à {{LIEU}}, le {{DATE_SIGNATURE}}

Le Bailleur                        Le Locataire
{{BAILLEUR_NOM}}                   {{LOCATAIRE_NOM}}""",
    },
]

for m in modeles_data:
    if not ModeleContrat.objects.filter(titre=m['titre']).exists():
        ModeleContrat.objects.create(**m, actif=True)
        print(f"✓ Modèle de contrat créé : {m['titre']}")

# ── 3. CONTRATS ────────────────────────────────────────────────────

modele_prestation = ModeleContrat.objects.get(type_contrat='prestation')
modele_vente      = ModeleContrat.objects.get(type_contrat='vente')

contrats_data = [
    {
        'proprietaire'      : client1,
        'modele'            : modele_prestation,
        'titre'             : 'Contrat de développement site web',
        'type_contrat'      : 'prestation',
        'statut'            : 'finalise',
        'nom_client'        : 'Boutique ASANTE',
        'email_client'      : 'asante@gmail.com',
        'telephone_client'  : '+225 01 22 33 44 55',
        'adresse_client'    : 'Adjamé, Abidjan',
        'nom_prestataire'   : 'DIALLO Services Informatiques',
        'email_prestataire' : 'diallo@gmail.com',
        'objet'             : 'Développement d\'un site e-commerce pour la vente de textiles en ligne.',
        'montant'           : Decimal('1500000'),
        'devise'            : 'FCFA',
        'date_debut'        : date(2026, 1, 15),
        'date_fin'          : date(2026, 4, 15),
        'lieu_signature'    : 'Abidjan',
        'contenu_final'     : 'Contrat de prestation pour développement d\'un site e-commerce.',
    },
    {
        'proprietaire'      : client2,
        'modele'            : modele_vente,
        'titre'             : 'Vente de matériel informatique',
        'type_contrat'      : 'vente',
        'statut'            : 'brouillon',
        'nom_client'        : 'Boutique ASANTE',
        'email_client'      : 'asante@gmail.com',
        'nom_prestataire'   : 'DIALLO Services Informatiques',
        'email_prestataire' : 'diallo@gmail.com',
        'objet'             : 'Vente de 5 ordinateurs portables HP EliteBook.',
        'montant'           : Decimal('4250000'),
        'devise'            : 'FCFA',
        'lieu_signature'    : 'Abidjan',
        'contenu_final'     : 'Vente de 5 ordinateurs portables.',
    },
    {
        'proprietaire'      : client1,
        'modele'            : modele_prestation,
        'titre'             : 'Contrat de maintenance informatique',
        'type_contrat'      : 'prestation',
        'statut'            : 'signe',
        'nom_client'        : 'Boutique ASANTE',
        'email_client'      : 'asante@gmail.com',
        'telephone_client'  : '+225 01 22 33 44 55',
        'nom_prestataire'   : 'TechSupport CI',
        'email_prestataire' : 'techsupport@gmail.com',
        'objet'             : 'Maintenance mensuelle du parc informatique et assistance technique.',
        'montant'           : Decimal('150000'),
        'devise'            : 'FCFA',
        'date_debut'        : date(2026, 1, 1),
        'date_fin'          : date(2026, 12, 31),
        'lieu_signature'    : 'Abidjan',
        'contenu_final'     : 'Contrat de maintenance mensuelle du système informatique.',
    },
]

for c in contrats_data:
    if not Contrat.objects.filter(titre=c['titre'], proprietaire=c['proprietaire']).exists():
        Contrat.objects.create(**c)
        print(f"✓ Contrat créé : {c['titre']}")

# ── 4. DECLARATIONS FISCALES ───────────────────────────────────────

decls_data = [
    {
        'utilisateur'     : client1,
        'type_impot'      : 'tva',
        'periode'         : 'mensuel',
        'annee'           : 2026,
        'mois'            : 1,
        'chiffre_affaires': Decimal('8500000'),
        'charges'         : Decimal('0'),
        'benefice_net'    : Decimal('0'),
        'taux_applique'   : Decimal('18'),
        'montant_impot'   : Decimal('1530000'),
        'statut'          : 'soumise',
    },
    {
        'utilisateur'     : client1,
        'type_impot'      : 'is',
        'periode'         : 'annuel',
        'annee'           : 2025,
        'mois'            : None,
        'chiffre_affaires': Decimal('45000000'),
        'charges'         : Decimal('28000000'),
        'benefice_net'    : Decimal('17000000'),
        'taux_applique'   : Decimal('25'),
        'montant_impot'   : Decimal('4750000'),
        'statut'          : 'validee',
    },
    {
        'utilisateur'     : client2,
        'type_impot'      : 'bnc',
        'periode'         : 'annuel',
        'annee'           : 2025,
        'mois'            : None,
        'chiffre_affaires': Decimal('12000000'),
        'charges'         : Decimal('4500000'),
        'benefice_net'    : Decimal('7500000'),
        'taux_applique'   : Decimal('20'),
        'montant_impot'   : Decimal('1500000'),
        'statut'          : 'en_attente',
    },
]

for d in decls_data:
    Declaration.objects.get_or_create(
        utilisateur=d['utilisateur'],
        type_impot=d['type_impot'],
        annee=d['annee'],
        defaults=d
    )
    print(f"✓ Déclaration créée : {d['type_impot'].upper()} {d['annee']}")

# ── 5. ECHEANCES FISCALES ──────────────────────────────────────────

echeances_data = [
    {
        'utilisateur' : client1,
        'titre'       : 'Déclaration TVA — Février 2026',
        'type_impot'  : 'tva',
        'date_limite' : date(2026, 3, 15),
        'montant'     : Decimal('1200000'),
        'statut'      : 'a_faire',
        'notes'       : 'Ne pas oublier les factures fournisseurs',
    },
    {
        'utilisateur' : client1,
        'titre'       : 'Paiement IS — Exercice 2025',
        'type_impot'  : 'is',
        'date_limite' : date(2026, 4, 30),
        'montant'     : Decimal('4750000'),
        'statut'      : 'a_faire',
        'notes'       : '',
    },
    {
        'utilisateur' : client2,
        'titre'       : 'Déclaration BNC — Exercice 2025',
        'type_impot'  : 'bnc',
        'date_limite' : date(2026, 3, 31),
        'montant'     : Decimal('1500000'),
        'statut'      : 'a_faire',
        'notes'       : 'Préparer les justificatifs de charges',
    },
    {
        'utilisateur' : client1,
        'titre'       : 'Cotisations CNPS — Janvier 2026',
        'type_impot'  : 'cnps',
        'date_limite' : date(2026, 2, 15),
        'montant'     : Decimal('180000'),
        'statut'      : 'fait',
        'notes'       : '',
    },
]

for e in echeances_data:
    Echeance.objects.get_or_create(
        utilisateur=e['utilisateur'],
        titre=e['titre'],
        defaults=e
    )
    print(f"✓ Échéance créée : {e['titre']}")

# ── 6. DOSSIERS COLLABORATION ──────────────────────────────────────

dossiers_data = [
    {
        'client'      : client1,
        'expert'      : expert1,
        'titre'       : 'Vérification contrat fournisseur tissus',
        'description' : 'J\'ai reçu un contrat de mon fournisseur de tissus de 15 pages. Je voudrais qu\'un expert vérifie les clauses de résiliation et les pénalités de retard avant de signer.',
        'type_dossier': 'contrat',
        'statut'      : 'valide',
        'priorite'    : 'haute',
        'note_expert' : 'Contrat examiné. Les clauses de résiliation sont équilibrées. Toutefois, je recommande de négocier l\'article 12 sur les pénalités qui semble excessif (5% par jour). Proposez 1% par semaine à la place. Le reste du contrat est conforme aux standards du secteur.',
    },
    {
        'client'      : client2,
        'expert'      : expert2,
        'titre'       : 'Conseil fiscal pour déclaration BNC 2025',
        'description' : 'Je suis prestataire de services informatiques. C\'est ma première déclaration BNC et je ne sais pas quelles charges sont déductibles. Puis-je déduire mon ordinateur, mon abonnement internet et mes déplacements ?',
        'type_dossier': 'fiscal',
        'statut'      : 'en_cours',
        'priorite'    : 'normale',
        'note_expert' : '',
    },
    {
        'client'      : client1,
        'expert'      : None,
        'titre'       : 'Problème avec un client qui ne paie pas',
        'description' : 'Un client me doit 850 000 FCFA depuis 3 mois. J\'ai un contrat signé. Quelles sont mes options légales pour récupérer cette somme ? Puis-je aller en justice ?',
        'type_dossier': 'juridique',
        'statut'      : 'en_attente',
        'priorite'    : 'urgente',
        'note_expert' : '',
    },
]

dossiers_crees = []
for d in dossiers_data:
    dossier, created = Dossier.objects.get_or_create(
        client=d['client'], titre=d['titre'],
        defaults=d
    )
    dossiers_crees.append(dossier)
    if created:
        print(f"✓ Dossier créé : {d['titre']}")

# ── 7. MESSAGES DANS LES DOSSIERS ─────────────────────────────────

dossier_valide  = dossiers_crees[0]
dossier_en_cours = dossiers_crees[1]

messages_data = [
    # Dossier validé
    {'dossier': dossier_valide, 'auteur': client1,  'contenu': 'Bonjour Maître, je vous envoie le contrat de mon fournisseur. Merci de vérifier particulièrement les articles 8, 12 et 15.', 'lu': True},
    {'dossier': dossier_valide, 'auteur': expert1,  'contenu': 'Bonjour M. ASANTE. J\'ai bien reçu votre demande. Je commence l\'examen du contrat et reviens vers vous dans 48h.', 'lu': True},
    {'dossier': dossier_valide, 'auteur': expert1,  'contenu': 'Après examen, les articles 8 et 15 sont standards. L\'article 12 (pénalités de 5%/jour) est problématique. Je vous recommande de le négocier.', 'lu': True},
    {'dossier': dossier_valide, 'auteur': client1,  'contenu': 'Merci beaucoup ! J\'ai négocié avec mon fournisseur et il accepte 1%/semaine. Pouvez-vous valider le dossier ?', 'lu': True},
    # Dossier en cours
    {'dossier': dossier_en_cours, 'auteur': client2, 'contenu': 'Bonjour, j\'aimerais savoir si je peux déduire mon MacBook Pro acheté 850 000 FCFA pour le travail.', 'lu': True},
    {'dossier': dossier_en_cours, 'auteur': expert2, 'contenu': 'Bonjour Mme DIALLO. Oui, le matériel informatique est déductible en BNC à 100% l\'année d\'achat si utilisé exclusivement pour l\'activité.', 'lu': True},
    {'dossier': dossier_en_cours, 'auteur': client2, 'contenu': 'Et mon abonnement internet et téléphone ?', 'lu': False},
]

for m in messages_data:
    Message.objects.get_or_create(
        dossier=m['dossier'], auteur=m['auteur'], contenu=m['contenu'][:50],
        defaults=m
    )

print("✓ Messages créés dans les dossiers")

# ── 8. NOTIFICATIONS ───────────────────────────────────────────────

notifs_data = [
    {
        'destinataire': client1,
        'type_notif'  : 'dossier_valide',
        'titre'       : 'Dossier validé : Vérification contrat fournisseur tissus',
        'message'     : 'Votre dossier a été validé par Maître BAMBA. Consultez son avis détaillé.',
        'lien'        : f'/collaboration/{dossier_valide.pk}/',
        'lu'          : False,
    },
    {
        'destinataire': expert2,
        'type_notif'  : 'nouveau_message',
        'titre'       : 'Nouveau message dans : Conseil fiscal BNC 2025',
        'message'     : 'Fatou DIALLO vous a envoyé un message : "Et mon abonnement internet et téléphone ?"',
        'lien'        : f'/collaboration/{dossier_en_cours.pk}/',
        'lu'          : False,
    },
    {
        'destinataire': client1,
        'type_notif'  : 'echeance_7j',
        'titre'       : '📅 Échéance dans 14 jours : Déclaration TVA Février 2026',
        'message'     : 'Votre déclaration TVA est due le 15 Mars 2026. Montant estimé : 1 200 000 FCFA.',
        'lien'        : '/fiscalite/calendrier/',
        'lu'          : False,
    },
    {
        'destinataire': client2,
        'type_notif'  : 'contrat_genere',
        'titre'       : 'Contrat généré : Vente de matériel informatique',
        'message'     : 'Votre contrat a été créé avec succès. Vous pouvez le finaliser et l\'exporter en PDF.',
        'lien'        : '/contrats/',
        'lu'          : True,
    },
]

for n in notifs_data:
    Notification.objects.get_or_create(
        destinataire=n['destinataire'],
        titre=n['titre'],
        defaults=n
    )
    print(f"✓ Notification créée pour {n['destinataire'].username}")

# ── RESUME ─────────────────────────────────────────────────────────
print("\n" + "="*50)
print("✅ DONNÉES DE TEST CRÉÉES AVEC SUCCÈS !")
print("="*50)
print("\n📋 COMPTES DISPONIBLES :")
print("  admin    / admin123  → Administrateur")
print("  expert1  / expert123 → Kouassi BAMBA (Droit Commercial)")
print("  expert2  / expert123 → Aminata COULIBALY (Comptabilité)")
print("  client1  / client123 → Kofi ASANTE (Commerçant)")
print("  client2  / client123 → Fatou DIALLO (Prestataire)")
print("\n📊 DONNÉES CRÉÉES :")
print(f"  • {ModeleContrat.objects.count()} modèles de contrats")
print(f"  • {Contrat.objects.count()} contrats")
print(f"  • {Declaration.objects.count()} déclarations fiscales")
print(f"  • {Echeance.objects.count()} échéances fiscales")
print(f"  • {Dossier.objects.count()} dossiers collaboration")
print(f"  • {Message.objects.count()} messages")
print(f"  • {Notification.objects.count()} notifications")
print("\n🌐 Testez sur : http://127.0.0.1:8000")