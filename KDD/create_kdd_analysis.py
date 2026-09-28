import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---- Analysis data ----
# Felder: (ID, Kurzname, Team, Priority, BTP_oder_Ext, Grosser_Change, BTP_Begruendung, Change_Begruendung)
analysis = [
    ('3-50','SD-003 Credit Memo Processing','Verkauf','Medium',False,False,'',''),
    ('3-52','SD-005 Debit Memo Processing','Verkauf','Medium',False,False,'',''),
    ('3-64','CO-032 Projekt-zu-Anlage-Verbuchung','Controlling','Medium',False,True,'','Grundsatzentscheidung CAPEX/OPEX-Trennung nicht im Standard; Audit-Trail-Logik muss neu gestaltet werden'),
    ('3-68','CO-036 Integration Kassenautomaten','Finance','Medium',True,True,'Schnittstelle zu Kassenautomat-Vorsystemen via BTP Integration Suite','Erlösprozess auf Projektbasis; B2C-Massendebitorenabstimmung neu aufzusetzen'),
    ('3-77','SD-008 Invoice Correction Credit Memo','Verkauf','Medium',False,False,'',''),
    ('3-80','FI-GL-05-01 Buchung ausstehender Eingangsrechnungen','Finance','Medium',False,True,'','Buchungslogik wechselt von Rueckstellung auf Sachkonto zu Sonderhauptbuch-Kreditor; Prozess und OP-Verwaltung aendern sich grundlegend'),
    ('KDD-WF','KDD Workflow-Framework (Sammel-KDD, 11 Anforderungen)','Finance','High',True,True,'Grundsatzentscheidung Workflow-Framework: SAP Build Process Automation (BPA) / SAP Task Center auf BTP fuer alle mehrstufigen Genehmigungs- und Freigabeprozesse. Public-Cloud-Standard bietet keinen ausreichend flexiblen, gruppenbasierten Workflow (inkl. Web-/Non-SAP-User, zentrale Genehmiger-Tabelle, Erinnerungslogik).','Betrifft 11 Einzelanforderungen (3-84, 3-99, 3-105, 3-108, 3-118, 3-153, 3-154, 3-155, 3-158, 3-172, 3-205). Ersetzt heutige E-Mail-/SharePoint-basierte Freigaben durch systemgestuetzte Workflows: Rechnungsfreigabe, Debitorenmanagement, Anlagen-Genehmigungen (Verschrottung/Investition), Abgrenzungen. Rollen, Wertgrenzen, Genehmiger-Ermittlung und Web-User-Lizenzen muessen uebergreifend neu definiert werden.'),
    ('3-88','FI-GL-02-01 CSV/Excel-Massenupload Buchungen','Finance','High',False,True,'','Must-Have: heutiger universeller CSV-Upload (alle Kontoarten, spaltenweise) existiert im Standard nicht 1:1; Layout-Entscheidung und Prozessumstellung erforderlich'),
    ('3-90','FI-GL-03-03 Nicht-Standard-Reportings','Finance','Low',True,False,'Custom CDS-Views oder SAP Analytics Cloud (BTP)',''),
    ('3-92','FI-GL-06-01 Rueckstellungsspiegel & Kontenverlauf','Finance','High',False,True,'','Durchgaengige Bewegungsarten-Vergabe je Buchung als neues Muss; aendert Buchungsverhalten und erfordert Schulung'),
    ('3-93','FI-GL-06-02 Altsalden-Migration mit Bewegungsarten','Finance','High',False,False,'',''),
    ('3-96','FI-GL-07-01 MB5L-Pendant MatWirt/FiBu-Abstimmung','Finance','Medium',False,False,'',''),
    ('3-97','FI-AP-01-03 Leistungszeitraum-Feld Eingangsrechnung','Finance','High',True,False,'Key User Extensibility oder BTP Side-by-Side fuer zusaetzliches Feld in CIM',''),
    ('3-100','FI-AP-03-01 E-Mail-Steuerung Zahlungsavis','Finance','Medium',False,False,'',''),
    ('3-101','FI-AP-04-01 Nebenbuch-an-Nebenbuch-Buchungen','Finance','Medium',False,False,'',''),
    ('3-102','FI-AP-04-02 Endrechnungskennzeichen Baurechnungen','Finance','Medium',True,False,'Key User Extensibility oder BTP Side-by-Side fuer benutzerdefiniertes Kennzeichenfeld',''),
    ('3-103','FI-AP-04-04 Dauerbuchung Kreditorenrechnung','Finance','Medium',False,False,'',''),
    ('3-104','FI-AP-05-02 Feldebene-Berechtigungen Rollenkonzept','Finance','Medium',False,False,'',''),
    ('3-106','FI-AP-06-02 Verhindern Direktbuchung (Buchen-Button)','Finance','High',True,False,'UI-Anpassung via Key User Extensibility oder Erweiterung (Feldsichtbarkeit)',''),
    ('3-111','FI-TAX-02-02 Automatischer Storno USt-Zahllast (Batch)','Finance','Medium',False,False,'',''),
    ('3-114','FI-TAX-02-06 Lesbare Auswertung neben XML/CSV Meldungen','Finance','Medium',True,False,'Custom Analytical Query oder SAP Analytics Cloud (BTP)',''),
    ('3-160','FI-AP-04-05 Sicherheitseinbehalte Baurechnungen','Finance','Medium',False,False,'',''),
    ('3-162','FI-AP-05-03 Stammdaten-Governance & Migration','Finance','High',False,True,'','Parallelbetrieb Onventis/Ariba zu klaeren; Governance-Struktur und Pflegregeln muessen neu etabliert werden; Dubletten-Bereinigung im Migration'),
    ('3-171','FI-AR-01-04 E-Mail-Steuerung Korrespondenzarten','Finance','High',False,False,'',''),
    ('3-175','FI-AR-03-02 Recon Hub (Abrantix) Abloesung pruefen','Finance','High',True,True,'S/4HANA native oder SAP Cash Application (BTP) fuer PSP-/Transaktionsdaten-Abgleich','Heute: Recon Hub gleicht Parken-Transaktionsdaten, PSP-Daten und Bankdaten ab; Abloesung = vollstaendig neues Konzept fuer Massendebitorenabstimmung'),
    ('3-176','FI-AR-04-01 Kautionsverwaltung & Verzinsung (Fioport-Abloesung)','Finance','Medium',True,True,'Pruefen: SAP Treasury and Risk Management (TRM) oder externe Kautionsverwaltung','Abloesung Fioport: Kautionsverwaltung inkl. automatischer Verzinsung und Kundenberichten muss vollstaendig neu aufgebaut werden'),
    ('3-178','FI-AR-05-01 Rechnungsnummer vs. Buchungsbelegnummer','Finance','Medium',False,False,'',''),
    ('3-181','FI-BILL-01-01 Sky-Billing-Komplexitaet in Subscription Billing','Finance','High',True,True,'SAP Subscription Billing (BTP-Komponente) oder separates Billing-System als Abloesung Sky Billing','Sky Billing muss vollstaendig neu abgebildet werden: Abstellzeiten, Rollwegzeiten, Maintenance-Interaktionen, heterogene Preiskomponenten'),
    ('3-182','FI-BILL-01-03 Taegliche Stammdaten-Aktualisierung Billing','Finance','High',True,False,'BTP Integration Suite: Tagesschnittstelle Duma -> S/4HANA fuer Triebwerks-/Stammdatenaenderungen',''),
    ('3-184','FI-TAX-01-02 Ertragsteuern / Paragraph 60 Abs.2-Ueberleitung','Finance','Medium',True,False,'BTP Side-by-Side oder Excel-Loesung; kein dediziertes Steuerledger; IFRS-Ledger explizit nicht gewuenscht',''),
    ('3-188','FI-AA-01-01 Granulare Z-Anlagenklassen & Nutzungsdauer','Finance','High',False,True,'','Ueber 20.000 Anlagen betroffen; Z-Anlagenklassen und Z-Tabelle fuer Nutzungsdauer existieren im Standard nicht; Revisionssicherheit und Kontenfindung muessen komplett neu designt werden'),
    ('3-192','FI-AA-02-03 Integration Anlageninventursystem Membrane','Finance','Medium',True,False,'Externe Schnittstelle Membrane <-> S/4HANA (ggf. BTP Integration Suite); Anlagennummer-Uebergabe + Rueckmeldung',''),
    ('3-193','FI-AA-03-01 AIB-Erzeugung aus PSP-Elementen','Finance','High',False,True,'','Heute: je PSP-Element eine AIB -> zu viele; Logik muss mit CO neu definiert werden; beeinflusst Investitionsprozess und spaetere Abrechnung auf fertige Anlage'),
    ('3-197','FI-AA-04-03 Beschaffung mit Anlagenkontierung (Onventis->Ariba)','Finance','Medium',True,False,'Schnittstelle Ariba/Onventis -> S/4HANA fuer PO-Uebergabe mit Anlagen-Kontierung (ggf. BTP)',''),
    ('3-199','FI-AA-06-02 CSV-Upload Eigenleistung & Rueckstellungen','Finance','Medium',False,False,'',''),
    ('3-203','FI-AA-08-02 Query taegliche Rechnungsdurchsicht Anlagevermoegen','Finance','Medium',True,False,'Custom Analytical Query (SAP Analytics Cloud) als Ersatz fuer kundeneigene Z-Query',''),
    ('3-204','FI-AA-08-03 Durchsicht kontierter Bestellungen / Job Bestellliste','Finance','Medium',True,False,'Custom Report oder API-basierter Job als Ersatz fuer Z-Job JOBZMBEST010',''),
    ('3-206','FI-AA-10-01 Filebasierte Migration ~20.000 Anlagen inkl. Historie','Finance','High',False,True,'','Aufwaendige Datenmigration (20.331 Anlagenstammsa tze inkl. Historie): AHK, kumulierte AfA, offene AIB-Posten - Layout und Migrationsvorgehen neu zu planen'),
    ('3-207','FI-GEN-01-01 Archiv & DMS mit Suchfunktion','Finance','High',True,True,'Externes DMS (SAP DMS/OpenText auf BTP) oder Enscale-Nachfolger fuer revisionssicheres Archiv','Abloesung Enscale: uebergreifendes Archiv- und DMS-Konzept muss workstream-uebergreifend neu etabliert werden'),
    ('3-286','SD-021 Fakturaformular Auftragsnummer auf Positionsebene','Verkauf','Medium',False,False,'',''),
    ('3-396','SD-045 ATLED/Unicad Integration via BTP','Verkauf','Medium',True,True,'Explizit BTP Integration Suite: REST/SOAP-Anbindung ATLED fuer automatische Verkaufsauftrags-Anlage via OData-API','Z-Programm ZOM01 existiert in Public Cloud nicht; manueller CSV-Import wird durch vollautomatische BTP-Schnittstelle ersetzt'),
]

# ---- Begruendung fuer Standard/Config-Zeilen (warum KEIN BTP / KEIN grosser Change) ----
std_reasons = {
    '3-50':  'Reine Formularanpassung (Adobe Forms); im Quellsystem explizit als "kein KDD" vermerkt, bei Formularerstellung zu beruecksichtigen. Keine Plattform-Entscheidung, kein Prozess-Change.',
    '3-52':  'Reine Formular-/Kalkulationsschema-Korrektur (Adobe Forms); im Quellsystem als "kein KDD" vermerkt. Keine Plattform-Entscheidung, kein Prozess-Change.',
    '3-77':  'Reine Formularanpassung (Adobe Forms), analog SD-003; im Quellsystem als "kein KDD" vermerkt. Im Standard abbildbar.',
    '3-93':  'Teil der Hauptbuch-Standardmigration; Bewegungsarten (Vortrag) werden im Migrationslauf mitgegeben. Standard-Migrationstaetigkeit ohne separate Loesung.',
    '3-96':  'Standard-App/-Funktion in S/4HANA zu identifizieren und freizuschalten (Abgleich Bestands-/MatWirt-Konten gegen Bilanzsalden). Reine Klaerung/Aktivierung im Standard.',
    '3-100': 'Empfaengerbezogene Steuerung des Zahlungsavis ueber Standard-Korrespondenz-Customizing abbildbar. Keine Plattform-Entwicklung, kein Prozess-Change.',
    '3-101': 'Nebenbuch-an-Nebenbuch-Umbuchung ueber Standard-Workaround (Verrechnungskonto) loesbar; kein eigenes Tool noetig. Standard-Loesungsweg.',
    '3-103': 'Dauerbuchung (wiederkehrende Belege) ist Standard-Funktion; Umsetzbarkeit im Standard zu bestaetigen. Der Workflow-Freigabeanteil faellt unter die Sammel-KDD Workflow-Framework.',
    '3-104': 'Feldbezogene Berechtigungen ueber das Standard-Rollen-/Berechtigungskonzept abbildbar. Standard-Konfiguration.',
    '3-111': 'Pruefung der Standard-Batch-Funktion der App "Zahllast buchen"; Umsetzung innerhalb des Standards, keine Zusatzentwicklung.',
    '3-160': 'Sicherheitseinbehalte ueber Standard-Zahlungssperre/Teilzahlung abbildbar; Konzeption im Standard-Deep-Dive. Keine Plattform-Entwicklung.',
    '3-171': 'Empfaengerbezogene Steuerung der Korrespondenzarten ueber Standard-Customizing je Korrespondenzart abbildbar. Keine Plattform-Entwicklung.',
    '3-178': 'Nummernkonzept-Entscheidung (Config): Buchungsbelegnummer als Rechnungsnummer vs. separates Referenzfeld. Im Standard konfigurierbar; kein Prozess-Change.',
    '3-199': 'Massenupload ueber Standard-App "Hauptbuchbelege hochladen" (F2548/F0718); nur Layout-/Formatpruefung. Standard (Layout-Ueberschneidung mit 3-88).',
    '3-286': 'Reine Formularanpassung (Auftragsnummer auf Positionsebene); separat im Projektverlauf zu betrachten. Im Standard abbildbar.',
}

print(f'Analysierte Anforderungen: {len(analysis)}')
btp_count = sum(1 for a in analysis if a[4])
change_count = sum(1 for a in analysis if a[5])
both_count = sum(1 for a in analysis if a[4] and a[5])
print(f'BTP/Externe Loesung: {btp_count}')
print(f'Grosser Process Change: {change_count}')
print(f'Beides: {both_count}')
print(f'Nur Standard/Config: {len(analysis) - btp_count - change_count + both_count}')

# ---- Load source data for full titles ----
wb_src = openpyxl.load_workbook('Gaps_WRICEF/KDD_Items_For Analysis.xlsx', read_only=True)
ws_src = wb_src['Items_For Analysis']
src_headers = None
src_rows = {}
for i, row in enumerate(ws_src.iter_rows(values_only=True)):
    if i == 0:
        src_headers = list(row)
        continue
    d = dict(zip(src_headers, row))
    src_rows[str(d.get('ID',''))] = d

# ---- Create Excel ----
wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'KDD Analyse'

# Colors
GREEN_DARK  = 'FF006341'  # Deloitte green dark
GREEN_LIGHT = 'FF86BC25'  # Deloitte green light
RED_FILL    = 'FFFFE0E0'  # light red bg
YELLOW_FILL = 'FFFFF2CC'  # light yellow bg
GREEN_FILL  = 'FFE8F5E9'  # very light green bg
GREY_HDR    = 'FF404040'  # dark grey header
WHITE       = 'FFFFFFFF'
RED_STRONG  = 'FFCC0000'
AMBER       = 'FFFF6600'

def hdr_font(bold=True, color='FFFFFFFF', sz=11):
    return Font(bold=bold, color=color, size=sz, name='Calibri')

def cell_font(bold=False, color='FF000000', sz=10):
    return Font(bold=bold, color=color, size=sz, name='Calibri')

def fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)

def thin_border():
    s = Side(style='thin', color='FFD0D0D0')
    return Border(left=s, right=s, top=s, bottom=s)

def wrap_align(h='left', v='top'):
    return Alignment(horizontal=h, vertical=v, wrap_text=True)

# ---- HEADER ROW ----
headers_out = [
    'Nr.',
    'Anforderungs-ID',
    'Titel (Kurz)',
    'Vollstaendiger Titel',
    'Team / Workstream',
    'Prioritaet',
    'BTP / Externe Loesung?',
    'Grosser Prozess-Change?',
    'Einstufung',
    'Begruendung: BTP / Externe Loesung',
    'Begruendung: Prozess-Change',
    'Begruendung (konsolidiert)',
]

ws.row_dimensions[1].height = 40
for col, h in enumerate(headers_out, 1):
    c = ws.cell(row=1, column=col, value=h)
    c.font = hdr_font(sz=10)
    c.fill = fill(GREY_HDR)
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = thin_border()

# Column widths
col_widths = [5, 14, 42, 60, 20, 12, 18, 20, 22, 55, 55, 70]
for i, w in enumerate(col_widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

# ---- DATA ROWS ----
EINSTUFUNG_BTP_ONLY   = 'BTP / Ext. Tool'
EINSTUFUNG_CHANGE_ONLY = 'Process Change'
EINSTUFUNG_BOTH       = 'BTP + Process Change'
EINSTUFUNG_STD        = 'Standard / Config'

PRIO_COLOR = {
    'Very High': ('FFCC0000', 'FFFFFFFF'),
    'High':      ('FFFF6600', 'FFFFFFFF'),
    'Medium':    (YELLOW_FILL, 'FF000000'),
    'Low':       (GREEN_FILL,  'FF000000'),
}

records = []  # fuer JSON-Export

row_num = 2
for i, a in enumerate(analysis):
    id_, short_title, team, prio, is_btp, is_change, btp_reason, change_reason = a
    full_title = src_rows.get(id_, {}).get('Title', '') or short_title

    if is_btp and is_change:
        einstufung = EINSTUFUNG_BOTH
        row_color = 'FFFDE8E8'
    elif is_btp:
        einstufung = EINSTUFUNG_BTP_ONLY
        row_color = 'FFFFF8E1'
    elif is_change:
        einstufung = EINSTUFUNG_CHANGE_ONLY
        row_color = 'FFFE9CC7'
    else:
        einstufung = EINSTUFUNG_STD
        row_color = 'FFF5F5F5'

    # Konsolidierte Begruendung (immer gefuellt)
    parts = []
    if btp_reason:
        parts.append('BTP/Ext.: ' + btp_reason)
    if change_reason:
        parts.append('Change: ' + change_reason)
    if not parts:
        parts.append(std_reasons.get(id_, 'Im S/4HANA-Standard bzw. per Konfiguration abbildbar; keine Plattform-Entscheidung und kein wesentlicher Prozess-Change.'))
    begruendung_konsolidiert = ' | '.join(parts)

    values = [
        i + 1,
        id_,
        short_title,
        full_title,
        team,
        prio,
        'Ja' if is_btp else 'Nein',
        'Ja' if is_change else 'Nein',
        einstufung,
        btp_reason,
        change_reason,
        begruendung_konsolidiert,
    ]

    records.append({
        'nr': i + 1,
        'anforderungs_id': id_,
        'titel_kurz': short_title,
        'titel_vollstaendig': full_title,
        'team_workstream': team,
        'prioritaet': prio,
        'btp_oder_externe_loesung': is_btp,
        'grosser_prozess_change': is_change,
        'einstufung': einstufung,
        'begruendung_btp_externe_loesung': btp_reason,
        'begruendung_prozess_change': change_reason,
        'begruendung_konsolidiert': begruendung_konsolidiert,
    })

    ws.row_dimensions[row_num].height = 55

    for col, val in enumerate(values, 1):
        c = ws.cell(row=row_num, column=col, value=val)
        c.font = cell_font()
        c.fill = fill(row_color)
        c.border = thin_border()
        c.alignment = wrap_align('center' if col in (1,6,7,8) else 'left')

        # Prio color
        if col == 6:
            prio_bg, prio_fg = PRIO_COLOR.get(prio, (row_color, '00000000'))
            c.fill = fill(prio_bg)
            c.font = cell_font(bold=True, color=prio_fg)

        # BTP Ja/Nein
        if col == 7:
            if is_btp:
                c.font = cell_font(bold=True, color='FF006341')
            else:
                c.font = cell_font(color='FF888888')

        # Change Ja/Nein
        if col == 8:
            if is_change:
                c.font = cell_font(bold=True, color='FFCC0000')
            else:
                c.font = cell_font(color='FF888888')

        # Einstufung
        if col == 9:
            if einstufung == EINSTUFUNG_BOTH:
                c.font = cell_font(bold=True, color='FFCC0000')
            elif einstufung == EINSTUFUNG_BTP_ONLY:
                c.font = cell_font(bold=True, color='FF006341')
            elif einstufung == EINSTUFUNG_CHANGE_ONLY:
                c.font = cell_font(bold=True, color='FF8B0000')
            else:
                c.font = cell_font(color='FF888888')

    row_num += 1

# ---- SUMMARY SHEET ----
ws2 = wb.create_sheet('Zusammenfassung')
ws2.column_dimensions['A'].width = 40
ws2.column_dimensions['B'].width = 12
ws2.column_dimensions['C'].width = 60

s_data = [
    ('Kategorie', 'Anzahl', 'Hinweis'),
    ('Gesamt analysierte Anforderungen', len(analysis), ''),
    ('BTP oder externe Loesung benoetigt', btp_count, 'Umsetzung ausserhalb S/4HANA Standard'),
    ('Grosser Prozess-Change', change_count, 'Wesentliche Aenderung bestehender Ablaeufe'),
    ('BTP + Prozess-Change (kombiniert)', both_count, 'Hoechste Komplexitaet - KDD-Kandidaten priorisiert betrachten'),
    ('Nur Standard / Configuration', len(analysis) - btp_count - change_count + both_count, 'Im Standard abbildbar'),
]

for ri, row_vals in enumerate(s_data, 1):
    ws2.row_dimensions[ri].height = 30
    for ci, val in enumerate(row_vals, 1):
        c = ws2.cell(row=ri, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap_align('center' if ci == 2 else 'left', 'center')
        if ri == 1:
            c.font = hdr_font(sz=11)
            c.fill = fill(GREY_HDR)
        else:
            c.font = cell_font(sz=11)
            if row_vals[0] == 'BTP + Prozess-Change (kombiniert)':
                c.fill = fill('FFFDE8E8')
                c.font = cell_font(bold=True, sz=11, color='FFCC0000')
            elif row_vals[0] == 'BTP oder externe Loesung benoetigt':
                c.fill = fill('FFFFF8E1')
                c.font = cell_font(bold=True, sz=11, color='FF006341')
            elif row_vals[0] == 'Grosser Prozess-Change':
                c.fill = fill('FFFE9CC7')
                c.font = cell_font(bold=True, sz=11, color='FF8B0000')

# ---- BTP-Liste Sheet ----
ws3 = wb.create_sheet('BTP & Externe Tools')
ws3.column_dimensions['A'].width = 14
ws3.column_dimensions['B'].width = 50
ws3.column_dimensions['C'].width = 20
ws3.column_dimensions['D'].width = 70

btp_hdr = ['ID', 'Titel', 'Prioritaet', 'BTP-Begruendung / Externe Tool']
ws3.row_dimensions[1].height = 35
for ci, h in enumerate(btp_hdr, 1):
    c = ws3.cell(row=1, column=ci, value=h)
    c.font = hdr_font(sz=10)
    c.fill = fill(GREEN_DARK)
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = thin_border()

ri = 2
for a in analysis:
    id_, short_title, team, prio, is_btp, is_change, btp_reason, change_reason = a
    if not is_btp:
        continue
    ws3.row_dimensions[ri].height = 50
    for ci, val in enumerate([id_, short_title, prio, btp_reason], 1):
        c = ws3.cell(row=ri, column=ci, value=val)
        c.font = cell_font()
        c.fill = fill('FFFFF8E1')
        c.border = thin_border()
        c.alignment = wrap_align('center' if ci == 3 else 'left')
        if ci == 3:
            prio_bg, prio_fg = PRIO_COLOR.get(prio, ('FFFFFFFF', '00000000'))
            c.fill = fill(prio_bg)
            c.font = cell_font(bold=True, color=prio_fg)
    ri += 1

# ---- Process Change Sheet ----
ws4 = wb.create_sheet('Grosse Process Changes')
ws4.column_dimensions['A'].width = 14
ws4.column_dimensions['B'].width = 50
ws4.column_dimensions['C'].width = 20
ws4.column_dimensions['D'].width = 70

chg_hdr = ['ID', 'Titel', 'Prioritaet', 'Begruendung Prozess-Change']
ws4.row_dimensions[1].height = 35
for ci, h in enumerate(chg_hdr, 1):
    c = ws4.cell(row=1, column=ci, value=h)
    c.font = hdr_font(sz=10)
    c.fill = fill('FF8B0000')
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = thin_border()

ri = 2
for a in analysis:
    id_, short_title, team, prio, is_btp, is_change, btp_reason, change_reason = a
    if not is_change:
        continue
    ws4.row_dimensions[ri].height = 55
    for ci, val in enumerate([id_, short_title, prio, change_reason], 1):
        c = ws4.cell(row=ri, column=ci, value=val)
        c.font = cell_font()
        c.fill = fill('FFFDE8E8')
        c.border = thin_border()
        c.alignment = wrap_align('center' if ci == 3 else 'left')
        if ci == 3:
            prio_bg, prio_fg = PRIO_COLOR.get(prio, ('FFFFFFFF', '00000000'))
            c.fill = fill(prio_bg)
            c.font = cell_font(bold=True, color=prio_fg)
    ri += 1

output_path = 'KDD_Analyse_Ergebnis.xlsx'
wb.save(output_path)
print(f'\nGespeichert: {output_path}')

# ---- JSON-Export (fuer KI-/maschinelle Weiterverarbeitung) ----
import json
json_payload = {
    'meta': {
        'quelle': 'KDD_Items_For Analysis.xlsx',
        'projekt': 'JURI - SAP S/4HANA Public Cloud',
        'anzahl_anforderungen': len(records),
        'anzahl_btp_oder_extern': btp_count,
        'anzahl_grosser_prozess_change': change_count,
        'anzahl_btp_und_change': both_count,
        'anzahl_standard_config': len(analysis) - btp_count - change_count + both_count,
        'einstufung_werte': [EINSTUFUNG_BTP_ONLY, EINSTUFUNG_CHANGE_ONLY, EINSTUFUNG_BOTH, EINSTUFUNG_STD],
        'hinweis_sammel_kdd': 'Die Zeile mit ID "KDD-WF" fasst 11 Workflow-Anforderungen zusammen (3-84, 3-99, 3-105, 3-108, 3-118, 3-153, 3-154, 3-155, 3-158, 3-172, 3-205).',
    },
    'anforderungen': records,
}
json_path = 'KDD_Analyse_Ergebnis.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(json_payload, f, ensure_ascii=False, indent=2)
print(f'Gespeichert: {json_path}')
