"""
Verifie que la base de connaissances juridique (datasets chatbot/data/) est
bien prise en compte par le chatbot.

Usage :
    python manage.py tester_kb "mon employeur ne me paie pas mon salaire"
    python manage.py tester_kb --stats
"""
from django.core.management.base import BaseCommand

from chatbot.kb import DATA_DIR, INDEX_DIR, charger_lots, rechercher


class Command(BaseCommand):
    help = "Teste la recherche d'articles de loi (RAG) utilisee par le chatbot."

    def add_arguments(self, parser):
        parser.add_argument('question', nargs='?', type=str, help='Question a tester')
        parser.add_argument('--stats', action='store_true', help="N'afficher que les statistiques de l'index")
        parser.add_argument('--top', type=int, default=3, help='Nombre de resultats a afficher (defaut 3)')

    def handle(self, *args, **options):
        if options['stats'] or not options['question']:
            self._afficher_stats()
            if not options['question']:
                return

        question = options['question']
        top = options['top']

        self.stdout.write(self.style.MIGRATE_HEADING(f"\nQuestion : {question}"))

        resultats = rechercher(question, top_k=top, seuil=0.0)
        if not resultats:
            self.stdout.write(self.style.ERROR(
                "Aucun resultat — l'index n'existe pas encore. "
                "Lancez : python chatbot/construire_index.py"
            ))
            return

        for r in resultats:
            if r['score'] >= 0.30:
                niveau = self.style.SUCCESS(f"[{r['score']}] CITABLE dans moteur.py (seuil 0.30)")
            elif r['score'] >= 0.15:
                niveau = self.style.WARNING(f"[{r['score']}] envoye a Claude comme contexte (seuil 0.15)")
            else:
                niveau = self.style.NOTICE(f"[{r['score']}] trop faible, ignore")
            self.stdout.write(f"\n{niveau}")
            self.stdout.write(f"  Source : {r['source']}  (categorie : {r['label']})")
            extrait = r['texte'].strip().replace('\n', ' ')
            self.stdout.write(f"  Texte  : {extrait[:200]}")

    def _afficher_stats(self):
        lignes = charger_lots(DATA_DIR)
        vectorizer_ok = (INDEX_DIR / 'kb_vectorizer.pkl').exists()
        self.stdout.write(self.style.MIGRATE_HEADING("Etat de la base de connaissances du chatbot"))
        self.stdout.write(f"  Dossier CSV     : {DATA_DIR}")
        self.stdout.write(f"  Lignes lues     : {len(lignes)}")
        self.stdout.write(f"  Sources uniques : {len(set(l['source'] for l in lignes))}")
        self.stdout.write(f"  Index construit : {'OUI' if vectorizer_ok else 'NON — lancez python chatbot/construire_index.py'}")
