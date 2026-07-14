"""
Commande Django : python manage.py seed_data
Peuple la base de données avec des données de démonstration réalistes.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profil
from annuaire.models import AvisExpert
from collaboration.models import Dossier, Message
from contrats.models import Contrat, ModeleContrat
from documents.models import Document
from fiscalite.models import Declaration, Echeance
from notifications.models import Notification


# ──────────────────────────────────────────────
# Données brutes
# ──────────────────────────────────────────────

EXPERTS = [
    {
        'username': 'kkouame_avocat',
        'first_name': 'Kouamé',
        'last_name': 'Assi',
        'email': 'k.assi@legalconnect.ci',
        'entreprise': 'Cabinet Assi & Associés',
        'specialite': 'droit_commercial',
        'telephone': '+225 07 01 23 45 67',
        'bio': 'Avocat au Barreau d\'Abidjan depuis 15 ans, spécialisé en droit des affaires et contrats commerciaux. Intervenant régulier au Tribunal de Commerce d\'Abidjan.',
    },
    {
        'username': 'dr_bamba_fiscal',
        'first_name': 'Sékou',
        'last_name': 'Bamba',
        'email': 's.bamba@legalconnect.ci',
        'entreprise': 'Cabinet Bamba Conseil Fiscal',
        'specialite': 'droit_fiscal',
        'telephone': '+225 05 44 78 90 12',
        'bio': 'Expert-comptable et conseil fiscal agréé. 12 ans d\'expérience en optimisation fiscale, TVA, IS et accompagnement DGI pour les PME ivoiriennes.',
    },
    {
        'username': 'me_traore_travail',
        'first_name': 'Aminata',
        'last_name': 'Traoré',
        'email': 'a.traore@legalconnect.ci',
        'entreprise': 'Traoré Legal RH',
        'specialite': 'droit_travail',
        'telephone': '+225 01 55 66 77 88',
        'bio': 'Juriste spécialisée en droit social et droit du travail. Gestion des conflits collectifs, licenciements, négociations salariales et inspection du travail.',
    },
    {
        'username': 'assoumou_compta',
        'first_name': 'Jean-Claude',
        'last_name': 'Assoumou',
        'email': 'jc.assoumou@legalconnect.ci',
        'entreprise': 'Assoumou Finance & Audit',
        'specialite': 'comptabilite',
        'telephone': '+225 07 99 88 77 66',
        'bio': 'Expert-comptable DSCG, commissaire aux comptes. Spécialisé dans la mise en conformité comptable, l\'audit interne et le conseil aux startups ivoiriennes.',
    },
    {
        'username': 'diallo_immobilier',
        'first_name': 'Fatou',
        'last_name': 'Diallo',
        'email': 'f.diallo@legalconnect.ci',
        'entreprise': 'Cabinet Diallo Immobilier & Droit',
        'specialite': 'droit_immobilier',
        'telephone': '+225 05 22 33 44 55',
        'bio': 'Notaire et juriste immobilier. Transactions foncières, baux commerciaux, litiges de voisinage et formalisation des titres fonciers en Côte d\'Ivoire.',
    },
]

CLIENTS = [
    {
        'username': 'konan_marc',
        'first_name': 'Marc',
        'last_name': 'Konan',
        'email': 'marc.konan@gmail.com',
        'role': 'commercant',
        'entreprise': 'Boutique Konan & Fils',
        'telephone': '+225 07 10 20 30 40',
        'adresse': 'Cocody, Rue des Jardins, Abidjan',
    },
    {
        'username': 'ouattara_samira',
        'first_name': 'Samira',
        'last_name': 'Ouattara',
        'email': 'samira.ouattara@yahoo.fr',
        'role': 'prestataire',
        'entreprise': 'Digital Créa CI',
        'telephone': '+225 05 50 60 70 80',
        'adresse': 'Plateau, Avenue Noguès, Abidjan',
    },
    {
        'username': 'brou_felix',
        'first_name': 'Félix',
        'last_name': 'Brou',
        'email': 'felix.brou@hotmail.com',
        'role': 'commercant',
        'entreprise': 'Import-Export Brou',
        'telephone': '+225 01 11 22 33 44',
        'adresse': 'Treichville, Marché de Gros, Abidjan',
    },
    {
        'username': 'coulibaly_awa',
        'first_name': 'Awa',
        'last_name': 'Coulibaly',
        'email': 'awa.coulibaly@gmail.com',
        'role': 'prestataire',
        'entreprise': 'Awa Events & Traiteur',
        'telephone': '+225 07 88 99 00 11',
        'adresse': 'Yopougon, Cité Orly, Abidjan',
    },
    {
        'username': 'n_guessan_paul',
        'first_name': 'Paul',
        'last_name': 'N\'Guessan',
        'email': 'paul.nguessan@gmail.com',
        'role': 'commercant',
        'entreprise': 'Pharmacie N\'Guessan',
        'telephone': '+225 05 77 88 99 00',
        'adresse': 'Adjamé, Boulevard Nangui Abrogoua, Abidjan',
    },
    {
        'username': 'soro_ibrahim',
        'first_name': 'Ibrahim',
        'last_name': 'Soro',
        'email': 'ibrahim.soro@gmail.com',
        'role': 'prestataire',
        'entreprise': 'Soro BTP & Construction',
        'telephone': '+225 01 23 45 67 89',
        'adresse': 'Abobo, Quartier Samaké, Abidjan',
    },
    {
        'username': 'kone_mariam',
        'first_name': 'Mariam',
        'last_name': 'Koné',
        'email': 'mariam.kone@gmail.com',
        'role': 'commercant',
        'entreprise': 'Salon de Beauté Mariam',
        'telephone': '+225 07 34 56 78 90',
        'adresse': 'Marcory, Rue de la Paix, Abidjan',
    },
    {
        'username': 'tape_rodrigue',
        'first_name': 'Rodrigue',
        'last_name': 'Tapé',
        'email': 'rodrigue.tape@outlook.com',
        'role': 'prestataire',
        'entreprise': 'AgriTech Tapé',
        'telephone': '+225 05 65 43 21 09',
        'adresse': 'Bouaké, Quartier Commerce',
    },
    {
        'username': 'diarrassouba_hawa',
        'first_name': 'Hawa',
        'last_name': 'Diarrassouba',
        'email': 'hawa.dia@gmail.com',
        'role': 'commercant',
        'entreprise': 'Restaurant Saveur d\'Afrique',
        'telephone': '+225 01 98 76 54 32',
        'adresse': 'Cocody, 2 Plateaux, Abidjan',
    },
    {
        'username': 'yao_celestin',
        'first_name': 'Célestin',
        'last_name': 'Yao',
        'email': 'celestin.yao@gmail.com',
        'role': 'prestataire',
        'entreprise': 'Yao Consulting IT',
        'telephone': '+225 07 12 34 56 78',
        'adresse': 'Plateau, Tour CCIA, Abidjan',
    },
]

MODELES_CONTRATS = [
    {
        'type_contrat': 'prestation',
        'titre': 'Contrat de prestation de services informatiques',
        'description': 'Modèle standard pour les prestations IT : développement web, maintenance, conseil.',
        'contenu': """CONTRAT DE PRESTATION DE SERVICES

Entre les soussignés :

**LE PRESTATAIRE** : {{nom_prestataire}}, domicilié à {{adresse_prestataire}},
**LE CLIENT** : {{nom_client}}, domicilié à {{adresse_client}},

Il est convenu ce qui suit :

**Article 1 — Objet**
{{objet}}

**Article 2 — Durée**
Du {{date_debut}} au {{date_fin}}.

**Article 3 — Rémunération**
Montant : {{montant}} {{devise}} HT.
TVA applicable au taux légal en vigueur (18%).

**Article 4 — Obligations du prestataire**
Le prestataire s'engage à exécuter la mission avec diligence et dans les délais convenus.

**Article 5 — Clause de confidentialité**
Les parties s'engagent à préserver la confidentialité des informations échangées.

**Article 6 — Droit applicable**
Le présent contrat est soumis au droit ivoirien. Tout litige sera soumis aux tribunaux compétents d'Abidjan.

Fait à {{lieu_signature}}, le {{date_debut}}.

Signature Prestataire                    Signature Client""",
    },
    {
        'type_contrat': 'bail',
        'titre': 'Contrat de bail commercial standard',
        'description': 'Bail commercial pour locaux professionnels ou boutiques.',
        'contenu': """CONTRAT DE BAIL COMMERCIAL

Entre :

**LE BAILLEUR** : {{nom_prestataire}}, propriétaire des lieux sis à {{adresse_prestataire}},
**LE PRENEUR** : {{nom_client}}, domicilié à {{adresse_client}},

**Article 1 — Objet du bail**
{{objet}}

**Article 2 — Durée**
Bail de 3 ans renouvelable, prenant effet le {{date_debut}}.

**Article 3 — Loyer**
Loyer mensuel : {{montant}} {{devise}}, payable le 5 de chaque mois.

**Article 4 — Dépôt de garantie**
2 mois de loyer, soit {{montant}} x 2 {{devise}}.

**Article 5 — Destination des lieux**
Usage exclusivement commercial. Toute sous-location est interdite sans accord écrit.

**Article 6 — Résiliation**
Préavis de 3 mois par lettre recommandée.

Fait à {{lieu_signature}}, le {{date_debut}}.

Signature Bailleur                       Signature Preneur""",
    },
    {
        'type_contrat': 'travail',
        'titre': 'Contrat de travail CDI',
        'description': 'Contrat à Durée Indéterminée conforme au Code du Travail ivoirien.',
        'contenu': """CONTRAT DE TRAVAIL À DURÉE INDÉTERMINÉE

**L\'EMPLOYEUR** : {{nom_prestataire}}, {{adresse_prestataire}},
**L\'EMPLOYÉ** : {{nom_client}}, {{adresse_client}},

**Article 1 — Engagement**
M./Mme {{nom_client}} est engagé(e) en qualité de : {{objet}}.

**Article 2 — Date d\'entrée en fonctions**
Le {{date_debut}}.

**Article 3 — Rémunération**
Salaire brut mensuel : {{montant}} {{devise}}.
Cotisations CNPS : 5,2% à la charge du salarié.

**Article 4 — Durée du travail**
40 heures hebdomadaires, conformément au Code du Travail CI.

**Article 5 — Période d\'essai**
3 mois renouvelable une fois (cadres : 6 mois).

**Article 6 — Congés**
26 jours ouvrables par an après 12 mois de service.

**Article 7 — Résiliation**
Préavis selon ancienneté conformément à la Convention Collective Interprofessionnelle.

Fait à {{lieu_signature}}, le {{date_debut}}.

Signature Employeur                      Signature Employé""",
    },
    {
        'type_contrat': 'vente',
        'titre': 'Contrat de vente de marchandises',
        'description': 'Contrat de vente commerciale avec garanties et conditions de livraison.',
        'contenu': """CONTRAT DE VENTE

**LE VENDEUR** : {{nom_prestataire}}, {{adresse_prestataire}},
**L\'ACHETEUR** : {{nom_client}}, {{adresse_client}},

**Article 1 — Objet**
{{objet}}

**Article 2 — Prix**
Prix total : {{montant}} {{devise}} TTC (TVA 18% incluse).

**Article 3 — Modalités de paiement**
50% à la commande, 50% à la livraison.

**Article 4 — Livraison**
Au plus tard le {{date_fin}} au : {{adresse_client}}.

**Article 5 — Transfert de propriété**
La propriété est transférée à l\'acheteur après paiement intégral.

**Article 6 — Garantie**
Garantie légale de conformité de 6 mois.

Fait à {{lieu_signature}}, le {{date_debut}}.

Signature Vendeur                        Signature Acheteur""",
    },
    {
        'type_contrat': 'confidentialite',
        'titre': 'Accord de confidentialité (NDA)',
        'description': 'Non-Disclosure Agreement pour protéger les informations sensibles.',
        'contenu': """ACCORD DE CONFIDENTIALITÉ (NDA)

Entre :
- {{nom_prestataire}} (« Partie Divulgatrice »)
- {{nom_client}} (« Partie Réceptrice »)

**Article 1 — Informations confidentielles**
Toutes informations techniques, commerciales, financières échangées dans le cadre de : {{objet}}.

**Article 2 — Obligations**
La Partie Réceptrice s\'engage à :
- Ne pas divulguer les informations à des tiers
- Ne les utiliser qu\'aux fins convenues
- Protéger ces informations avec le même soin que ses propres secrets

**Article 3 — Durée**
Du {{date_debut}} au {{date_fin}} (3 ans après la fin des relations).

**Article 4 — Sanctions**
Toute violation expose la partie fautive à des dommages-intérêts.

Fait à {{lieu_signature}}, le {{date_debut}}.

Signatures des parties""",
    },
    {
        'type_contrat': 'partenariat',
        'titre': 'Convention de partenariat commercial',
        'description': 'Accord de partenariat entre deux entreprises pour une collaboration commerciale.',
        'contenu': """CONVENTION DE PARTENARIAT

Entre :
**PARTENAIRE A** : {{nom_prestataire}}, {{adresse_prestataire}},
**PARTENAIRE B** : {{nom_client}}, {{adresse_client}},

**Article 1 — Objet du partenariat**
{{objet}}

**Article 2 — Durée**
Du {{date_debut}} au {{date_fin}}, renouvelable par tacite reconduction.

**Article 3 — Apports respectifs**
Chaque partenaire apporte ses ressources, compétences et réseaux professionnels.

**Article 4 — Partage des bénéfices**
À définir par avenant selon les résultats obtenus.

**Article 5 — Comité de suivi**
Réunion mensuelle de suivi entre les partenaires.

**Article 6 — Non-concurrence**
Chaque partie s\'interdit de mener des activités concurrentes pendant la durée du partenariat.

Fait à {{lieu_signature}}, le {{date_debut}}.

Signatures""",
    },
]


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def jours_passes(n):
    return timezone.now() - timedelta(days=n)


def date_passee(n):
    return date.today() - timedelta(days=n)


def date_future(n):
    return date.today() + timedelta(days=n)


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de démonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime toutes les données existantes avant de recréer',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
            self._reset()

        self.stdout.write(self.style.MIGRATE_HEADING('═' * 55))
        self.stdout.write(self.style.MIGRATE_HEADING('  SEED DATA — Légal Connect'))
        self.stdout.write(self.style.MIGRATE_HEADING('═' * 55))

        experts = self._creer_experts()
        clients = self._creer_clients()
        self._creer_modeles_contrats()
        self._creer_contrats(clients, experts)
        self._creer_documents(clients, experts)
        self._creer_declarations(clients, experts)
        self._creer_echeances(clients)
        self._creer_dossiers(clients, experts)
        self._creer_avis(clients, experts)
        self._creer_notifications(clients, experts)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write(self.style.SUCCESS('  ✅  Seed terminé avec succès !'))
        self.stdout.write(self.style.SUCCESS('═' * 55))
        self.stdout.write('')
        self.stdout.write('  Comptes créés (mot de passe : Pass1234!) :')
        self.stdout.write(self.style.WARNING('  admin          → superadmin'))
        for e in EXPERTS:
            self.stdout.write(f"  {e['username']:<25} → expert")
        for c in CLIENTS:
            self.stdout.write(f"  {c['username']:<25} → client ({c['role']})")
        self.stdout.write('')

    # ── Reset ────────────────────────────────────────────────
    def _reset(self):
        from chatbot.models import ConversationChatbot, MessageChatbot
        Notification.objects.all().delete()
        AvisExpert.objects.all().delete()
        Message.objects.all().delete()
        Dossier.objects.all().delete()
        Declaration.objects.all().delete()
        Echeance.objects.all().delete()
        Document.objects.all().delete()
        Contrat.objects.all().delete()
        ModeleContrat.objects.all().delete()
        MessageChatbot.objects.all().delete()
        ConversationChatbot.objects.all().delete()
        Profil.objects.all().delete()
        User.objects.filter(username__in=[
            'admin',
            *[e['username'] for e in EXPERTS],
            *[c['username'] for c in CLIENTS],
        ]).delete()
        self.stdout.write(self.style.SUCCESS('  Données supprimées.'))

    # ── Experts ──────────────────────────────────────────────
    def _creer_experts(self):
        self.stdout.write('\n▶  Création des experts...')
        experts = []
        for data in EXPERTS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                    'is_active':  True,
                }
            )
            if created:
                user.set_password('Pass1234!')
                user.save()
            Profil.objects.update_or_create(
                utilisateur=user,
                defaults={
                    'role':       'expert',
                    'telephone':  data['telephone'],
                    'entreprise': data['entreprise'],
                    'specialite': data['specialite'],
                    'bio':        data['bio'],
                    'adresse':    'Abidjan, Côte d\'Ivoire',
                }
            )
            experts.append(user)
            self.stdout.write(f"    ✓ Expert : {user.get_full_name()}")
        return experts

    # ── Clients ──────────────────────────────────────────────
    def _creer_clients(self):
        self.stdout.write('\n▶  Création des clients...')
        # Superadmin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@legalconnect.ci', 'Pass1234!')
            Profil.objects.get_or_create(
                utilisateur=admin,
                defaults={'role': 'admin', 'entreprise': 'Légal Connect CI'}
            )
            self.stdout.write('    ✓ Superadmin : admin')

        clients = []
        for data in CLIENTS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                    'is_active':  True,
                }
            )
            if created:
                user.set_password('Pass1234!')
                user.save()
            Profil.objects.update_or_create(
                utilisateur=user,
                defaults={
                    'role':       data['role'],
                    'telephone':  data['telephone'],
                    'entreprise': data['entreprise'],
                    'adresse':    data['adresse'],
                }
            )
            clients.append(user)
            self.stdout.write(f"    ✓ Client : {user.get_full_name()} ({data['role']})")
        return clients

    # ── Modèles de contrats ──────────────────────────────────
    def _creer_modeles_contrats(self):
        self.stdout.write('\n▶  Création des modèles de contrats...')
        for m in MODELES_CONTRATS:
            obj, created = ModeleContrat.objects.get_or_create(
                titre=m['titre'],
                defaults={
                    'type_contrat': m['type_contrat'],
                    'description':  m['description'],
                    'contenu':      m['contenu'],
                    'actif':        True,
                }
            )
            if created:
                self.stdout.write(f"    ✓ Modèle : {obj.titre[:55]}")

    # ── Contrats ─────────────────────────────────────────────
    def _creer_contrats(self, clients, experts):
        self.stdout.write('\n▶  Création des contrats...')

        contrats_data = [
            {
                'proprietaire': clients[0],
                'expert': experts[0],
                'type_contrat': 'prestation',
                'titre': 'Prestation de développement site web — Digital Créa CI',
                'statut': 'signe',
                'nom_client': 'Boutique Konan & Fils',
                'email_client': 'marc.konan@gmail.com',
                'nom_prestataire': 'Digital Créa CI',
                'email_prestataire': 'samira.ouattara@yahoo.fr',
                'objet': 'Développement d\'un site e-commerce pour la boutique Konan & Fils avec intégration Wave/Orange Money.',
                'montant': Decimal('850000'),
                'date_debut': date_passee(90),
                'date_fin': date_passee(30),
                'lieu_signature': 'Cocody, Abidjan',
            },
            {
                'proprietaire': clients[1],
                'type_contrat': 'prestation',
                'titre': 'Création identité visuelle — Restaurant Saveur d\'Afrique',
                'statut': 'finalise',
                'nom_client': 'Restaurant Saveur d\'Afrique',
                'email_client': 'hawa.dia@gmail.com',
                'nom_prestataire': 'Digital Créa CI',
                'email_prestataire': 'samira.ouattara@yahoo.fr',
                'objet': 'Création du logo, charte graphique, cartes de visite et supports de communication.',
                'montant': Decimal('350000'),
                'date_debut': date_passee(15),
                'date_fin': date_future(30),
                'lieu_signature': 'Plateau, Abidjan',
            },
            {
                'proprietaire': clients[2],
                'expert': experts[3],
                'type_contrat': 'bail',
                'titre': 'Bail commercial — Entrepôt Treichville',
                'statut': 'signe',
                'nom_client': 'Import-Export Brou',
                'email_client': 'felix.brou@hotmail.com',
                'nom_prestataire': 'SCI Les Palmiers d\'Abidjan',
                'email_prestataire': 'palmiers@immo.ci',
                'objet': 'Location d\'un entrepôt de 500m² au marché de gros de Treichville pour activité d\'import-export.',
                'montant': Decimal('450000'),
                'date_debut': date_passee(180),
                'date_fin': date_future(900),
                'lieu_signature': 'Treichville, Abidjan',
            },
            {
                'proprietaire': clients[3],
                'type_contrat': 'prestation',
                'titre': 'Organisation événement d\'entreprise — Soro BTP',
                'statut': 'brouillon',
                'nom_client': 'Soro BTP & Construction',
                'email_client': 'ibrahim.soro@gmail.com',
                'nom_prestataire': 'Awa Events & Traiteur',
                'email_prestataire': 'awa.coulibaly@gmail.com',
                'objet': 'Organisation d\'un dîner de gala pour 120 personnes, cérémonie de remise de diplômes des employés.',
                'montant': Decimal('1200000'),
                'date_debut': date_future(15),
                'date_fin': date_future(16),
                'lieu_signature': 'Abidjan',
            },
            {
                'proprietaire': clients[4],
                'expert': experts[1],
                'type_contrat': 'prestation',
                'titre': 'Conseil fiscal annuel — Pharmacie N\'Guessan',
                'statut': 'signe',
                'nom_client': 'Pharmacie N\'Guessan',
                'email_client': 'paul.nguessan@gmail.com',
                'nom_prestataire': 'Cabinet Bamba Conseil Fiscal',
                'email_prestataire': 's.bamba@legalconnect.ci',
                'objet': 'Mission de conseil fiscal annuel : déclarations TVA mensuelles, IS annuel, audit préventif DGI.',
                'montant': Decimal('600000'),
                'date_debut': date_passee(120),
                'date_fin': date_future(245),
                'lieu_signature': 'Adjamé, Abidjan',
            },
            {
                'proprietaire': clients[5],
                'type_contrat': 'partenariat',
                'titre': 'Partenariat construction — AgriTech Tapé',
                'statut': 'finalise',
                'nom_client': 'AgriTech Tapé',
                'email_client': 'rodrigue.tape@outlook.com',
                'nom_prestataire': 'Soro BTP & Construction',
                'email_prestataire': 'ibrahim.soro@gmail.com',
                'objet': 'Construction de 3 entrepôts frigorifiques de 200m² chacun pour stockage de produits agricoles à Bouaké.',
                'montant': Decimal('12500000'),
                'date_debut': date_passee(30),
                'date_fin': date_future(150),
                'lieu_signature': 'Bouaké',
            },
            {
                'proprietaire': clients[6],
                'expert': experts[2],
                'type_contrat': 'travail',
                'titre': 'CDI — Coiffeuse senior Salon Mariam',
                'statut': 'signe',
                'nom_client': 'Ahou Christelle Deby',
                'email_client': 'christelle.deby@gmail.com',
                'nom_prestataire': 'Salon de Beauté Mariam',
                'email_prestataire': 'mariam.kone@gmail.com',
                'objet': 'Coiffeuse-styliste senior, responsable de la formation des apprenties.',
                'montant': Decimal('185000'),
                'date_debut': date_passee(60),
                'lieu_signature': 'Marcory, Abidjan',
            },
            {
                'proprietaire': clients[7],
                'type_contrat': 'vente',
                'titre': 'Vente matériel agricole — Coopérative Katiola',
                'statut': 'archive',
                'nom_client': 'Coopérative Agricole de Katiola',
                'email_client': 'coop.katiola@ci.org',
                'nom_prestataire': 'AgriTech Tapé',
                'email_prestataire': 'rodrigue.tape@outlook.com',
                'objet': 'Fourniture de 12 tracteurs légers, 50 kits d\'irrigation et formation technique des opérateurs.',
                'montant': Decimal('8750000'),
                'date_debut': date_passee(200),
                'date_fin': date_passee(140),
                'lieu_signature': 'Katiola',
            },
            {
                'proprietaire': clients[8],
                'type_contrat': 'bail',
                'titre': 'Bail local commercial — Restaurant Saveur d\'Afrique',
                'statut': 'signe',
                'nom_client': 'Restaurant Saveur d\'Afrique',
                'email_client': 'hawa.dia@gmail.com',
                'nom_prestataire': 'SCI Cocody Invest',
                'email_prestataire': 'cocody.invest@immo.ci',
                'objet': 'Location de la salle de restaurant 220m² + cuisine équipée 80m², 2 Plateaux Abidjan.',
                'montant': Decimal('380000'),
                'date_debut': date_passee(365),
                'date_fin': date_future(730),
                'lieu_signature': 'Cocody, Abidjan',
            },
            {
                'proprietaire': clients[9],
                'expert': experts[0],
                'type_contrat': 'confidentialite',
                'titre': 'NDA — Projet ERP SaaS Côte d\'Ivoire',
                'statut': 'signe',
                'nom_client': 'FinTech Solutions CI',
                'email_client': 'contact@fintechci.com',
                'nom_prestataire': 'Yao Consulting IT',
                'email_prestataire': 'celestin.yao@gmail.com',
                'objet': 'Protection des informations relatives au développement d\'une solution ERP SaaS destinée aux PME ivoiriennes.',
                'montant': None,
                'date_debut': date_passee(20),
                'date_fin': date_future(1095),
                'lieu_signature': 'Plateau, Abidjan',
            },
            {
                'proprietaire': clients[0],
                'type_contrat': 'prestation',
                'titre': 'Maintenance informatique mensuelle',
                'statut': 'brouillon',
                'nom_client': 'Boutique Konan & Fils',
                'email_client': 'marc.konan@gmail.com',
                'nom_prestataire': 'Yao Consulting IT',
                'email_prestataire': 'celestin.yao@gmail.com',
                'objet': 'Maintenance préventive et corrective du parc informatique, sauvegarde données, support utilisateur.',
                'montant': Decimal('75000'),
                'date_debut': date_future(10),
                'lieu_signature': 'Cocody, Abidjan',
            },
            {
                'proprietaire': clients[2],
                'type_contrat': 'prestation',
                'titre': 'Transport et logistique — Import Brou Q3',
                'statut': 'archive',
                'nom_client': 'Import-Export Brou',
                'email_client': 'felix.brou@hotmail.com',
                'nom_prestataire': 'Transit Rapid CI',
                'email_prestataire': 'transit.rapid@ci.com',
                'objet': 'Transport et dédouanement de marchandises en provenance de Chine via le Port d\'Abidjan.',
                'montant': Decimal('2100000'),
                'date_debut': date_passee(280),
                'date_fin': date_passee(220),
                'lieu_signature': 'Treichville, Abidjan',
            },
        ]

        for data in contrats_data:
            contrat, created = Contrat.objects.get_or_create(
                titre=data['titre'],
                proprietaire=data['proprietaire'],
                defaults={k: v for k, v in data.items() if k not in ('titre', 'proprietaire')}
            )
            if created:
                self.stdout.write(f"    ✓ {contrat.titre[:60]}")

    # ── Documents ────────────────────────────────────────────
    def _creer_documents(self, clients, experts):
        self.stdout.write('\n▶  Création des documents...')

        docs_data = [
            (clients[0], 'Registre de Commerce — Boutique Konan & Fils', 'registre', 'signe',
             'RCCM, registre, commerce, Konan', '2027-12-31'),
            (clients[0], 'Déclaration TVA Janvier 2026', 'declaration', 'archive',
             'TVA, déclaration, DGI', None),
            (clients[0], 'Facture fournisseur — Chine Import Mars 2026', 'facture', 'prive',
             'facture, import, fournisseur', None),
            (clients[1], 'Portfolio créations graphiques 2025', 'rapport', 'partage',
             'portfolio, graphisme, design', None),
            (clients[1], 'Devis client — Logo Pharmacie N\'Guessan', 'facture', 'prive',
             'devis, facture, logo', None),
            (clients[2], 'Titre foncier entrepôt Treichville', 'juridique', 'signe',
             'titre foncier, entrepôt, treichville', '2099-01-01'),
            (clients[2], 'Déclaration IS 2025 — Import-Export Brou', 'declaration', 'en_revision',
             'IS, impôt, sociétés', None),
            (clients[2], 'Assurance marchandises — Police 2026', 'assurance', 'prive',
             'assurance, marchandises, import', '2026-12-31'),
            (clients[3], 'Contrat de cession — Matériel cuisine', 'contrat', 'archive',
             'cession, cuisine, matériel', None),
            (clients[4], 'Autorisation d\'ouverture pharmacie — Ministère Santé', 'juridique', 'signe',
             'autorisation, pharmacie, ministère', '2028-06-30'),
            (clients[4], 'Registre de commerce — Pharmacie N\'Guessan', 'registre', 'prive',
             'RCCM, pharmacie, registre', '2027-09-15'),
            (clients[5], 'Permis de construire — Entrepôts Bouaké', 'juridique', 'signe',
             'permis, construire, Bouaké, BTP', '2026-12-01'),
            (clients[5], 'Devis travaux Phase 1', 'facture', 'partage',
             'devis, travaux, BTP', None),
            (clients[6], 'Extrait Kbis — Salon de Beauté Mariam', 'registre', 'prive',
             'Kbis, registre, salon beauté', '2027-11-30'),
            (clients[7], 'Rapport technique matériel agricole', 'rapport', 'archive',
             'rapport, agriculture, tracteur', None),
            (clients[8], 'Licence exploitation restauration 2026', 'juridique', 'signe',
             'licence, restaurant, mairie', '2026-12-31'),
            (clients[8], 'Déclaration CNPS employés 2026', 'declaration', 'soumise',
             'CNPS, employés, cotisation', None),
            (clients[9], 'Contrat licence logiciel ERP v2.0', 'contrat', 'signe',
             'licence, logiciel, ERP, SaaS', '2028-01-01'),
            (clients[9], 'Cahier des charges ERP — FinTech CI', 'rapport', 'partage',
             'cahier charges, ERP, fintech', None),
            (clients[9], 'Déclaration BNC 2025 — Yao Consulting', 'declaration', 'validee',
             'BNC, déclaration, consulting', None),
        ]

        tailles = [45000, 120000, 230000, 80000, 55000, 1200000, 340000,
                   900000, 67000, 2100000, 450000, 1500000, 320000, 78000,
                   210000, 190000, 88000, 560000, 740000, 95000]

        for i, (proprio, titre, cat, statut, mots, expiration) in enumerate(docs_data):
            ext = 'pdf' if cat in ('declaration', 'juridique', 'contrat', 'registre') else 'docx'
            chemin = f'documents/{proprio.id}/{titre[:30].replace(" ", "_").lower()}.{ext}'

            doc, created = Document.objects.get_or_create(
                titre=titre,
                proprietaire=proprio,
                defaults={
                    'categorie':        cat,
                    'statut':           statut,
                    'fichier':          chemin,
                    'taille':           tailles[i % len(tailles)],
                    'mots_cles':        mots,
                    'date_expiration':  expiration,
                    'nb_telechargements': random.randint(0, 25),
                }
            )
            if i < 5 and created:
                doc.experts_partage.set([experts[random.randint(0, len(experts)-1)]])
            if created:
                self.stdout.write(f"    ✓ {doc.titre[:55]}")

    # ── Déclarations fiscales ────────────────────────────────
    def _creer_declarations(self, clients, experts):
        self.stdout.write('\n▶  Création des déclarations fiscales...')

        decls = [
            # (client, type, periode, annee, mois, CA, charges, taux, montant, statut)
            (clients[0], 'tva',  'mensuel',    2026, 1,  None, 4200000, 0,    0,    18, 756000,  'validee'),
            (clients[0], 'tva',  'mensuel',    2026, 2,  None, 3800000, 0,    0,    18, 684000,  'validee'),
            (clients[0], 'tva',  'mensuel',    2026, 3,  None, 5100000, 0,    0,    18, 918000,  'soumise'),
            (clients[0], 'tva',  'mensuel',    2026, 4,  None, 4750000, 0,    0,    18, 855000,  'en_attente'),
            (clients[0], 'is',   'annuel',     2025, None, None, 32000000, 18000000, 14000000, 25, 3500000, 'validee'),
            (clients[2], 'tva',  'mensuel',    2026, 1,  None, 8500000, 0,    0,    18, 1530000, 'validee'),
            (clients[2], 'tva',  'mensuel',    2026, 2,  None, 7200000, 0,    0,    18, 1296000, 'validee'),
            (clients[2], 'is',   'annuel',     2025, None, None, 95000000, 65000000, 30000000, 20, 6000000, 'en_revision'),
            (clients[2], 'cnps', 'trimestriel', 2026, None, 1,  2100000, 0,    0,   23.2, 487200, 'validee'),
            (clients[4], 'tva',  'mensuel',    2026, 1,  None, 12000000, 0,   0,    18, 2160000, 'validee'),
            (clients[4], 'tva',  'mensuel',    2026, 2,  None, 11500000, 0,   0,    18, 2070000, 'soumise'),
            (clients[4], 'cnps', 'mensuel',    2026, 1,  None, 3500000, 0,    0,   23.2, 812000, 'validee'),
            (clients[7], 'bnc',  'annuel',     2025, None, None, 18000000, 6000000, 12000000, 20, 2400000, 'validee'),
            (clients[8], 'tva',  'mensuel',    2026, 1,  None, 4800000, 0,    0,    18, 864000, 'validee'),
            (clients[8], 'tva',  'mensuel',    2026, 2,  None, 5200000, 0,    0,    18, 936000, 'en_retard'),
            (clients[8], 'cnps', 'mensuel',    2026, 1,  None, 1800000, 0,    0,   23.2, 417600, 'soumise'),
            (clients[9], 'bnc',  'annuel',     2025, None, None, 24000000, 8000000, 16000000, 20, 3200000, 'validee'),
            (clients[9], 'tva',  'mensuel',    2026, 1,  None, 6500000, 0,    0,    18, 1170000, 'en_attente'),
        ]

        for row in decls:
            client, type_i, periode, annee, mois, tri, ca, charges, benef, taux, montant, statut = row
            Declaration.objects.get_or_create(
                utilisateur=client,
                type_impot=type_i,
                annee=annee,
                mois=mois,
                trimestre=tri,
                defaults={
                    'periode':          periode,
                    'chiffre_affaires': ca if ca else 0,
                    'charges':          charges,
                    'benefice_net':     benef,
                    'taux_applique':    taux,
                    'montant_impot':    montant,
                    'statut':           statut,
                    'expert':           experts[1] if statut == 'en_revision' else None,
                    'soumise_a_expert': statut == 'en_revision',
                }
            )
        self.stdout.write(f"    ✓ {len(decls)} déclarations fiscales créées")

    # ── Échéances fiscales ───────────────────────────────────
    def _creer_echeances(self, clients):
        self.stdout.write('\n▶  Création des échéances fiscales...')

        ech = [
            (clients[0], 'Déclaration TVA Mai 2026', 'tva', date_future(14), 855000, 'a_faire'),
            (clients[0], 'Acompte IS Q2 2026', 'is', date_future(30), 875000, 'a_faire'),
            (clients[2], 'Déclaration TVA Mai 2026', 'tva', date_future(14), 1300000, 'a_faire'),
            (clients[2], 'CNPS Q2 2026 (salarié)', 'cnps', date_future(20), 520000, 'a_faire'),
            (clients[4], 'TVA Mai 2026 — Pharmacie', 'tva', date_future(14), 2200000, 'a_faire'),
            (clients[4], 'CNPS Juin 2026', 'cnps', date_future(45), 850000, 'a_faire'),
            (clients[5], 'Patente 2026 — Soro BTP', 'patente', date_future(60), 450000, 'a_faire'),
            (clients[8], 'TVA Mai 2026 — Restaurant', 'tva', date_future(5), 950000, 'a_faire'),
            (clients[8], 'CNPS Mai 2026', 'cnps', date_future(8), 430000, 'a_faire'),
            (clients[9], 'BNC Acompte Q2 2026', 'bnc', date_future(25), 800000, 'a_faire'),
            # Passées
            (clients[0], 'TVA Avril 2026', 'tva', date_passee(15), 855000, 'fait'),
            (clients[2], 'CNPS Q1 2026', 'cnps', date_passee(30), 487200, 'fait'),
            (clients[4], 'TVA Avril 2026', 'tva', date_passee(15), 2070000, 'fait'),
            (clients[8], 'TVA Avril 2026', 'tva', date_passee(15), 936000, 'en_retard'),
        ]

        for client, titre, type_i, dl, montant, statut in ech:
            Echeance.objects.get_or_create(
                utilisateur=client,
                titre=titre,
                defaults={
                    'type_impot': type_i,
                    'date_limite': dl,
                    'montant': montant,
                    'statut': statut,
                }
            )
        self.stdout.write(f"    ✓ {len(ech)} échéances fiscales créées")

    # ── Dossiers de collaboration ────────────────────────────
    def _creer_dossiers(self, clients, experts):
        self.stdout.write('\n▶  Création des dossiers de collaboration...')

        dossiers_data = [
            {
                'client': clients[0],
                'expert': experts[0],
                'titre': 'Révision contrat de prestation — litige retard livraison',
                'description': 'Mon prestataire web a pris 3 mois de retard sur la livraison du site. Je veux savoir si je peux appliquer les pénalités prévues au contrat et comment procéder.',
                'type_dossier': 'contrat',
                'statut': 'en_cours',
                'priorite': 'haute',
                'note_expert': '',
                'messages_content': [
                    ('client', 'Bonjour Maître, voici le contrat en question. Le site devait être livré le 15 mars, nous sommes au 30 juin et il n\'est toujours pas opérationnel.'),
                    ('expert', 'Bonjour M. Konan. J\'ai bien reçu le dossier. L\'article 3 de votre contrat prévoit effectivement des pénalités de retard à 0,5% par semaine. Pouvez-vous me transmettre les échanges email avec le prestataire pour documenter le retard ?'),
                    ('client', 'Je vous envoie tous les emails en pièce jointe. Total du retard : 15 semaines.'),
                    ('expert', 'Excellent. 15 semaines × 0,5% × 850 000 FCFA = 63 750 FCFA de pénalités contractuelles. Je prépare une mise en demeure formelle. Voulez-vous aussi explorer la résolution du contrat ?'),
                ],
            },
            {
                'client': clients[1],
                'expert': experts[1],
                'titre': 'Conseil TVA — Activité de prestation graphique',
                'description': 'Je viens de dépasser le seuil d\'assujettissement à la TVA. J\'ai besoin d\'aide pour me conformer et comprendre mes obligations.',
                'type_dossier': 'fiscal',
                'statut': 'valide',
                'priorite': 'normale',
                'note_expert': 'Dossier traité avec succès. Client immatriculée à la TVA (NIF: 2025-A-123456). Première déclaration à faire avant le 15 juillet 2026.',
                'messages_content': [
                    ('client', 'Bonjour Dr Bamba, mon CA a dépassé 50 millions FCFA cette année. On m\'a dit que je dois m\'assujettir à la TVA. Comment faire ?'),
                    ('expert', 'Bonjour Mme Ouattara ! Oui, effectivement au-delà de 50M FCFA de CA, vous êtes obligatoirement assujettie à la TVA au taux de 18%. Il faut vous immatriculer à la DGI.'),
                    ('client', 'Quelles sont les pièces à fournir ?'),
                    ('expert', 'Voici la liste : CNI/Passeport, extrait RCCM, déclaration d\'existence, formulaire DGI. Je vous accompagne dans la démarche. RDV possible mardi matin ?'),
                    ('client', 'Parfait, mardi 10h ça me convient. Merci beaucoup !'),
                    ('expert', 'C\'est confirmé. Je prépare votre dossier d\'immatriculation pour mardi.'),
                ],
            },
            {
                'client': clients[4],
                'expert': experts[2],
                'titre': 'Licenciement employé — Procédure légale',
                'description': 'Un de mes pharmaciens a commis des erreurs répétées de dispensation. Je souhaite procéder à un licenciement pour faute mais veux m\'assurer de respecter la procédure.',
                'type_dossier': 'juridique',
                'statut': 'en_cours',
                'priorite': 'urgente',
                'note_expert': '',
                'messages_content': [
                    ('client', 'Maître Traoré, j\'ai un pharmacien qui a fait 3 erreurs de dispensation en 2 mois, dont une qui a mis un client en danger. Je veux le licencier.'),
                    ('expert', 'M. N\'Guessan, pour un licenciement pour faute grave, la procédure est stricte : 1) Lettre de mise à pied conservatoire immédiate, 2) Convocation à entretien préalable (5 jours ouvrables), 3) Notification du licenciement.'),
                    ('client', 'Il est déjà mis à pied depuis lundi. L\'entretien est prévu jeudi.'),
                    ('expert', 'Parfait. Pour l\'entretien, rédigez précisément les 3 fautes avec dates et témoins. Voulez-vous que je sois présente comme conseil lors de l\'entretien ?'),
                    ('client', 'Oui, ce serait vraiment utile. Comment procéder ?'),
                ],
            },
            {
                'client': clients[7],
                'expert': experts[1],
                'titre': 'Optimisation fiscale — BNC et structuration société',
                'description': 'Mes revenus de consulting augmentent. Est-il plus avantageux de rester en BNC ou de créer une société soumise à l\'IS ?',
                'type_dossier': 'fiscal',
                'statut': 'valide',
                'priorite': 'normale',
                'note_expert': 'Recommandation : Création d\'une SARL recommandée à partir de 30M FCFA de CA annuel. IS à 20% plus avantageux que BNC à 20% avec la possibilité de déduire plus de charges. Accompagnement CEPICI proposé.',
                'messages_content': [
                    ('client', 'Bonjour, je suis consultant IT avec 18M FCFA de CA en 2025. Vaut-il mieux rester en BNC ou créer une SARL ?'),
                    ('expert', 'Bonne question ! En BNC : 20% sur bénéfice net. En SARL (IS) : 20% pour CA < 500M, mais avec plus de charges déductibles. À votre niveau, la différence est faible. Je vous prépare une simulation comparative.'),
                    ('client', 'Voici mes charges détaillées. Simulation reçue — très claire. Donc je reste en BNC pour l\'instant ?'),
                    ('expert', 'Oui, en dessous de 30M FCFA, la BNC reste optimale. Si vous dépassez ce seuil en 2026, on revisite la question. Je vous prépare une note de synthèse.'),
                ],
            },
            {
                'client': clients[5],
                'expert': experts[4],
                'titre': 'Titre foncier — Terrain Bouaké acquisition',
                'description': 'Je veux acquérir un terrain de 2 hectares à Bouaké pour construire un dépôt agricole. Le vendeur présente un titre foncier mais je veux vérifier son authenticité.',
                'type_dossier': 'juridique',
                'statut': 'en_attente',
                'priorite': 'haute',
                'note_expert': '',
                'messages_content': [
                    ('client', 'Bonjour Me Diallo, j\'ai trouvé un terrain à Bouaké pour mon projet agricole. Le vendeur dit avoir le TF. Comment vérifier ?'),
                    ('expert', 'Bonjour M. Soro. Pour vérifier un titre foncier, il faut : 1) Demander copie du TF au Conservation Foncière de Bouaké, 2) Vérifier qu\'il n\'y a pas d\'hypothèque ou servitude, 3) Contrôler l\'identité du vrai propriétaire.'),
                    ('client', 'Je vous envoie la copie du TF que le vendeur m\'a remise.'),
                    ('expert', 'Document reçu. Je vais effectuer les vérifications à la Conservation Foncière. Je reviendrai vers vous dans 3 jours.'),
                ],
            },
            {
                'client': clients[9],
                'expert': experts[0],
                'titre': 'NDA — Négociation termes accord de confidentialité',
                'description': 'Je dois signer un NDA avec un client important. Je veux qu\'un expert vérifie les clauses avant signature, notamment la durée et les exclusions.',
                'type_dossier': 'contrat',
                'statut': 'valide',
                'priorite': 'normale',
                'note_expert': 'NDA relu et validé. Deux modifications suggérées : 1) Réduire la clause de non-concurrence de 5 ans à 2 ans, 2) Exclure les informations déjà publiques. Client a accepté les modifications. Document final signé.',
                'messages_content': [
                    ('client', 'Maître Assi, voici le NDA proposé par FinTech Solutions. La durée de confidentialité est de 5 ans — est-ce normal ?'),
                    ('expert', 'M. Yao, 5 ans est effectivement long pour un NDA standard. En Côte d\'Ivoire, 2-3 ans est la norme. J\'ai également noté l\'absence de clause d\'exclusion pour les informations déjà publiques — c\'est risqué pour vous.'),
                    ('client', 'Quelles modifications recommandez-vous ?'),
                    ('expert', 'Je vous prépare un avenant avec : durée réduite à 2 ans, clause d\'exclusion information publique, et plafond de responsabilité. Je vous envoie ça dans 24h.'),
                    ('client', 'Parfait. Le client a accepté les modifications. On peut signer.'),
                    ('expert', 'Excellent ! NDA finalisé. Conservez bien l\'original signé. Mission clôturée avec succès.'),
                ],
            },
        ]

        for ddata in dossiers_data:
            dossier, created = Dossier.objects.get_or_create(
                titre=ddata['titre'],
                client=ddata['client'],
                defaults={
                    'expert':       ddata['expert'],
                    'description':  ddata['description'],
                    'type_dossier': ddata['type_dossier'],
                    'statut':       ddata['statut'],
                    'priorite':     ddata['priorite'],
                    'note_expert':  ddata['note_expert'],
                }
            )
            if created:
                for role, contenu in ddata['messages_content']:
                    auteur = ddata['client'] if role == 'client' else ddata['expert']
                    Message.objects.create(
                        dossier=dossier,
                        auteur=auteur,
                        contenu=contenu,
                        lu=True,
                    )
                self.stdout.write(f"    ✓ Dossier : {dossier.titre[:55]}")

    # ── Avis experts ─────────────────────────────────────────
    def _creer_avis(self, clients, experts):
        self.stdout.write('\n▶  Création des avis experts...')

        avis_data = [
            (experts[0], clients[0], 5, 'Maître Assi est exceptionnel ! Il a réglé mon litige en 2 semaines. Très professionnel et à l\'écoute.'),
            (experts[0], clients[9], 5, 'Excellent conseil juridique pour notre NDA. Rapide, précis, abordable. Je recommande vivement.'),
            (experts[0], clients[2], 4, 'Très compétent en droit commercial. Quelques délais de réponse longs mais le résultat est là.'),
            (experts[1], clients[1], 5, 'Dr Bamba m\'a sauvé d\'une situation compliquée avec la DGI. Il connaît parfaitement la fiscalité ivoirienne.'),
            (experts[1], clients[4], 5, 'Accompagnement fiscal complet et rassurant. On voit qu\'il maîtrise son sujet. Je lui confie ma comptabilité chaque année.'),
            (experts[1], clients[7], 4, 'Très bon conseil pour l\'optimisation BNC. Pédagogique et disponible. Recommandé.'),
            (experts[2], clients[4], 5, 'Maître Traoré a géré le licenciement de façon irréprochable. Tout s\'est passé sans litige. Bravo !'),
            (experts[2], clients[6], 4, 'Bons conseils en droit du travail. Elle défend vraiment les intérêts de son client.'),
            (experts[3], clients[2], 5, 'M. Assoumou a redressé notre comptabilité en 3 mois. Excellent auditeur, très rigoureux.'),
            (experts[4], clients[5], 4, 'Me Diallo a bien vérifié le titre foncier. Travail sérieux, bon suivi. Je la recommande pour les transactions immobilières.'),
        ]

        for expert, client, note, commentaire in avis_data:
            AvisExpert.objects.get_or_create(
                expert=expert,
                auteur=client,
                defaults={'note': note, 'commentaire': commentaire, 'valide': True}
            )
        self.stdout.write(f"    ✓ {len(avis_data)} avis déposés")

    # ── Notifications ────────────────────────────────────────
    def _creer_notifications(self, clients, experts):
        self.stdout.write('\n▶  Création des notifications...')

        notifs = [
            (clients[0], 'nouveau_message',     'Nouveau message de Maître Assi',
             'Maître Assi a répondu à votre dossier sur le litige de prestation.',
             '/collaboration/', False),
            (clients[0], 'echeance_7j',         'Échéance TVA dans 14 jours',
             'Votre déclaration TVA Mai 2026 est à soumettre avant le 15 juillet.',
             '/fiscalite/', False),
            (clients[0], 'contrat_genere',      'Contrat signé — Prestation Digital Créa',
             'Votre contrat de prestation avec Digital Créa CI est signé.',
             '/contrats/', True),
            (clients[1], 'dossier_valide',      'Dossier fiscal clôturé avec succès',
             'Dr Bamba a clôturé votre dossier TVA. Vous êtes maintenant immatriculée.',
             '/collaboration/', False),
            (clients[1], 'document_partage',    'Document partagé avec un expert',
             'Votre portfolio a été partagé avec Me Traoré.',
             '/documents/', True),
            (clients[2], 'echeance_depassee',   'Déclaration TVA Février 2026 en retard !',
             'Votre déclaration TVA de février est en retard. Des pénalités peuvent s\'appliquer.',
             '/fiscalite/', False),
            (clients[4], 'nouveau_dossier',     'Dossier reçu par Maître Traoré',
             'Votre dossier de licenciement a été pris en charge par Maître Traoré.',
             '/collaboration/', True),
            (clients[4], 'echeance_7j',         'TVA Mai 2026 — 14 jours',
             'Pensez à préparer votre déclaration TVA mensuelle.',
             '/fiscalite/', False),
            (clients[8], 'echeance_1j',         '⚠️ TVA Mai 2026 dans 5 jours !',
             'Urgence : votre déclaration TVA Mai doit être soumise avant le 15 juillet.',
             '/fiscalite/', False),
            (clients[9], 'dossier_valide',      'NDA validé — Mission terminée',
             'Maître Assi a finalisé la révision de votre NDA. Document prêt à signer.',
             '/collaboration/', True),
            (experts[0], 'nouveau_dossier',     'Nouveau dossier reçu de Marc Konan',
             'M. Konan a soumis un dossier sur un litige de prestation de services.',
             '/collaboration/', False),
            (experts[1], 'nouveau_dossier',     'Nouvelle mission fiscale — N\'Guessan',
             'La Pharmacie N\'Guessan vous a assigné une déclaration IS à réviser.',
             '/collaboration/', False),
            (experts[2], 'nouveau_dossier',     'Dossier urgent — Licenciement Pharmacie',
             'Nouveau dossier priorité URGENTE de la Pharmacie N\'Guessan.',
             '/collaboration/', False),
        ]

        for user, type_n, titre, msg, lien, lu in notifs:
            Notification.objects.get_or_create(
                destinataire=user,
                titre=titre,
                defaults={
                    'type_notif': type_n,
                    'message':    msg,
                    'lien':       lien,
                    'lu':         lu,
                }
            )
        self.stdout.write(f"    ✓ {len(notifs)} notifications créées")
