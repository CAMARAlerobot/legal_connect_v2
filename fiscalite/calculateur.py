"""
Moteur de calcul fiscal pour la Côte d'Ivoire.
Taux en vigueur 2025-2026.
"""
from decimal import Decimal

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
# Tranches IS Côte d'Ivoire
IS_TRANCHES = [
    (Decimal('0'),         Decimal('5000000'),   Decimal('0.20')),   # 20% jusqu'à 5M
    (Decimal('5000000'),   Decimal('20000000'),  Decimal('0.25')),   # 25% de 5M à 20M
    (Decimal('20000000'),  Decimal('999999999'), Decimal('0.30')),   # 30% au-delà
]
IS_MINIMUM = Decimal('500000')   # IS minimum annuel

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
CNPS_EMPLOYE    = Decimal('0.063')   # 6.3% salarié
CNPS_EMPLOYEUR  = Decimal('0.077')   # 7.7% employeur  → taux global 14%
CNPS_PLAFOND    = Decimal('3375000') # Plafond mensuel par employé

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


def calculer(type_impot: str, data: dict) -> dict:
    """Point d'entrée principal."""
    ca      = Decimal(str(data.get('chiffre_affaires', 0)))
    charges = Decimal(str(data.get('charges', 0)))
    salaire = Decimal(str(data.get('salaire', 0)))
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
    return {}