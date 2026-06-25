#!/usr/bin/env python3
"""Genera PDF informativo per i condomini del Condominio Mazzini 3."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime

OUTPUT = "/home/openclaw/attibot/reports/condominio_mazzini3_info_condomini.pdf"

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title="Condominio Mazzini 3 — Note informative appalto e finanziamento",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title2', parent=styles['Title'],
        fontSize=16, textColor=colors.HexColor('#1a3a5c'),
        spaceAfter=4, leading=20)

    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#555555'),
        spaceAfter=12, alignment=TA_CENTER)

    h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
        fontSize=13, textColor=colors.HexColor('#1a3a5c'),
        spaceBefore=14, spaceAfter=4)

    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
        fontSize=11, textColor=colors.HexColor('#2c5f8a'),
        spaceBefore=10, spaceAfter=3)

    body = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6, alignment=TA_JUSTIFY)

    bullet = ParagraphStyle('Bullet', parent=styles['Normal'],
        fontSize=10, leading=13, leftIndent=12, spaceAfter=3)

    note_style = ParagraphStyle('Note', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=colors.HexColor('#444444'),
        leftIndent=8, spaceAfter=6)

    alert_style = ParagraphStyle('Alert', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6,
        backColor=colors.HexColor('#fff3cd'),
        borderColor=colors.HexColor('#ffc107'),
        borderWidth=1, borderPad=6)

    red_style = ParagraphStyle('Red', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6,
        backColor=colors.HexColor('#f8d7da'),
        borderColor=colors.HexColor('#dc3545'),
        borderWidth=1, borderPad=6)

    green_style = ParagraphStyle('Green', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6,
        backColor=colors.HexColor('#d4edda'),
        borderColor=colors.HexColor('#28a745'),
        borderWidth=1, borderPad=6)

    story = []

    # ── INTESTAZIONE ──────────────────────────────────────────────────────────
    story.append(Paragraph("Condominio Mazzini 3", title_style))
    story.append(Paragraph("Via Pacini 77/79/81 — Seregno (MB)", subtitle_style))
    story.append(Paragraph(
        "Note informative per i condomini — Riunione con Edilizia Acrobatica del 26 giugno 2026",
        subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2,
        color=colors.HexColor('#1a3a5c'), spaceAfter=12))

    story.append(Paragraph(
        "Questo documento sintetizza la situazione relativa all'appalto di rifacimento facciate, "
        "con particolare riferimento alla questione finanziaria che blocca l'erogazione del "
        "finanziamento Banca Sella da mesi. È redatto sulla base della corrispondenza intercorsa "
        "tra l'amministratore e Edilizia Acrobatica.",
        note_style))

    story.append(Spacer(1, 4))

    # ── DATI APPALTO ──────────────────────────────────────────────────────────
    story.append(Paragraph("1. I numeri dell'appalto", h1_style))

    data = [
        ["Voce", "Importo / Dettaglio"],
        ["Appalto base lavori (tutti i condomini)", "€ 230.000,00 + IVA 10%"],
        ["Extra addebitato ai soli 5 condomini finanziatori", "€ 5.840,78 + IVA 10%"],
        ["Totale appalto deliberato in assemblea (unanime)", "€ 235.840,78 + IVA 10%"],
        ["Finanziamento Sella Personal Credit", "€ 22.798,26 IVA incl. — 48 rate — TAN 0,00%"],
        ["Lavori", "Partiti a giugno 2026 — nuova colorazione comunicata ad Acrobatica"],
        ["Scadenza detraibilità 50%", "Rate pagate entro il 21/12/2026"],
    ]
    t = Table(data, colWidths=[9*cm, 8.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a3a5c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
        ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,3), (-1,3), colors.HexColor('#1a3a5c')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # ── IL PROBLEMA SOSTANZIALE ───────────────────────────────────────────────
    story.append(Paragraph("2. Il problema sostanziale: il finanziamento è a rischio", h1_style))

    story.append(Paragraph(
        "<b>Il finanziamento Banca Sella non è ancora stato erogato</b>, nonostante "
        "l'assemblea abbia deliberato ad aprile 2026. Il motivo è una questione che "
        "riguarda i €5.840,78 — cifra che appare esplicitamente nel verbale assembleare "
        "e che Acrobatica non riesce a gestire senza la collaborazione dell'amministratore.",
        body))

    story.append(Paragraph(
        "⚠ ATTENZIONE: il nodo non è solo fiscale. Il rischio concreto è che il "
        "finanziamento non venga erogato nella sua totalità, bloccando la possibilità "
        "dei 5 condomini di pagare a rate.",
        red_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Cosa sono i €5.840,78:", h2_style))
    story.append(Paragraph(
        "Sono un costo aggiuntivo addebitato <b>esclusivamente ai 5 condomini che hanno "
        "scelto il finanziamento</b>. Non fanno parte dell'appalto base (€230.000), "
        "non vengono erogati da Banca Sella e non riguardano gli altri condomini.", body))
    story.append(Paragraph(
        "Nella sostanza rappresentano la commissione che Acrobatica paga a Sella Personal Credit "
        "per offrire il finanziamento a tasso zero — commissione che, invece di assorbire "
        "nel proprio prezzo come sarebbe corretto, ha ribaltato sui 5 condomini finanziatori.", body))

    story.append(Paragraph(
        "⚠ Risultato: chi ha scelto il finanziamento paga €5.840 in più rispetto a chi "
        "paga in contanti. Questo per definizione non è un vero tasso zero.",
        alert_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Il nodo con Banca Sella:", h2_style))
    story.append(Paragraph(
        "Il verbale assembleare del 10 aprile 2026 recita testualmente che i €5.840,78 "
        "sono destinati all'addebito pro quota <i>\"ai 5 condomini che hanno fatto richiesta "
        "del finanziamento con Sella Personal Credit\"</i>. "
        "Questo significa che <b>chiunque legga il verbale originale — inclusa Banca Sella — "
        "può vedere che i finanziatori pagano di più degli altri</b>.", body))
    story.append(Paragraph(
        "La banca, vedendo questa voce, potrebbe concludere che il finanziamento "
        "non è davvero a tasso zero (perché c'è un sovracosto legato ad esso) e "
        "<b>rifiutare l'erogazione</b> o richiedere ad Acrobatica di rinegoziare le condizioni.", body))

    story.append(Paragraph("Cosa ha chiesto Acrobatica:", h2_style))
    story.append(Paragraph(
        "Acrobatica ha chiesto all'amministratore di inviare a Banca Sella una copia "
        "del verbale <b>senza quella riga</b> (cosiddetto \"omissis\"). "
        "Obiettivo: far sembrare alla banca che i €5.840 non esistano, "
        "così il finanziamento risulta formalmente a tasso zero e viene erogato. "
        "Contemporaneamente, quei €5.840 verrebbero portati in detrazione fiscale al 50% "
        "come se fossero lavori edilizi.", body))

    story.append(Paragraph("Perché l'amministratore si è rifiutato:", h2_style))
    for txt in [
        "Produrre un verbale diverso da quello ufficiale per mandarlo alla banca "
        "significherebbe creare un documento alternativo non corrispondente agli atti — "
        "potenzialmente un illecito.",
        "L'amministratore firma personalmente i documenti fiscali del condominio: "
        "se portasse in detrazione €5.840 non detraibili, risponderebbe all'Agenzia "
        "delle Entrate con responsabilità personale.",
        "Ha richiesto chiarimenti scritti da mesi. Non sono mai arrivati.",
    ]:
        story.append(Paragraph(f"• {txt}", bullet))

    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "L'amministratore ha agito correttamente tutelando sé stesso e l'intero condominio. "
        "Non è possibile firmare documentazione di dubbia regolarità senza chiarimenti formali "
        "da parte di Acrobatica e di Banca Sella.",
        note_style))

    # ── STATO ATTUALE ─────────────────────────────────────────────────────────
    story.append(Paragraph("3. Situazione attuale", h1_style))

    items = [
        ("Finanziamento Sella", "NON erogato — bloccato da aprile 2026"),
        ("Fattura d'acconto", "Già pagata dal condominio"),
        ("Lavori", "Partiti a giugno 2026 — colorazione comunicata ad Acrobatica"),
        ("Chiarimenti scritti Acrobatica", "Richiesti da mesi — mai forniti"),
        ("Contratto Acrobatica/Banca Sella", "Mai esibito nonostante le richieste"),
    ]
    data2 = [["Voce", "Stato"]] + [[k, v] for k, v in items]
    t2 = Table(data2, colWidths=[5.5*cm, 12*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c5f8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f0f4f8'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8))

    # ── DOMANDE CHIAVE ────────────────────────────────────────────────────────
    story.append(Paragraph("4. Domande a cui Acrobatica deve rispondere", h1_style))

    domande = [
        ("Cosa sono esattamente i €5.840,78?",
         "Sono la commissione che pagate voi a Sella Personal Credit per il tasso zero? "
         "Mostrate il contratto con la banca."),
        ("Il verbale originale è sufficiente per l'erogazione?",
         "Se mandassimo a Banca Sella il verbale così com'è — senza modifiche — "
         "la banca procederebbe? Se no, perché? Siete disposti a contattare Banca Sella "
         "direttamente in questa riunione per avere una risposta?"),
        ("Questi €5.840 sono detraibili al 50%?",
         "Se sì, fornite una dichiarazione scritta con avallo di Banca Sella. "
         "È quello che l'amministratore chiede da mesi."),
        ("Siete disposti ad assorbire i €5.840 nel vostro prezzo?",
         "Se li toglierete dalla quota dei 5 condomini (come sarebbe corretto per un "
         "vero tasso zero), il problema è risolto per tutti senza ulteriori assemblee."),
    ]

    for i, (titolo, testo) in enumerate(domande, 1):
        story.append(KeepTogether([
            Paragraph(f"<b>{i}. {titolo}</b>", body),
            Paragraph(testo, note_style),
            Spacer(1, 4),
        ]))

    # ── POSSIBILI SOLUZIONI ───────────────────────────────────────────────────
    story.append(Paragraph("5. Possibili soluzioni", h1_style))

    soluzioni = [
        ("Acrobatica rinuncia ai €5.840",
         "Assorbe la commissione nel proprio prezzo. Il verbale va alla banca così "
         "com'è, il finanziamento viene erogato, nessun problema fiscale. "
         "È la soluzione più pulita — quella che avrebbe dovuto applicarsi dall'inizio "
         "per un vero tasso zero."),
        ("I 5 condomini rinunciano al finanziamento",
         "Pagano la loro quota come gli altri condomini, in contanti. "
         "Semplice e immediato. Svantaggio: ~€4.500 a testa da trovare subito."),
        ("Nuova delibera assembleare",
         "L'assemblea ridefinisce i termini: elimina i €5.840 dall'appalto "
         "oppure delibera la rinuncia formale al finanziamento. "
         "Richiede almeno 5 giorni di preavviso per la convocazione."),
    ]

    for titolo, testo in soluzioni:
        story.append(KeepTogether([
            Paragraph(f"✓ <b>{titolo}</b>", green_style),
            Paragraph(testo, note_style),
            Spacer(1, 4),
        ]))

    # ── NOTA FINALE ───────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1,
        color=colors.HexColor('#cccccc'), spaceBefore=8, spaceAfter=8))

    story.append(Paragraph(
        "<b>In sintesi:</b> il finanziamento è bloccato non per capriccio dell'amministratore, "
        "ma perché Acrobatica ha strutturato i €5.840 in modo incompatibile sia con le "
        "condizioni di Banca Sella che con la detraibilità fiscale. "
        "La soluzione richiede un atto concreto da parte di Acrobatica, non una firma "
        "su documentazione irregolare.", note_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Documento informativo — {datetime.now().strftime('%d/%m/%Y')}",
        ParagraphStyle('Footer', parent=styles['Normal'],
            fontSize=8, textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER)))

    doc.build(story)
    print(f"PDF generato: {OUTPUT}")

if __name__ == "__main__":
    build_pdf()
