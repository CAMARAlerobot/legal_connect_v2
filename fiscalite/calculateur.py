"""
Moteur de calcul fiscal pour la Côte d'Ivoire.
Taux en vigueur 2025-2026.
"""
from decimal import Decimal
from datetime import date

# ── TVA ────────────────────────────────────────────────────────────
TVA_TAUX = Decimal('0.18')        # 18%

def calculer_tva(chiffre_affaires: Decimal) -> dict:
    ca   = Decimal(str(chiffre_affaires))
    tva  = ca * TVA_TAUX
    ca_ht = ca / (1 + TVA_TAUX)
    return {
        'type'           : 'TVA',
        'ca_ttc'         : ca,
        'ca_ht'          : round(ca_ht, 2),
        'taux'           : float(TVA_TAUX * 100),
        'montant_impot'  : round(tva, 2),
        'detail'         : f"TVA = CA TTC × {TVA_TAUX*100:.0f}% = {ca} × 18% = {round(tva,2)} FCFA",
    }


# ── IS ─────────────────────────────────────────────────────────────
IS_TRANCHES = [
    (Decimal('0'),         Decimal('5000000'),   Decimal('0.20')),
    (Decimal('5000000'),   Decimal('20000000'),  Decimal('0.25')),
    (Decimal('20000000'),  Decimal('999999999'), Decimal('0.30')),
]
IS_MINIMUM = Decimal('500000')

def calculer_is(chiffre_affaires: Decimal, charges: Decimal) -> dict:
    ca      = Decimal(str(chiffre_affaires))
    ch      = Decimal(str(charges))
    benefice = max(ca - ch, Decimal('0'))

    impot = Decimal('0')
    detail_tranches = []
    for plancher, plafond, taux in IS_TRANCHES:
        if benefice <= plancher:
            break
        part = min(benefice, plafond) - plancher
        part_impot = part * taux
        impot += part_impot
        detail_tranches.append(f"{taux*100:.0f}% × {part:,.0f} = {part_impot:,.0f} FCFA")
        if benefice <= plafond:
            break

    impot = max(impot, IS_MINIMUM)
    return {
        'type'         : 'IS',
        'ca'           : ca,
        'charges'      : ch,
        'benefice_net' : benefice,
        'taux'         : 'Progressif (20%-30%)',
        'montant_impot': round(impot, 2),
        'tranches'     : detail_tranches,
        'detail'       : f"Bénéfice = {ca:,.0f} - {ch:,.0f} = {benefice:,.0f} FCFA | IS = {round(impot,2):,.0f} FCFA",
    }


# ── CNPS ───────────────────────────────────────────────────────────
CNPS_EMPLOYE    = Decimal('0.063')
CNPS_EMPLOYEUR  = Decimal('0.077')
CNPS_PLAFOND    = Decimal('3375000')

def calculer_cnps(salaire_mensuel: Decimal, nb_employes: int = 1) -> dict:
    sal     = Decimal(str(salaire_mensuel))
    base    = min(sal, CNPS_PLAFOND)
    employe = base * CNPS_EMPLOYE
    employeur = base * CNPS_EMPLOYEUR
    total   = (employe + employeur) * nb_employes
    return {
        'type'             : 'CNPS',
        'salaire'          : sal,
        'base_cotisation'  : base,
        'nb_employes'      : nb_employes,
        'part_employe'     : round(employe, 2),
        'part_employeur'   : round(employeur, 2),
        'total_mensuel'    : round(total, 2),
        'total_annuel'     : round(total * 12, 2),
        'taux'             : f"{CNPS_EMPLOYE*100:.1f}% (salarié) + {CNPS_EMPLOYEUR*100:.1f}% (employeur)",
        'montant_impot'    : round(total, 2),
        'detail'           : f"Base = min({sal:,.0f}, {CNPS_PLAFOND:,.0f}) = {base:,.0f} FCFA × (6,3% + 7,7%) × {nb_employes} = {round(total,2):,.0f} FCFA/mois",
    }


# ── BIC / BNC ──────────────────────────────────────────────────────
BIC_TAUX = Decimal('0.25')
BNC_TAUX = Decimal('0.20')

def calculer_bic(chiffre_affaires: Decimal, charges: Decimal) -> dict:
    ca      = Decimal(str(chiffre_affaires))
    ch      = Decimal(str(charges))
    benefice = max(ca - ch, Decimal('0'))
    impot   = benefice * BIC_TAUX
    return {
        'type'         : 'BIC',
        'ca'           : ca,
        'charges'      : ch,
        'benefice_net' : benefice,
        'taux'         : float(BIC_TAUX * 100),
        'montant_impot': round(impot, 2),
        'detail'       : f"BIC = {benefice:,.0f} × 25% = {round(impot,2):,.0f} FCFA",
    }

def calculer_bnc(recettes: Decimal, depenses: Decimal) -> dict:
    rec   = Decimal(str(recettes))
    dep   = Decimal(str(depenses))
    benefice = max(rec - dep, Decimal('0'))
    impot = benefice * BNC_TAUX
    return {
        'type'         : 'BNC',
        'ca'           : rec,
        'charges'      : dep,
        'benefice_net' : benefice,
        'taux'         : float(BNC_TAUX * 100),
        'montant_impot': round(impot, 2),
        'detail'       : f"BNC = {benefice:,.0f} × 20% = {round(impot,2):,.0f} FCFA",
    }


# ── PATENTE ────────────────────────────────────────────────────────
# Patente CI : droit fixe selon catégorie + droit proportionnel sur valeur locative
# Simplification : taux global estimatif selon tranche de CA (CGI art. 264)
PATENTE_TRANCHES = [
    (Decimal('0'),          Decimal('5000000'),   Decimal('50000'),   Decimal('0.005')),
    (Decimal('5000000'),    Decimal('20000000'),  Decimal('150000'),  Decimal('0.007')),
    (Decimal('20000000'),   Decimal('50000000'),  Decimal('350000'),  Decimal('0.010')),
    (Decimal('50000000'),   Decimal('100000000'), Decimal('700000'),  Decimal('0.012')),
    (Decimal('100000000'),  Decimal('999999999'), Decimal('1500000'), Decimal('0.015')),
]

def calculer_patente(chiffre_affaires: Decimal) -> dict:
    ca = Decimal(str(chiffre_affaires))
    droit_fixe = Decimal('50000')
    droit_proportionnel = Decimal('0')
    taux_applique = Decimal('0.005')

    for plancher, _, fixe, taux in PATENTE_TRANCHES:
        if ca > plancher:
            droit_fixe = fixe
            taux_applique = taux
            droit_proportionnel = ca * taux

    total = droit_fixe + droit_proportionnel
    return {
        'type'              : 'Patente',
        'ca'                : ca,
        'droit_fixe'        : round(droit_fixe, 2),
        'droit_proportionnel': round(droit_proportionnel, 2),
        'taux'              : float(taux_applique * 100),
        'montant_impot'     : round(total, 2),
        'benefice_net'      : Decimal('0'),
        'detail'            : f"Patente = Droit fixe {droit_fixe:,.0f} + Droit proportionnel ({ca:,.0f} × {taux_applique*100:.1f}%) = {round(total,2):,.0f} FCFA",
    }


# ── TSE ────────────────────────────────────────────────────────────
# Taxe Spéciale sur l'Équipement : 0.1% du CA HT (CGI art. 1086)
TSE_TAUX    = Decimal('0.001')
TSE_MINIMUM = Decimal('25000')
TSE_PLAFOND = Decimal('5000000')

def calculer_tse(chiffre_affaires: Decimal) -> dict:
    ca    = Decimal(str(chiffre_affaires))
    tse   = ca * TSE_TAUX
    tse   = max(tse, TSE_MINIMUM)
    tse   = min(tse, TSE_PLAFOND)
    return {
        'type'         : 'TSE',
        'ca'           : ca,
        'taux'         : float(TSE_TAUX * 100),
        'montant_impot': round(tse, 2),
        'benefice_net' : Decimal('0'),
        'detail'       : f"TSE = {ca:,.0f} × 0,1% = {round(tse,2):,.0f} FCFA (min {TSE_MINIMUM:,.0f} | max {TSE_PLAFOND:,.0f} FCFA)",
    }


# ── IMF ────────────────────────────────────────────────────────────
# Impôt Minimum Forfaitaire : 1% du CA HT, minimum 300 000 FCFA (CGI art. 36)
IMF_TAUX    = Decimal('0.01')
IMF_MINIMUM = Decimal('300000')

def calculer_imf(chiffre_affaires: Decimal) -> dict:
    ca  = Decimal(str(chiffre_affaires))
    imf = max(ca * IMF_TAUX, IMF_MINIMUM)
    return {
        'type'         : 'IMF',
        'ca'           : ca,
        'taux'         : float(IMF_TAUX * 100),
        'montant_impot': round(imf, 2),
        'benefice_net' : Decimal('0'),
        'detail'       : f"IMF = max({ca:,.0f} × 1%, {IMF_MINIMUM:,.0f}) = {round(imf,2):,.0f} FCFA",
    }


# ── PÉNALITÉS DE RETARD ────────────────────────────────────────────
# CGI CI : majoration 10% + 1% par mois de retard (max 100%)
def calculer_penalites(montant_principal: Decimal, date_echeance: date, date_paiement: date = None) -> dict:
    if date_paiement is None:
        date_paiement = date.today()

    montant  = Decimal(str(montant_principal))
    delta    = date_paiement - date_echeance

    if delta.days <= 0:
        return {
            'en_retard'        : False,
            'jours_retard'     : 0,
            'mois_retard'      : 0,
            'majoration_fixe'  : Decimal('0'),
            'majoration_mensuelle': Decimal('0'),
            'total_penalites'  : Decimal('0'),
            'montant_total'    : montant,
            'detail'           : "Aucune pénalité — paiement dans les délais.",
        }

    jours    = delta.days
    mois     = min((jours + 29) // 30, 90)
    taux_fixe    = Decimal('0.10')
    taux_mensuel = Decimal('0.01') * mois
    taux_total   = min(taux_fixe + taux_mensuel, Decimal('1.00'))

    maj_fixe    = montant * taux_fixe
    maj_mensuel = montant * taux_mensuel
    total_pen   = montant * taux_total
    total       = montant + total_pen

    return {
        'en_retard'           : True,
        'jours_retard'        : jours,
        'mois_retard'         : mois,
        'montant_principal'   : montant,
        'taux_fixe'           : float(taux_fixe * 100),
        'taux_mensuel_total'  : float(taux_mensuel * 100),
        'taux_total'          : float(taux_total * 100),
        'majoration_fixe'     : round(maj_fixe, 2),
        'majoration_mensuelle': round(maj_mensuel, 2),
        'total_penalites'     : round(total_pen, 2),
        'montant_total'       : round(total, 2),
        'detail'              : (
            f"Retard de {jours} jours ({mois} mois) — "
            f"Majoration fixe 10% ({maj_fixe:,.0f}) + "
            f"1%/mois × {mois} ({maj_mensuel:,.0f}) = "
            f"Total pénalités : {round(total_pen,2):,.0f} FCFA"
        ),
    }


# ── SUGGESTIONS D'OPTIMISATION FISCALE ────────────────────────────
def suggestions_optimisation(type_impot: str, data: dict) -> list:
    """Retourne des conseils d'optimisation fiscale selon le type d'impôt."""
    suggestions = []
    ca       = Decimal(str(data.get('chiffre_affaires', 0)))
    charges  = Decimal(str(data.get('charges', 0)))
    benefice = max(ca - charges, Decimal('0'))
    salaire  = Decimal(str(data.get('salaire', 0)))

    if type_impot == 'tva':
        suggestions += [
            {
                'titre'     : 'Récupérez votre TVA sur achats professionnels',
                'detail'    : 'Conservez toutes vos factures fournisseurs pour déduire la TVA payée sur vos achats.',
                'economie'  : None,
                'priorite'  : 'haute',
            },
            {
                'titre'     : 'Régime du réel simplifié',
                'detail'    : 'Si votre CA < 150M FCFA, optez pour le régime simplifié avec déclaration trimestrielle.',
                'economie'  : None,
                'priorite'  : 'moyenne',
            },
        ]
        if ca > Decimal('150000000'):
            suggestions.append({
                'titre'   : 'Attention au franchissement de seuil',
                'detail'  : 'Au-delà de 150M FCFA de CA, vous êtes obligatoirement au régime réel normal (déclaration mensuelle).',
                'economie': None,
                'priorite': 'haute',
            })

    elif type_impot == 'is':
        suggestions += [
            {
                'titre'   : 'Maximisez vos charges déductibles',
                'detail'  : 'Loyers, amortissements, frais de personnel, provisions pour créances douteuses sont déductibles.',
                'economie': None,
                'priorite': 'haute',
            },
            {
                'titre'   : 'Amortissement accéléré',
                'detail'  : 'Les investissements en équipements peuvent bénéficier d\'un amortissement accéléré sur 2 ans.',
                'economie': None,
                'priorite': 'moyenne',
            },
        ]
        if benefice > Decimal('20000000'):
            eco = (benefice - Decimal('20000000')) * (Decimal('0.30') - Decimal('0.25'))
            suggestions.append({
                'titre'   : 'Tranche à 30% — Réduisez votre bénéfice imposable',
                'detail'  : f'Votre bénéfice dépasse 20M FCFA. Chaque FCFA de charges supplémentaires vous économise 30 cts d\'impôt.',
                'economie': round(eco, 0),
                'priorite': 'haute',
            })
        suggestions.append({
            'titre'   : 'Déficit reportable',
            'detail'  : 'Un déficit fiscal peut être reporté sur les 5 exercices suivants pour réduire l\'IS futur.',
            'economie': None,
            'priorite': 'faible',
        })

    elif type_impot == 'cnps':
        if salaire > CNPS_PLAFOND:
            eco = (salaire - CNPS_PLAFOND) * (CNPS_EMPLOYE + CNPS_EMPLOYEUR)
            suggestions.append({
                'titre'   : 'Salaire au-dessus du plafond CNPS',
                'detail'  : f'La base de cotisation est plafonnée à {CNPS_PLAFOND:,.0f} FCFA/mois par employé.',
                'economie': round(eco, 0),
                'priorite': 'info',
            })
        suggestions += [
            {
                'titre'   : 'Avantages en nature',
                'detail'  : 'Certains avantages en nature (logement, véhicule) ont des règles d\'évaluation forfaitaire favorables.',
                'economie': None,
                'priorite': 'moyenne',
            },
            {
                'titre'   : 'Régularité des déclarations',
                'detail'  : 'Déclarez et payez avant le 15 du mois suivant pour éviter les majorations de 10%.',
                'economie': None,
                'priorite': 'haute',
            },
        ]

    elif type_impot in ('bic', 'bnc'):
        suggestions += [
            {
                'titre'   : 'Abattement forfaitaire BNC',
                'detail'  : 'Les professionnels libéraux peuvent opter pour l\'abattement forfaitaire de 30% sur recettes brutes.',
                'economie': None,
                'priorite': 'haute',
            } if type_impot == 'bnc' else {
                'titre'   : 'Stock et provisions',
                'detail'  : 'Évaluez correctement votre stock de fin d\'exercice. Une provision pour stock obsolète est déductible.',
                'economie': None,
                'priorite': 'moyenne',
            },
            {
                'titre'   : 'Frais professionnels documentés',
                'detail'  : 'Transport, repas d\'affaires, documentation professionnelle — conservez toutes vos justificatifs.',
                'economie': None,
                'priorite': 'haute',
            },
        ]

    elif type_impot == 'patente':
        suggestions += [
            {
                'titre'   : 'Vérification de la catégorie patente',
                'detail'  : 'Assurez-vous d\'être classé dans la bonne catégorie. Une erreur peut entraîner une surtaxation.',
                'economie': None,
                'priorite': 'haute',
            },
            {
                'titre'   : 'Exonérations possibles',
                'detail'  : 'Nouvelles entreprises bénéficient d\'une exonération de 2 ans. Vérifiez votre éligibilité.',
                'economie': None,
                'priorite': 'haute',
            },
        ]

    # Conseil commun toujours affiché
    suggestions.append({
        'titre'   : 'Consultez un expert-comptable agréé',
        'detail'  : 'Pour optimiser votre fiscalité, faites-vous accompagner par un expert-comptable ou un fiscaliste.',
        'economie': None,
        'priorite': 'info',
    })

    return suggestions


def calculer(type_impot: str, data: dict) -> dict:
    """Point d'entrée principal."""
    ca       = Decimal(str(data.get('chiffre_affaires', 0)))
    charges  = Decimal(str(data.get('charges', 0)))
    salaire  = Decimal(str(data.get('salaire', 0)))
    employes = int(data.get('nb_employes', 1))

    if type_impot == 'tva':
        return calculer_tva(ca)
    elif type_impot == 'is':
        return calculer_is(ca, charges)
    elif type_impot == 'cnps':
        return calculer_cnps(salaire, employes)
    elif type_impot == 'bic':
        return calculer_bic(ca, charges)
    elif type_impot == 'bnc':
        return calculer_bnc(ca, charges)
    elif type_impot == 'patente':
        return calculer_patente(ca)
    elif type_impot == 'tse':
        return calculer_tse(ca)
    elif type_impot == 'imf':
        return calculer_imf(ca)
    return {}
