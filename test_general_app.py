"""
Suite de non-regression de l'application Legal Connect (multi-apps).

Execution : python manage.py test test_general_app -v 2 --noinput
Utilise la base de test Django (creee/detruite automatiquement),
ne touche jamais la vraie base de dev.
"""
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from unittest.mock import patch

from accounts.models import Profil
from abonnements.models import Abonnement, Paiement, Plan
from collaboration.models import Dossier
from contrats.models import Contrat, ModeleContrat


class TestGeneralApplication(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.commercant = User.objects.create_user('test_commercant', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.commercant, role='commercant')

        cls.expert = User.objects.create_user('test_expert', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.expert, role='expert', specialite='droit_travail')

        cls.admin_user = User.objects.create_superuser('test_admin', 'admin@test.local', 'TestPass123!')
        Profil.objects.create(utilisateur=cls.admin_user, role='admin')

    def setUp(self):
        self.client = Client()

    # ---------- Pages publiques (anonyme) ----------

    def test_pages_publiques(self):
        pour_tester = {
            'landing': '/',
            'accounts:login': '/accounts/login/',
            'accounts:inscription': '/accounts/inscription/',
        }
        for nom, url in pour_tester.items():
            r = self.client.get(url)
            self.assertIn(r.status_code, (200, 302), f"{nom} ({url}) -> {r.status_code}")

    def test_pages_protegees_redirigent_si_anonyme(self):
        urls_protegees = [
            '/dashboard/', '/contrats/', '/documents/', '/fiscalite/',
            '/collaboration/', '/notifications/', '/chatbot/', '/recommandation/',
        ]
        for url in urls_protegees:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, f"{url} devrait rediriger (anonyme) -> {r.status_code}")

    # ---------- Connexion ----------

    def test_connexion_commercant(self):
        ok = self.client.login(username='test_commercant', password='TestPass123!')
        self.assertTrue(ok, "La connexion a echoue")

    # ---------- Pages authentifiees, par app ----------

    def test_pages_authentifiees_commercant(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        urls = [
            '/dashboard/', '/contrats/', '/documents/', '/fiscalite/',
            '/collaboration/', '/notifications/', '/annuaire/',
            '/recommandation/', '/chatbot/', '/accounts/profil/',
        ]
        for url in urls:
            r = self.client.get(url)
            self.assertIn(r.status_code, (200, 302), f"{url} -> {r.status_code}")
            if r.status_code == 200:
                self.assertGreater(len(r.content), 200, f"{url} : page suspicieusement vide")

    def test_admin_users_reserve_aux_admins(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        r = self.client.get('/accounts/admin/users/')
        self.assertIn(r.status_code, (302, 403), f"Un commercant ne devrait pas acceder a admin_users -> {r.status_code}")

        self.client.logout()
        self.client.login(username='test_admin', password='TestPass123!')
        r = self.client.get('/accounts/admin/users/')
        self.assertEqual(r.status_code, 200, f"Un admin devrait acceder a admin_users -> {r.status_code}")

    # ---------- Django admin ----------

    def test_django_admin(self):
        self.client.login(username='test_admin', password='TestPass123!')
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 200)

    # ---------- Chatbot end-to-end ----------

    def test_chatbot_ajax(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        r = self.client.post(
            '/chatbot/ajax/',
            data='{"message": "Mon employeur ne me paie pas mon salaire depuis 2 mois", "session_id": "test-session-1"}',
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200, r.content)
        data = r.json()
        for cle in ('reponse', 'escalade', 'suggestions', 'mode', 'session_id'):
            self.assertIn(cle, data, f"Cle manquante dans la reponse chatbot : {cle}")
        self.assertGreater(len(data['reponse']), 10)

    def test_chatbot_message_vide_rejete(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        r = self.client.post(
            '/chatbot/ajax/', data='{"message": "", "session_id": "s"}',
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 400)

    # ---------- Recommandation end-to-end ----------

    def test_recommandation_ajax(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        r = self.client.post(
            '/recommandation/ajax/',
            data='{"texte": "Mon associe a detourne les fonds de notre societe"}',
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200, r.content)
        data = r.json()
        self.assertIn('experts', data, f"Cle 'experts' manquante : {data}")

    # ---------- Annuaire ----------

    def test_annuaire_liste_experts(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        r = self.client.get('/annuaire/')
        self.assertEqual(r.status_code, 200)

    # ---------- API REST ----------

    def test_api_token_obtain(self):
        r = self.client.post('/api/token/', data={'username': 'test_commercant', 'password': 'TestPass123!'})
        self.assertEqual(r.status_code, 200, r.content)
        self.assertIn('access', r.json())
        self.assertIn('refresh', r.json())

    def test_api_experts_authentifie(self):
        token_resp = self.client.post('/api/token/', data={'username': 'test_commercant', 'password': 'TestPass123!'})
        access = token_resp.json()['access']
        r = self.client.get('/api/experts/', HTTP_AUTHORIZATION=f'Bearer {access}')
        self.assertEqual(r.status_code, 200, r.content)

    def test_api_schema_et_docs(self):
        r = self.client.get('/api/schema/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/docs/')
        self.assertEqual(r.status_code, 200)

    # ---------- Fiscalite : calculateur ----------

    def test_fiscalite_calculateur(self):
        self.client.login(username='test_commercant', password='TestPass123!')
        r = self.client.get('/fiscalite/calculateur/')
        self.assertEqual(r.status_code, 200)


class TestWorkflowContrats(TestCase):
    """Cycle de vie complet d'un contrat : creation depuis un modele -> detail
    -> modification -> finalisation -> export PDF -> suppression."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_contrats', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.user, role='commercant')
        cls.modele = ModeleContrat.objects.create(
            type_contrat='prestation',
            titre='Modele prestation standard',
            description='Modele de test',
            contenu='Entre {{nom_prestataire}} et {{nom_client}}, il est convenu ce qui suit : {{objet}}.',
            actif=True,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_contrats', password='TestPass123!')

    def test_choisir_modele_liste(self):
        r = self.client.get('/contrats/nouveau/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Modele prestation standard')

    def test_cycle_de_vie_contrat(self):
        # Creation
        r = self.client.post(f'/contrats/nouveau/{self.modele.pk}/', data={
            'titre': 'Contrat de test E2E',
            'nom_client': 'Client Test SARL',
            'nom_prestataire': 'Prestataire Test',
            'objet': "Prestation de conseil juridique pour le mois d'avril",
            'devise': 'FCFA',
        })
        self.assertEqual(r.status_code, 302, r.context['form'].errors if r.status_code == 200 else None)

        contrat = self.user.contrats.get(titre='Contrat de test E2E')
        self.assertEqual(contrat.statut, 'brouillon')
        self.assertIn('Client Test SARL', contrat.contenu_final)

        # Detail
        r = self.client.get(f'/contrats/{contrat.pk}/')
        self.assertEqual(r.status_code, 200)

        # Modification
        r = self.client.post(f'/contrats/{contrat.pk}/modifier/', data={
            'titre': 'Contrat de test E2E (modifie)',
            'nom_client': 'Client Test SARL',
            'nom_prestataire': 'Prestataire Test',
            'objet': "Prestation modifiee",
            'devise': 'FCFA',
        })
        self.assertEqual(r.status_code, 302)
        contrat.refresh_from_db()
        self.assertEqual(contrat.titre, 'Contrat de test E2E (modifie)')

        # Finalisation
        r = self.client.get(f'/contrats/{contrat.pk}/finaliser/')
        self.assertEqual(r.status_code, 302)
        contrat.refresh_from_db()
        self.assertEqual(contrat.statut, 'finalise')

        # Export PDF (reportlab, pas weasyprint)
        r = self.client.get(f'/contrats/{contrat.pk}/pdf/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        self.assertGreater(len(r.content), 500, "Le PDF genere semble vide")

        # Suppression
        r = self.client.post(f'/contrats/{contrat.pk}/supprimer/')
        self.assertEqual(r.status_code, 302)
        self.assertFalse(self.user.contrats.filter(pk=contrat.pk).exists())


class TestWorkflowDocuments(TestCase):
    """Cycle de vie complet d'un document : upload -> detail -> commentaire
    -> archivage -> desarchivage -> telechargement -> suppression."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_documents', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.user, role='commercant')

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_documents', password='TestPass123!')

    def _fichier_test(self, nom='piece.pdf'):
        return SimpleUploadedFile(nom, b'%PDF-1.4 contenu de test', content_type='application/pdf')

    def test_cycle_de_vie_document(self):
        # Upload
        r = self.client.post('/documents/upload/', data={
            'titre': 'Piece de test',
            'categorie': 'juridique',
            'statut': 'prive',
            'description': 'Un document de test',
            'fichier': self._fichier_test(),
        })
        self.assertEqual(r.status_code, 302, r.context['form'].errors if r.status_code == 200 else None)

        doc = self.user.documents.get(titre='Piece de test')
        self.assertGreater(doc.taille, 0)

        # Detail
        r = self.client.get(f'/documents/{doc.pk}/')
        self.assertEqual(r.status_code, 200)

        # Commentaire
        r = self.client.post(f'/documents/{doc.pk}/commenter/', data={'texte': 'Un commentaire de test'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(doc.commentaires.count(), 1)

        # Telechargement (on consomme le flux pour liberer le verrou sur le
        # fichier, sinon la suppression qui suit peut echouer sous Windows)
        r = self.client.get(f'/documents/{doc.pk}/telecharger/')
        self.assertEqual(r.status_code, 200)
        b''.join(r.streaming_content)

        # Archivage / desarchivage
        r = self.client.post(f'/documents/{doc.pk}/archiver/')
        self.assertEqual(r.status_code, 302)
        doc.refresh_from_db()
        self.assertEqual(doc.statut, 'archive')

        r = self.client.post(f'/documents/{doc.pk}/desarchiver/')
        self.assertEqual(r.status_code, 302)
        doc.refresh_from_db()
        self.assertEqual(doc.statut, 'prive')

        # Suppression (nettoie aussi le fichier physique)
        r = self.client.post(f'/documents/{doc.pk}/supprimer/')
        self.assertEqual(r.status_code, 302)
        self.assertFalse(self.user.documents.filter(pk=doc.pk).exists())


class TestWorkflowCollaboration(TestCase):
    """Cycle de vie complet d'un dossier : creation par un client -> message
    -> assignation par un admin -> validation par l'expert -> archivage."""

    @classmethod
    def setUpTestData(cls):
        cls.client_user = User.objects.create_user('test_client_dossier', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.client_user, role='commercant')

        cls.expert = User.objects.create_user('test_expert_dossier', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.expert, role='expert', specialite='droit_travail')

        cls.admin_user = User.objects.create_superuser('test_admin_dossier', 'a@test.local', 'TestPass123!')
        Profil.objects.create(utilisateur=cls.admin_user, role='admin')

    def setUp(self):
        self.client = Client()

    def test_cycle_de_vie_dossier(self):
        # Creation par le client
        self.client.login(username='test_client_dossier', password='TestPass123!')
        r = self.client.post('/collaboration/creer/', data={
            'titre': 'Dossier de test E2E',
            'description': 'Verification de conformite',
            'type_dossier': 'juridique',
            'priorite': 'normale',
        })
        self.assertEqual(r.status_code, 302, r.content)

        dossier = Dossier.objects.get(titre='Dossier de test E2E')
        self.assertEqual(dossier.statut, 'en_attente')
        self.assertEqual(dossier.client, self.client_user)

        # Detail (par le client)
        r = self.client.get(f'/collaboration/{dossier.pk}/')
        self.assertEqual(r.status_code, 200)

        # Message du client
        r = self.client.post(f'/collaboration/{dossier.pk}/message/', data={'contenu': 'Bonjour, voici mon dossier.'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(dossier.nb_messages, 1)

        # Assignation par l'admin
        self.client.logout()
        self.client.login(username='test_admin_dossier', password='TestPass123!')
        r = self.client.post(f'/collaboration/{dossier.pk}/assigner/', data={'expert_id': self.expert.pk})
        self.assertEqual(r.status_code, 302)
        dossier.refresh_from_db()
        self.assertEqual(dossier.expert, self.expert)
        self.assertEqual(dossier.statut, 'en_cours')

        # Validation par l'expert
        self.client.logout()
        self.client.login(username='test_expert_dossier', password='TestPass123!')
        r = self.client.post(f'/collaboration/{dossier.pk}/valider/', data={
            'action': 'valider',
            'note_expert': 'Dossier conforme.',
        })
        self.assertEqual(r.status_code, 302)
        dossier.refresh_from_db()
        self.assertEqual(dossier.statut, 'valide')
        self.assertEqual(dossier.note_expert, 'Dossier conforme.')

        # Archivage par le client
        self.client.logout()
        self.client.login(username='test_client_dossier', password='TestPass123!')
        r = self.client.post(f'/collaboration/{dossier.pk}/archiver/')
        self.assertEqual(r.status_code, 302)
        dossier.refresh_from_db()
        self.assertEqual(dossier.statut, 'archive')


class TestAbonnements(TestCase):
    """Souscription, activation, webhook de paiement, et limites d'usage."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_abo', password='TestPass123!')
        Profil.objects.create(utilisateur=cls.user, role='commercant')

        cls.plan_gratuit = Plan.objects.create(
            nom='Gratuit', role_cible='commercant', prix=0, periode_jours=30,
            max_contrats_mois=1, max_dossiers_mois=2, max_messages_chatbot_mois=20,
        )
        cls.plan_pro = Plan.objects.create(
            nom='Pro', role_cible='commercant', prix=5000, periode_jours=30,
        )
        # Plan d'un autre role : ne doit pas apparaitre pour un commercant
        cls.plan_expert = Plan.objects.create(
            nom='Premium', role_cible='expert', prix=10000, periode_jours=30,
            mise_en_avant_annuaire=True,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='test_abo', password='TestPass123!')

    def test_liste_plans_filtree_par_role(self):
        r = self.client.get('/abonnements/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Gratuit')
        self.assertContains(r, 'Pro')
        self.assertNotContains(r, 'Premium')

    def test_souscription_plan_gratuit_active_immediatement(self):
        r = self.client.post(f'/abonnements/souscrire/{self.plan_gratuit.pk}/')
        self.assertEqual(r.status_code, 302)
        abo = Abonnement.objects.get(utilisateur=self.user, plan=self.plan_gratuit)
        self.assertTrue(abo.est_actif)
        self.assertEqual(abo.paiements.count(), 0)

    def test_souscription_plan_payant_mode_manuel_sans_cles_cinetpay(self):
        # CINETPAY_API_KEY/SITE_ID vides par defaut en test => mode manuel
        r = self.client.post(f'/abonnements/souscrire/{self.plan_pro.pk}/', data={
            'moyen_paiement': 'orange_money',
            'numero_telephone': '0701020304',
        })
        self.assertEqual(r.status_code, 302)
        abo = Abonnement.objects.get(utilisateur=self.user, plan=self.plan_pro)
        self.assertEqual(abo.statut, 'en_attente_paiement')
        paiement = abo.paiements.get()
        self.assertEqual(paiement.statut, 'en_attente')
        self.assertEqual(paiement.montant, 5000)
        self.assertEqual(paiement.numero_telephone, '0701020304')

    def test_simuler_confirmation_active_abonnement(self):
        r = self.client.post(f'/abonnements/souscrire/{self.plan_pro.pk}/', data={
            'moyen_paiement': 'wave', 'numero_telephone': '0708091011',
        })
        self.assertEqual(r.status_code, 302)
        paiement = Paiement.objects.get(abonnement__utilisateur=self.user, abonnement__plan=self.plan_pro)

        r = self.client.get('/abonnements/mon-abonnement/')
        self.assertContains(r, '0708091011')
        self.assertContains(r, 'Simuler la confirmation')

        r = self.client.post(f'/abonnements/paiement/{paiement.pk}/simuler-confirmation/')
        self.assertEqual(r.status_code, 302)
        paiement.refresh_from_db()
        self.assertEqual(paiement.statut, 'reussi')
        self.assertTrue(paiement.abonnement.est_actif)

    def test_simuler_confirmation_refuse_si_cinetpay_configure(self):
        abo = Abonnement.objects.create(utilisateur=self.user, plan=self.plan_pro, statut='en_attente_paiement')
        paiement = Paiement.objects.create(
            abonnement=abo, montant=5000, moyen_paiement='wave',
            reference_transaction='LC-GUARD1',
        )
        with patch('abonnements.views.cinetpay_configure', return_value=True):
            r = self.client.post(f'/abonnements/paiement/{paiement.pk}/simuler-confirmation/')
        self.assertEqual(r.status_code, 302)
        paiement.refresh_from_db()
        self.assertEqual(paiement.statut, 'en_attente', "Le garde-fou doit empecher l'auto-confirmation")

    def test_webhook_active_abonnement_si_paiement_reussi(self):
        abo = Abonnement.objects.create(utilisateur=self.user, plan=self.plan_pro, statut='en_attente_paiement')
        paiement = Paiement.objects.create(
            abonnement=abo, montant=5000, moyen_paiement='orange_money',
            reference_transaction='LC-TEST123',
        )
        with patch('abonnements.views.verifier_paiement', return_value='reussi'):
            r = self.client.post('/abonnements/webhook/cinetpay/', data={'cpm_trans_id': 'LC-TEST123'})
        self.assertEqual(r.status_code, 200)
        abo.refresh_from_db()
        paiement.refresh_from_db()
        self.assertTrue(abo.est_actif)
        self.assertEqual(paiement.statut, 'reussi')

    def test_limite_contrats_gratuits_bloque_la_creation(self):
        modele = ModeleContrat.objects.create(
            type_contrat='prestation', titre='Modele', description='',
            contenu='{{nom_client}}', actif=True,
        )
        # Aucun abonnement actif => limite gratuite implicite = 1 contrat/mois
        Contrat.objects.create(
            proprietaire=self.user, modele=modele, type_contrat='prestation',
            titre='Contrat 1', nom_client='A', nom_prestataire='B', objet='Test',
        )
        r = self.client.get(f'/contrats/nouveau/{modele.pk}/')
        self.assertRedirects(r, '/abonnements/')

    def test_annuler_renouvellement(self):
        abo = Abonnement.objects.create(
            utilisateur=self.user, plan=self.plan_pro, statut='actif',
            renouvellement_auto=True,
        )
        abo.activer()
        r = self.client.post(f'/abonnements/{abo.pk}/annuler-renouvellement/')
        self.assertEqual(r.status_code, 302)
        abo.refresh_from_db()
        self.assertFalse(abo.renouvellement_auto)

    def test_admin_gestion_reserve_aux_admins(self):
        r = self.client.get('/abonnements/admin/')
        self.assertEqual(r.status_code, 302)

    def test_admin_gestion_affiche_le_revenu(self):
        admin_user = User.objects.create_superuser('test_admin_abo', 'a@a.com', 'TestPass123!')
        Profil.objects.create(utilisateur=admin_user, role='admin')

        abo = Abonnement.objects.create(utilisateur=self.user, plan=self.plan_pro, statut='actif')
        abo.activer()
        Paiement.objects.create(
            abonnement=abo, montant=5000, moyen_paiement='wave',
            reference_transaction='LC-ADMINTEST', statut='reussi',
            confirme_le=timezone.now(),
        )

        self.client.logout()
        self.client.login(username='test_admin_abo', password='TestPass123!')
        r = self.client.get('/abonnements/admin/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '5000')
        self.assertContains(r, 'test_abo')
