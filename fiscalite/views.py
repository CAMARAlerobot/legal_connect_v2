from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal, InvalidOperation

from .models import Declaration, Echeance, TYPES_IMPOT, PERIODES
from . import calculateur

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT


@login_required
def dashboard_fiscal(request):
    user         = request.user
    declarations = Declaration.objects.filter(utilisateur=user).order_by('-created_at')
    echeances    = Echeance.objects.filter(utilisateur=user).order_by('date_limite')
    aujourd_hui  = timezone.now().date()

    from datetime import timedelta
    echeances_urgentes = echeances.filter(
        date_limite__gte=aujourd_hui,
        date_limite__lte=aujourd_hui + timedelta(days=7),
        statut='a_faire'
    )
    echeances.filter(date_limite__lt=aujourd_hui, statut='a_faire').update(statut='en_retard')

    context = {
        'declarations'      : declarations[:5],
        'echeances'         : echeances[:8],
        'echeances_urgentes': echeances_urgentes.count(),
        'total_declarations': declarations.count(),
        'total_impots'      : sum(d.montant_impot for d in declarations),
        'aujourd_hui'       : aujourd_hui,
    }
    return render(request, 'fiscalite/dashboard.html', context)


@login_required
def calculateur_view(request):
    resultat   = None
    type_impot = request.POST.get('type_impot', 'tva')
    erreur     = None

    if request.method == 'POST':
        try:
            data = {
                'chiffre_affaires': request.POST.get('chiffre_affaires', 0) or 0,
                'charges'         : request.POST.get('charges', 0) or 0,
                'salaire'         : request.POST.get('salaire', 0) or 0,
                'nb_employes'     : request.POST.get('nb_employes', 1) or 1,
            }
            resultat = calculateur.calculer(type_impot, data)

            if request.POST.get('sauvegarder') and resultat:
                Declaration.objects.create(
                    utilisateur      = request.user,
                    type_impot       = type_impot,
                    periode          = request.POST.get('periode', 'mensuel'),
                    annee            = timezone.now().year,
                    mois             = timezone.now().month,
                    chiffre_affaires = Decimal(str(data['chiffre_affaires'])),
                    charges          = Decimal(str(data['charges'])),
                    benefice_net     = resultat.get('benefice_net', 0),
                    taux_applique    = resultat.get('taux', 0) if isinstance(resultat.get('taux'), (int, float)) else 0,
                    montant_impot    = resultat.get('montant_impot', 0),
                )
                messages.success(request, 'Déclaration sauvegardée dans votre historique !')
                return redirect('fiscalite:historique')

        except (ValueError, InvalidOperation):
            erreur = "Erreur de calcul : veuillez vérifier vos saisies."

    context = {
        'types_impot': TYPES_IMPOT,
        'type_actif' : type_impot,
        'resultat'   : resultat,
        'erreur'     : erreur,
        'post_data'  : request.POST if request.method == 'POST' else {},
    }
    return render(request, 'fiscalite/calculateur.html', context)


@login_required
def historique(request):
    declarations = Declaration.objects.filter(utilisateur=request.user)

    type_impot = request.GET.get('type', '')
    annee      = request.GET.get('annee', '')
    if type_impot:
        declarations = declarations.filter(type_impot=type_impot)
    if annee:
        declarations = declarations.filter(annee=annee)

    total_impots = sum(d.montant_impot for d in declarations)
    annees = Declaration.objects.filter(
        utilisateur=request.user
    ).values_list('annee', flat=True).distinct()

    context = {
        'declarations': declarations,
        'types_impot' : TYPES_IMPOT,
        'type_actif'  : type_impot,
        'annee_active': annee,
        'annees'      : sorted(set(annees), reverse=True),
        'total_impots': total_impots,
    }
    return render(request, 'fiscalite/historique.html', context)


@login_required
def calendrier(request):
    aujourd_hui = timezone.now().date()
    echeances   = Echeance.objects.filter(utilisateur=request.user).order_by('date_limite')

    context = {
        'echeances'  : echeances,
        'types_impot': TYPES_IMPOT,
        'aujourd_hui': aujourd_hui,
    }
    return render(request, 'fiscalite/calendrier.html', context)


@login_required
def ajouter_echeance(request):
    if request.method == 'POST':
        titre       = request.POST.get('titre')
        type_impot  = request.POST.get('type_impot')
        date_limite = request.POST.get('date_limite')
        montant     = request.POST.get('montant') or None
        notes       = request.POST.get('notes', '')

        if titre and type_impot and date_limite:
            Echeance.objects.create(
                utilisateur = request.user,
                titre       = titre,
                type_impot  = type_impot,
                date_limite = date_limite,
                montant     = montant,
                notes       = notes,
            )
            messages.success(request, 'Échéance ajoutée au calendrier !')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    return redirect('fiscalite:calendrier')


@login_required
def marquer_echeance(request, pk):
    ech = get_object_or_404(Echeance, pk=pk, utilisateur=request.user)
    ech.statut = 'fait'
    ech.save()
    messages.success(request, f'Échéance "{ech.titre}" marquée comme faite.')
    return redirect('fiscalite:calendrier')


@login_required
def supprimer_echeance(request, pk):
    ech = get_object_or_404(Echeance, pk=pk, utilisateur=request.user)
    if request.method == 'POST':
        ech.delete()
        messages.success(request, 'Échéance supprimée.')
    return redirect('fiscalite:calendrier')


@login_required
def exporter_pdf_declaration(request, pk):
    decl = get_object_or_404(Declaration, pk=pk, utilisateur=request.user)
    user = request.user

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="declaration_{decl.type_impot}_{decl.annee}_{decl.pk}.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    BLEU    = colors.HexColor('#1B4F72')
    BLEU_S  = colors.HexColor('#2E86C1')
    BLEU_CL = colors.HexColor('#D6EAF8')
    VERT    = colors.HexColor('#1E8449')
    VERT_CL = colors.HexColor('#EAFAF1')

    style_titre = ParagraphStyle('titre',
        fontSize=18, textColor=BLEU, alignment=TA_CENTER,
        spaceAfter=4, fontName='Helvetica-Bold')
    style_sous_titre = ParagraphStyle('sous_titre',
        fontSize=11, textColor=BLEU_S, alignment=TA_CENTER,
        spaceAfter=16, fontName='Helvetica')
    style_section = ParagraphStyle('section',
        fontSize=11, textColor=BLEU, fontName='Helvetica-Bold',
        spaceBefore=12, spaceAfter=6)
    style_normal = ParagraphStyle('normal',
        fontSize=10, leading=16, alignment=TA_JUSTIFY,
        spaceAfter=6, fontName='Helvetica')
    style_footer = ParagraphStyle('footer',
        fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    style_montant = ParagraphStyle('montant',
        fontSize=22, textColor=VERT, alignment=TA_CENTER,
        fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=8)

    el = []

    # En-tête
    el.append(Paragraph("⚖ LÉGAL CONNECT", style_titre))
    el.append(Paragraph("Plateforme Numérique d'Assistance Juridique", style_sous_titre))
    el.append(HRFlowable(width="100%", thickness=2, color=BLEU))
    el.append(Spacer(1, 0.3*cm))
    el.append(Paragraph("DÉCLARATION FISCALE", style_titre))
    el.append(Paragraph(decl.get_type_impot_display(), style_sous_titre))

    # Référence
    ref_table = Table([[
        f"Référence : #{decl.pk:04d}",
        f"Type : {decl.get_type_impot_display()}",
        f"Statut : {decl.get_statut_display()}",
        f"Date : {decl.created_at.strftime('%d/%m/%Y')}",
    ]], colWidths=[3.5*cm, 4.5*cm, 4*cm, 4.5*cm])
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BLEU_CL),
        ('TEXTCOLOR',  (0,0), (-1,-1), BLEU),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWHEIGHT',  (0,0), (-1,-1), 22),
        ('BOX',        (0,0), (-1,-1), 0.5, BLEU_S),
    ]))
    el.append(ref_table)
    el.append(Spacer(1, 0.4*cm))

    # Contribuable
    el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
    el.append(Paragraph("INFORMATIONS DU CONTRIBUABLE", style_section))
    contrib_data = [
        ['Nom complet', f"{user.first_name} {user.last_name}"],
        ['Email',       user.email or 'Non renseigné'],
        ['Entreprise',  user.profil.entreprise or 'Non renseignée'],
        ['Téléphone',   user.profil.telephone or 'Non renseigné'],
        ['Adresse',     user.profil.adresse or 'Non renseignée'],
    ]
    contrib_table = Table(contrib_data, colWidths=[4*cm, 12.5*cm])
    contrib_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (0,-1), BLEU),
        ('TEXTCOLOR',    (0,0), (0,-1), colors.white),
        ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT',    (0,0), (-1,-1), 20),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('GRID',         (0,0), (-1,-1), 0.5, BLEU_S),
        ('BACKGROUND',   (1,0), (1,-1), colors.HexColor('#F8FBFF')),
        ('ROWBACKGROUNDS',(0,0),(-1,-1), [colors.HexColor('#F8FBFF'), colors.white]),
    ]))
    el.append(contrib_table)
    el.append(Spacer(1, 0.3*cm))

    # Période
    el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
    el.append(Paragraph("PÉRIODE DE DÉCLARATION", style_section))
    periode_val = f"{decl.get_periode_display()} — Année {decl.annee}"
    if decl.mois:
        mois_noms = ['','Janvier','Février','Mars','Avril','Mai','Juin',
                     'Juillet','Août','Septembre','Octobre','Novembre','Décembre']
        periode_val += f" — {mois_noms[decl.mois]}"
    if decl.trimestre:
        periode_val += f" — T{decl.trimestre}"
    el.append(Paragraph(periode_val, style_normal))
    el.append(Spacer(1, 0.2*cm))

    # Données financières
    el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
    el.append(Paragraph("DONNÉES FINANCIÈRES", style_section))

    fin_data = [['Libellé', 'Montant (FCFA)']]
    if decl.chiffre_affaires:
        fin_data.append(["Chiffre d'affaires", f"{decl.chiffre_affaires:,.0f}"])
    if decl.charges:
        fin_data.append(["Charges déductibles", f"{decl.charges:,.0f}"])
    if decl.benefice_net:
        fin_data.append(["Bénéfice net", f"{decl.benefice_net:,.0f}"])
    if decl.taux_applique:
        fin_data.append(["Taux appliqué", f"{decl.taux_applique}%"])

    fin_table = Table(fin_data, colWidths=[10*cm, 6.5*cm])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), BLEU),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (1,0), (1,-1), 'RIGHT'),
        ('ROWHEIGHT',    (0,0), (-1,-1), 22),
        ('LEFTPADDING',  (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('GRID',         (0,0), (-1,-1), 0.5, BLEU_S),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.HexColor('#F8FBFF'), colors.white]),
    ]))
    el.append(fin_table)
    el.append(Spacer(1, 0.4*cm))

    # Montant impôt — encadré vert
    el.append(HRFlowable(width="100%", thickness=1, color=VERT))
    montant_table = Table([
        ['MONTANT DE L\'IMPÔT DÛ'],
        [f"{decl.montant_impot:,.0f} FCFA"],
    ], colWidths=[16.5*cm])
    montant_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), BLEU),
        ('BACKGROUND',   (0,1), (-1,1), VERT_CL),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('TEXTCOLOR',    (0,1), (-1,1), VERT),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,0), 11),
        ('FONTSIZE',     (0,1), (-1,1), 22),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('ROWHEIGHT',    (0,0), (-1,0), 28),
        ('ROWHEIGHT',    (0,1), (-1,1), 50),
        ('BOX',          (0,0), (-1,-1), 1.5, VERT),
    ]))
    el.append(montant_table)
    el.append(Spacer(1, 0.5*cm))

    # Footer
    el.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    el.append(Spacer(1, 0.2*cm))
    el.append(Paragraph(
        f"Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')} — "
        "Légal Connect — Université Nangui Abrogoua — Master 1 MIAGE 2025-2026 — Confidentiel",
        style_footer
    ))

    doc.build(el)
    return response