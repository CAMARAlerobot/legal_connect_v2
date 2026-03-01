from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Contrat, ModeleContrat, TYPES_CONTRAT
from .forms import ContratEtape2Form

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

@login_required
def liste_contrats(request):
    contrats = Contrat.objects.filter(proprietaire=request.user).order_by('-created_at')

    statut       = request.GET.get('statut', '')
    type_contrat = request.GET.get('type', '')
    recherche    = request.GET.get('q', '')

    if statut:
        contrats = contrats.filter(statut=statut)
    if type_contrat:
        contrats = contrats.filter(type_contrat=type_contrat)
    if recherche:
        contrats = contrats.filter(titre__icontains=recherche)

    from django.core.paginator import Paginator
    paginator = Paginator(contrats, 10)
    page      = request.GET.get('page', 1)
    page_obj  = paginator.get_page(page)

    context = {
        'contrats'     : page_obj,
        'page_obj'     : page_obj,
        'types_contrat': TYPES_CONTRAT,
        'statut_actif' : statut,
        'type_actif'   : type_contrat,
        'recherche'    : recherche,
        'total'        : paginator.count,
    }
    return render(request, 'contrats/liste.html', context)
@login_required
def choisir_modele(request):
    modeles = ModeleContrat.objects.filter(actif=True).order_by('type_contrat')
    types   = {}
    for m in modeles:
        types.setdefault(m.get_type_contrat_display(), []).append(m)

    if request.method == 'POST':
        modele_id = request.POST.get('modele_id')
        if modele_id:
            return redirect('contrats:creer', modele_id=modele_id)
        messages.error(request, 'Veuillez sélectionner un modèle.')

    return render(request, 'contrats/choisir_modele.html', {'types': types, 'modeles': modeles})


@login_required
def creer_contrat(request, modele_id):
    modele = get_object_or_404(ModeleContrat, id=modele_id, actif=True)

    if request.method == 'POST':
        form = ContratEtape2Form(request.POST)
        if form.is_valid():
            contrat = form.save(commit=False)
            contrat.proprietaire  = request.user
            contrat.modele        = modele
            contrat.type_contrat  = modele.type_contrat
            contrat.contenu_final = generer_contenu(modele, form.cleaned_data)
            contrat.save()
            messages.success(request, 'Contrat créé avec succès !')
            return redirect('contrats:detail', pk=contrat.pk)
    else:
        form = ContratEtape2Form(initial={'type_contrat': modele.type_contrat})

    return render(request, 'contrats/creer.html', {'form': form, 'modele': modele})


def generer_contenu(modele, data):
    contenu = modele.contenu
    remplacements = {
        '{{nom_client}}'           : data.get('nom_client', ''),
        '{{email_client}}'         : data.get('email_client', ''),
        '{{telephone_client}}'     : data.get('telephone_client', ''),
        '{{adresse_client}}'       : data.get('adresse_client', ''),
        '{{nom_prestataire}}'      : data.get('nom_prestataire', ''),
        '{{email_prestataire}}'    : data.get('email_prestataire', ''),
        '{{telephone_prestataire}}': data.get('telephone_prestataire', ''),
        '{{adresse_prestataire}}'  : data.get('adresse_prestataire', ''),
        '{{objet}}'                : data.get('objet', ''),
        '{{montant}}'              : str(data.get('montant', '')),
        '{{devise}}'               : data.get('devise', 'FCFA'),
        '{{date_debut}}'           : str(data.get('date_debut', '')),
        '{{date_fin}}'             : str(data.get('date_fin', '')),
        '{{lieu_signature}}'       : data.get('lieu_signature', ''),
        '{{clauses_speciales}}'    : data.get('clauses_speciales', ''),
        '{{titre}}'                : data.get('titre', ''),
    }
    for variable, valeur in remplacements.items():
        contenu = contenu.replace(variable, valeur)
    return contenu


@login_required
def detail_contrat(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk, proprietaire=request.user)
    return render(request, 'contrats/detail.html', {'contrat': contrat})


@login_required
def modifier_contrat(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        form = ContratEtape2Form(request.POST, instance=contrat)
        if form.is_valid():
            contrat = form.save(commit=False)
            if contrat.modele:
                contrat.contenu_final = generer_contenu(contrat.modele, form.cleaned_data)
            contrat.save()
            messages.success(request, 'Contrat mis à jour avec succès !')
            return redirect('contrats:detail', pk=contrat.pk)
    else:
        form = ContratEtape2Form(instance=contrat)

    return render(request, 'contrats/modifier.html', {'form': form, 'contrat': contrat})


@login_required
def supprimer_contrat(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk, proprietaire=request.user)
    if request.method == 'POST':
        contrat.delete()
        messages.success(request, 'Contrat supprimé.')
        return redirect('contrats:liste')
    return render(request, 'contrats/supprimer.html', {'contrat': contrat})


@login_required
def exporter_pdf(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk, proprietaire=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contrat_{contrat.pk:04d}.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    BLEU    = colors.HexColor('#1B4F72')
    BLEU_S  = colors.HexColor('#2E86C1')
    BLEU_CL = colors.HexColor('#D6EAF8')

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

    el = []

    # En-tête
    el.append(Paragraph("⚖ LÉGAL CONNECT", style_titre))
    el.append(Paragraph("Plateforme Numérique d'Assistance Juridique", style_sous_titre))
    el.append(HRFlowable(width="100%", thickness=2, color=BLEU))
    el.append(Spacer(1, 0.3*cm))
    el.append(Paragraph(contrat.titre.upper(), style_titre))
    el.append(Paragraph(contrat.get_type_contrat_display(), style_sous_titre))

    # Statut
    statut_table = Table([[
        f"Statut : {contrat.get_statut_display()}",
        f"Référence : #{contrat.pk:04d}",
        f"Date : {contrat.created_at.strftime('%d/%m/%Y')}",
    ]], colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    statut_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BLEU_CL),
        ('TEXTCOLOR',  (0,0), (-1,-1), BLEU),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('ROWHEIGHT',  (0,0), (-1,-1), 22),
        ('BOX',        (0,0), (-1,-1), 0.5, BLEU_S),
    ]))
    el.append(statut_table)
    el.append(Spacer(1, 0.4*cm))

    # Parties
    el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
    el.append(Paragraph("ENTRE LES SOUSSIGNÉS", style_section))
    parties_table = Table([
        ['PARTIE 1 — CLIENT / PRENEUR', 'PARTIE 2 — PRESTATAIRE / BAILLEUR'],
        [
            f"{contrat.nom_client}\n{contrat.email_client or ''}\n{contrat.telephone_client or ''}\n{contrat.adresse_client or ''}".strip(),
            f"{contrat.nom_prestataire}\n{contrat.email_prestataire or ''}\n{contrat.telephone_prestataire or ''}\n{contrat.adresse_prestataire or ''}".strip(),
        ]
    ], colWidths=[8.25*cm, 8.25*cm])
    parties_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), BLEU),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (0,0), (-1,0), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ('LEADING',      (0,1), (-1,-1), 14),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('LEFTPADDING',  (0,0), (-1,-1), 8),
        ('GRID',         (0,0), (-1,-1), 0.5, BLEU_S),
        ('BACKGROUND',   (0,1), (-1,-1), colors.HexColor('#F8FBFF')),
        ('ROWHEIGHT',    (0,0), (-1,0), 20),
    ]))
    el.append(parties_table)
    el.append(Spacer(1, 0.3*cm))

    # Objet
    el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
    el.append(Paragraph("OBJET DU CONTRAT", style_section))
    el.append(Paragraph(contrat.objet or "Non renseigné", style_normal))

    # Détails financiers
    headers, values = [], []
    if contrat.montant:
        headers.append("Montant")
        values.append(f"{contrat.montant:,.0f} {contrat.devise}")
    if contrat.date_debut:
        headers.append("Date de début")
        values.append(contrat.date_debut.strftime('%d/%m/%Y'))
    if contrat.date_fin:
        headers.append("Date de fin")
        values.append(contrat.date_fin.strftime('%d/%m/%Y'))
    if contrat.lieu_signature:
        headers.append("Lieu")
        values.append(contrat.lieu_signature)

    if headers:
        el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
        el.append(Paragraph("CONDITIONS FINANCIÈRES ET DURÉE", style_section))
        col_w = 16.5*cm / len(headers)
        det_table = Table([headers, values], colWidths=[col_w]*len(headers))
        det_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), BLEU),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
            ('TEXTCOLOR',  (0,1), (-1,1), BLEU),
            ('FONTSIZE',   (0,0), (-1,-1), 9),
            ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
            ('ROWHEIGHT',  (0,0), (-1,-1), 22),
            ('GRID',       (0,0), (-1,-1), 0.5, BLEU_S),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FBFF')),
        ]))
        el.append(det_table)

    # Clauses spéciales
    if contrat.clauses_speciales:
        el.append(Spacer(1, 0.2*cm))
        el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
        el.append(Paragraph("CLAUSES PARTICULIÈRES", style_section))
        el.append(Paragraph(contrat.clauses_speciales.replace('\n', '<br/>'), style_normal))

    # Contenu final
    if contrat.contenu_final:
        el.append(Spacer(1, 0.2*cm))
        el.append(HRFlowable(width="100%", thickness=1, color=BLEU_S))
        el.append(Paragraph("DISPOSITIONS GÉNÉRALES", style_section))
        for ligne in contrat.contenu_final.split('\n'):
            if ligne.strip():
                el.append(Paragraph(ligne, style_normal))

    # Signatures
    el.append(Spacer(1, 0.6*cm))
    el.append(HRFlowable(width="100%", thickness=2, color=BLEU))
    el.append(Paragraph("SIGNATURES DES PARTIES", style_section))
    el.append(Paragraph(
        f"Fait à {contrat.lieu_signature or 'Abidjan'}, le {contrat.created_at.strftime('%d/%m/%Y')}",
        style_normal
    ))
    el.append(Spacer(1, 0.4*cm))

    sign_table = Table([
        ['LE CLIENT / PRENEUR', 'LE PRESTATAIRE / BAILLEUR'],
        [contrat.nom_client, contrat.nom_prestataire],
        ['\n\n\n(Signature)', '\n\n\n(Signature)'],
    ], colWidths=[8.25*cm, 8.25*cm])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,0), BLEU),
        ('TEXTCOLOR',    (0,0), (-1,0), colors.white),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME',     (0,1), (-1,1), 'Helvetica-Bold'),
        ('TEXTCOLOR',    (0,1), (-1,1), BLEU),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT',    (0,0), (-1,0), 20),
        ('ROWHEIGHT',    (0,2), (-1,2), 60),
        ('GRID',         (0,0), (-1,-1), 0.5, BLEU_S),
        ('BACKGROUND',   (0,1), (-1,-1), colors.white),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
    ]))
    el.append(sign_table)

    # Footer
    el.append(Spacer(1, 0.5*cm))
    el.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    el.append(Spacer(1, 0.2*cm))
    el.append(Paragraph(
        "Document généré par Légal Connect — Université Nangui Abrogoua — Master 1 MIAGE 2025-2026 — Confidentiel",
        style_footer
    ))

    doc.build(el)
    return response


@login_required
def finaliser_contrat(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk, proprietaire=request.user)
    contrat.statut = 'finalise'
    contrat.save()
    messages.success(request, 'Contrat finalisé avec succès !')
    return redirect('contrats:detail', pk=pk)