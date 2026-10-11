# F2S-Workshop 3 – Debitorenstammdaten, manuelle und automatisierte Kundenrechnung, Buchung und Basis-Konfiguration Debitorenbuchhaltung

Vorbereitung für den Berater (Finance), 3 Stunden, SAP S/4HANA Cloud Public Edition Release 2608.
Basis: Testskripte und Set-Up-Guides im Ordner `LOH/3_F2SWS` (Stand Juni 2026).

| Scope Item | Titel | Rolle im Workshop |
|---|---|---|
| J59 | Accounts Receivable | Kern des Workshops: Debitorenstamm aus FI-Sicht, Rechnung ohne Auftragsbezug (FB70), Massenupload (F4051), Buchung, Posten, Korrespondenz, Vorbereitungsschritte (Konfiguration) |
| BD6 | Basic Credit Management | Ergänzung zum Debitorenstamm: Kreditprofil, Kreditlimit, Kreditprüfung im Kundenauftrag, Freigabe gesperrter Aufträge (Documented Credit Decision) |

**Wichtige Lücken im Ordner, vorab klären:**
- **Anlage des Debitorenstamms** ist in J59 nur als Pflege eines vorhandenen Geschäftspartners beschrieben (Manage Customer Master Data F0850A). Die Neuanlage steckt im Master Data Script BND (Create Customer Master), das nicht im Ordner liegt. Für den Workshop reicht es, die Neuanlage in der Demo über Maintain Business Partner (BP) oder F0850A zu zeigen und die Governance-Fragen (wer legt an, welche Felder, welche Nummern) zu diskutieren.
- **Automatisierte Rechnungserstellung** heißt in J59 zweierlei: (1) Rechnungen, die aus Vertriebsprozessen automatisch in die Buchhaltung kommen (Faktura aus BD9 Sell from Stock, J14 Project-Based Services, BDN Order-Specific Procurement, alle als Business Condition in J59 genannt, keines im Ordner) und (2) der Massenupload von Kundenrechnungen über Excel (Upload Customer Open Items F4051). Die SD-Faktura selbst ist ein Vertriebsthema; aus Finance-Sicht erklären, wie der Buchhaltungsbeleg entsteht, und im Demosystem einen vorhandenen Fakturabeleg über die Prozessfluss-App zeigen.
- **Mahnen, Zahlungseingang, Collections** sind in J59 enthalten, gehören aber in Workshop 4 (Ordner `4_F2SWS`: J59 erneut, 2PD, BFC, 7MA). Hier nur als Ausblick, damit der Kunde die Prozesskette versteht.
- Die beiden **Set-Up-Guides sind für LOH nicht relevant**: J59 Set-Up beschreibt nur die China-spezifische Bankbeleganforderung (SAP_COM_0554), BD6 Set-Up nur die systemübergreifende Integration des Kreditmanagements zwischen zwei S/4HANA-Cloud-Systemen (SAP_COM_0B25 / SAP_COM_0173). Beides im Workshop nur erwähnen, falls jemand fragt, ob Kommunikationsszenarien eingerichtet werden müssen: Für ein einzelnes Public-Cloud-System nein.

---

## Teil A – Prozesserklärungen

### A1. Debitorenstammdaten (Geschäftspartner mit Rolle Kunde)

**Grundidee.** In S/4HANA Cloud gibt es keinen separaten Debitorenstamm mehr. Der Kunde ist ein Geschäftspartner (Business Partner, BP) mit Rollen. Die Nummer des Geschäftspartners ist zugleich die Debitorennummer. Die Nummernvergabe steuert die BP-Gruppierung (intern oder extern), die Gruppierungen sind in der Public Cloud vorgeliefert und werden in der Konfiguration ausgewählt, nicht frei definiert.

| Datenebene | Rolle im BP | Inhalt | Verantwortung (typisch) |
|---|---|---|---|
| Allgemeine Daten | alle Rollen | Name, Adresse, Kommunikation (E-Mail für Rechnungs- und Mahnversand), Steuernummern, USt-IdNr., Bankverbindungen, Identifikationsnummern, Zertifikate (optional) | Stammdaten-Team |
| Buchungskreisdaten | FLCU00 Customer (Fin. Accounting) | Abstimmkonto (im YCOA z. B. 12100000 Forderungen Inland, im System prüfen), Zahlungsbedingung, Zahlwege, Hausbank, Zinskennzeichen, Kennzeichen Zahlungsverhalten aufzeichnen, Sachbearbeiter (Accounting Clerk), Korrespondenz, Mahnverfahren, Mahnsperre, Mahnsachbearbeiter | Debitorenbuchhaltung |
| Vertriebsbereichsdaten | FLCU01 Customer (Sales) | Verkaufsorganisation, Vertriebsweg, Sparte, Preisfindung, Versand, Fakturadaten, Partnerrollen | Vertrieb |
| Kreditmanagement | UKM000 Credit Management (BD6) | Kreditprofil: Scoring, Risikoklasse, Prüfregel; je Kreditsegment: Kreditlimit, Gültigkeit, Kreditanalyst | Credit Controller |

**Apps und Rollen (J59).**
- Manage Customer Master Data (F0850A), Rolle Master Data Specialist – Business Partner Data (SAP_BR_BUPA_MASTER_SPECIALIST). Fiori-Sicht auf den Kunden mit Registern Company Codes (darin Finance, Correspondence, Dunning Data) und Sales Areas. J59 nutzt sie, um am Demokunden 10100001 Sachbearbeiter, Internetadresse des Sachbearbeiters, Zinskennzeichen 01, Zahlungsverhalten aufzeichnen und Mahnverfahren 1001 zu pflegen.
- Maintain Business Partner (BP), Rolle AR Accountant oder Master Data Specialist. Klassische Transaktion mit allen Rollen; J59 nutzt sie für das Register Certificates (Geschäftspartner-Zertifikate, länderspezifisch, nur nach Aktivierung in der Konfiguration).
- Display Customer List (F2640), Rolle AR Accountant. Liste je Buchungskreis mit Stadt, Telefon, E-Mail, Sachbearbeiter, Zahlungsbedingung, Mahnverfahren, Mahnsperre. Gedacht für die Stammdatenprüfung (Lücken finden) und als Absprung in Posten, Ausgleich, Mahnung.
- Define Accounting Clerks (S_ALR_87003335), Rolle AR Manager. Sachbearbeiter je Buchungskreis: zweistelliges Kürzel, Name, Benutzer. Der Sachbearbeiter steuert, wessen Mahnvorschläge in My Dunning Proposals erscheinen, und ist Auswertungsdimension in allen AR-KPIs.

**Massenanlage und Migration (nicht im Ordner, Standardwissen).** Für den Cut-over werden Debitoren über die Migrate Your Data App (Migrationsobjekt Customer) geladen, nicht manuell. Für laufende Massenänderungen gibt es die Mass-Maintenance-Apps für Geschäftspartner. Für Neuanlagen im Tagesgeschäft sollte der Kunde einen Anlageprozess mit Rollen und Pflichtfeldern definieren; die Public Cloud bietet dafür optional den Geschäftspartner-Genehmigungsworkflow (Business Partner Governance).

**Kreditprofil (BD6).** Basic Credit Management ist ohne Zusatzlizenz enthalten. Es prüft beim Anlegen oder Ändern eines Kundenauftrags (und bei Lieferungen) das Obligo des Kunden gegen das Kreditlimit im Kreditsegment und optional weitere Regeln (ältester offener Posten, höchste Mahnstufe, letzte Zahlung). Das Obligo setzt sich aus offenen Aufträgen, Lieferungen, Fakturen und FI-Posten zusammen.
- Manage Credit Accounts (F4596), Rolle Credit Controller (SAP_BR_CREDIT_CONTROLLER): Register Scoring (Berechnungsregel, Risikoklasse z. B. Medium Default Risk, Prüfregel 01 Default – alle Prüfungen aktiv), Register Credit Segments (Segment 1000, Kreditlimit, gültig bis), Kreditanalyst zuordnen (Mitarbeiterstamm nötig). Limitwährung ist immer die Konzernwährung aus der Aktivierung.
- Die Kreditmanagement-Rolle kann per Job massenhaft an Geschäftspartner vergeben werden (Schedule Credit Management Jobs F3748, Vorlage „Assign Credit Management Role to Business Partners“), ebenso Regeländerungen („Update Rules for Scoring and Credit Check“).
- Fällt die Prüfung negativ aus, wird der Auftrag gesperrt und das System legt eine Documented Credit Decision (DCD) an. Manage Documented Credit Decision – New Version (F5587A): Fall einem Kreditanalysten zuordnen, auf „In Process“ setzen, Release (mit Freigabenotiz) oder Reject (mit Ablehnungsgrund). Nach Release ist der Auftrag wieder lieferbar.
- Wiederholte Prüfung per Job „Check Credit on SD Documents“ (F3748, typischerweise täglich): gesperrte Aufträge werden automatisch frei, wenn der Kunde inzwischen gezahlt hat; freie Aufträge werden erneut gesperrt, wenn inzwischen Posten überfällig sind.
- Reporting: Display Credit Account Data (F4825, Sperrgrund, Obligo, Limit, Auslastung in Prozent), Display Credit Exposure (F4826), Analyze Credit Exposure – By Country (F2541), Display Credit Management Log (F2162), Credit Limit Utilization – gt 80 % (F1751).
- Wartungsjobs (Delete / Rebuild Credit Management Data F4802, F4234; Send Delta of Payment Behavior Summary) sind keine Tagesarbeit und im Workshop nur zu nennen. Feature FIN_FSCM_REBUILD_DCD muss in Activate Features aktiv sein.
- Botschaft für den Kunden: Eine FB70-Rechnung erhöht zwar das Obligo, eine Kreditsperre entsteht aber nur in Vertriebsbelegen mit kreditaktiver Positionsart. Ohne SD-Prozess ist BD6 nur ein Reporting-Instrument.

### A2. Manuelle Kundenrechnung ohne Auftragsbezug (FB70)

**Grundidee.** Die Debitorenbuchhaltung erfasst eine Rechnung direkt in der Finanzbuchhaltung, ohne Kundenauftrag und ohne Faktura. Typische Fälle: Weiterberechnungen, Schadenersatz, Mieten und Nebenkosten, Verkäufe von Anlagen, Rechnungen aus Systemen ohne Schnittstelle, Korrekturen. Das System erzeugt sofort einen Buchhaltungsbeleg (Journal Entry) mit Belegart DR und einen offenen Posten beim Kunden.

**App.** Create Outgoing Invoices (FB70), Rolle Accounts Receivable Accountant (SAP_BR_AR_ACCOUNTANT). Gutschriften analog über Create Outgoing Credit Memos (Belegart DG).

**Ablauf in der App (nach J59).**
1. Buchungskreis wählen (1010).
2. Basisdaten: Kunde, Rechnungsdatum, Buchungsdatum, Referenz (Rechnungsnummer des Kunden bzw. eigene Nummer, erscheint auf Korrespondenz und ist Suchkriterium beim Zahlungseingang), Betrag brutto, Währung, Kennzeichen „Steuer rechnen“. Bei aktivem RITA zusätzlich Steuerland.
3. Register Zahlung: Basisdatum, Zahlungsbedingung (0001 sofort fällig), Zahlweg optional. Hieraus leitet das System das Nettofälligkeitsdatum ab, Grundlage für Mahnung, Zinsen, DSO.
4. Positionen: Sachkonto 41000400 (Erlöse), Haben, Betrag, Steuerkennzeichen (Ausgangssteuer, z. B. A1 für 19 %, im Demosystem prüfen).
5. Ergebnisobjekt: Weil das Erlöskonto als Kostenart Typ Erlös angelegt ist, verlangt das System ein Ergebnisobjekt (margin analysis). Über den Button Profitability Segment Kunde und Profit Center eingeben, „Derivation“ wählen, übernehmen.
6. Simulieren (optional) und Buchen. Ergebnis: Journal Entry, Belegnummer in der Erfolgsmeldung.

**Buchungslogik.**

| Zeile | Soll | Haben | Herkunft |
|---|---|---|---|
| Kunde (Abstimmkonto Forderungen) | Bruttobetrag | – | Kundenstamm, Abstimmkonto |
| Erlöse 41000400 | – | Nettobetrag | Eingabe, Ergebnisobjekt |
| Ausgangssteuer | – | Steuerbetrag | Steuerkennzeichen, automatische Kontenfindung |

**Varianten, die Kunden meistens fragen.**
- Vorerfassen (Park) und später buchen; in der Public Cloud gibt es für Kundenrechnungen keinen Genehmigungsworkflow wie für Sachkontenbelege (Verify General Journal Entries). Vier-Augen-Prinzip also organisatorisch oder über Vorerfassung.
- Rechnung in Fremdwährung (Kurs aus Kurstabelle, Belegwährung ungleich Hauswährung).
- Abweichender Zahlungsregulierer, abweichender Rechnungsempfänger (Partnerrollen im Stamm).
- Anzahlungsanforderung statt Rechnung: Manage Customer Down Payment Requests (F1689), Sonderhauptbuchkennzeichen A, später Verrechnung mit der Schlussrechnung (J59 Abschnitt Down Payments).
- Skonto über Zahlungsbedingung; Teilzahlungen und Restposten erst beim Zahlungseingang (Workshop 4).

**Rechnungsausgabe aus FI.** Die FB70-Rechnung hat keine SD-Nachricht. Der Ausdruck läuft über die Korrespondenzart SAP21 (FI Customer Invoice): Create Correspondence (F0744A) mit Journal Entry und Geschäftsjahr, oder direkt aus Manage Journal Entries (F0717A) über Create Correspondence. Vorschau, Druck, E-Mail. Voraussetzung ist die BRF+-Ausgabesteuerung für „Accounting Document“ (siehe A5): Ausgabeart INVOICE, Empfängerrolle BP, Kanäle PRINT und EMAIL, Formularvorlage FIN_FO_CORR_FICUS_INV, E-Mail-Vorlage FIN_CUSINV_EMAIL_TEMPL, Absenderadresse. Versandte Korrespondenz ist in Display Correspondence History (F2934) nachvollziehbar. Weitere Korrespondenzarten für Kunden: SAP06 Kontoauszug, SAP08 Offene-Posten-Liste, SAP09 Interner Beleg (Erfassungs- oder Hauptbuchsicht), SAP13 Kundenkontoauszug.

**Nach der Buchung.**
- Manage Customer Line Items (F0711): offene, ausgeglichene oder alle Posten, Fälligkeit, Mahndaten, Zahlsperre; Edit Line Items ändert Zahlungsdaten, Mahndaten, Zusatzdaten. Administrator kann über Custom Fields (F1481) weitere Felder einblenden.
- Display Customer Balances (F0703A): Salden je Periode, Sonderhauptbuch, Vergleich.
- Display Process Flow – Accounts Receivable (F2692): Kette Kundenauftrag, Lieferung, Faktura, Journal Entry, Ausgleich. Für FB70-Belege zeigt die App nur Journal Entry und späteren Ausgleich.
- Storno: Manage Journal Entries (F0717A), Reverse mit Stornogrund, Buchungsdatum, Steuermeldedatum. Falsch ausgeglichene Posten zuerst über Reset Cleared Items (F2223) zurücknehmen (Reset oder Reset and Reverse).
- Änderungen an Posten: Display Item Change Log – Customer (F7796).

### A3. Automatisierte Rechnungserstellung

**Weg 1: Faktura aus dem Vertrieb (Standardfall in J59).** Der Buchhaltungsbeleg entsteht automatisch beim Freigeben der Faktura (Belegart RV). Kontenfindung für Erlöse, Erlösschmälerungen und Steuer kommt aus der SD-Kontenfindung (Kontoschlüssel, Kontierungsgruppen aus Material und Kunde), die Zahlungsbedingung aus dem Kundenauftrag, das Abstimmkonto aus dem Kundenstamm. Der Rechnungsdruck läuft über die Nachrichtensteuerung der Faktura, nicht über SAP21. Die Debitorenbuchhaltung bucht nichts, sie übernimmt den offenen Posten. Der Posten trägt die Fakturanummer als Referenz und ist damit für Zahlungszuordnung, Mahnung und Kreditobligo verknüpft. Im Workshop: Prozessfluss-App (F2692) mit einem vorhandenen Fakturabeleg zeigen; zuständig für Fakturierungsregeln, Fakturasperren und Sammelfakturen ist der SD-Berater. J59 setzt voraus, dass BD9, J14 oder BDN vorher gelaufen sind.

**Weg 2: Massenupload von Kundenrechnungen (J59 Abschnitt Mass Upload).** Für viele Ausgangsrechnungen ohne Auftragsbezug und für Abgrenzungen.
- App Upload Customer Open Items (F4051), Rolle AR Accountant.
- Vorlage in der App herunterladen (Sprache, Format xlsx). Maximal 500 Positionen je Datei.
- Kopfdaten je Beleg: Belegsequenznummer (manuell fortlaufend), Buchungskreis, Vorgang 1 Rechnung oder 2 Gutschrift, Kunde, Referenz (16 Zeichen), Belegdatum, Buchungsdatum (im Format der Vorlage, laut Skript MM/DD/YYYY), Belegart DR oder DG, Kopftext (25 Zeichen), Währung, Bruttobetrag.
- Sachkontenpositionen: Sachkonto (41000400), Positionstext (50 Zeichen), S/H, Betrag, Steuerkennzeichen, Profit Center (YB700), optional Reporting Segment und Funktionsbereich (sonst Ableitung aus Stammdaten).
- Ablauf: Datei hochladen, Positionen erscheinen in der Arbeitsliste als Entwurf; Check, Log anzeigen, Fehler in der Kundenrechnungs-App korrigieren (Entwurf wird grün), Post. Erst Post erzeugt Journal Entries.
- Voraussetzung aus den Vorbereitungsschritten: Manage Default Account Assignments (Buchungskreis, Kostenart 41000400, Kennzeichen Ergebnisobjekt), damit der Upload das Ergebnisobjekt automatisch ableitet. Ohne diesen Eintrag bleiben die Positionen im Check hängen.
- Typische Einsatzfälle: Rechnungen aus einem Vorsystem ohne Schnittstelle (Abrechnungssystem, Portal), periodische Weiterbelastungen, Abgrenzungen, Korrektur-Gutschriften in Masse. Nicht für den Cut-over der offenen Posten (dafür Migrationscockpit).

**Weg 3: Schnittstelle (nicht im Ordner, Standardwissen).** Externe Fakturierungssysteme buchen über die SOAP-API Journal Entry – Post (Kommunikationsszenario SAP_COM_0002) oder über die OData-APIs für Kundenrechnungen. Vorteil gegenüber Upload: kein manueller Schritt, Fehlerbehandlung über Message Monitoring. Für LOH klären, ob es solche Vorsysteme gibt.

**Weg 4: Periodische Buchungen.** Dauerbuchungen (Manage Recurring Journal Entries) sind in J58 beschrieben und für Mietrechnungen oder Wartungspauschalen nutzbar. Nur erwähnen.

### A4. Buchung und Folgeprozesse (Überblick, Vertiefung in Workshop 4)

| Schritt | App | Rolle | Was passiert |
|---|---|---|---|
| Offener Posten überwachen | Manage Customer Line Items (F0711), Display Customer Balances (F0703A) | AR Accountant | Fälligkeit, Mahnstufe, Zahlsperre, Zuordnung |
| Zahlungseingang automatisch | Reprocess Bank Statement Items (F1520), Regeln (F3555, F9062, F9297), optional Cash Application Intelligence (1MV) | Cash Management Specialist | Kontoauszug (BFB) ordnet Zahlungen über Referenz und Regeln den Posten zu; Rest manuell nachbearbeiten |
| Zahlungseingang manuell | Post Incoming Payments (F1345), Clear Incoming Payments – Manual Clearing (F0773) | AR Accountant | Bank an Kunde mit Ausgleich; Zahlungsavise (F2550A) als Hilfe |
| Korrektur | Reset Cleared Items (F2223), Manage Journal Entries (F0717A) | AR / GL Accountant | Ausgleich zurücknehmen, Beleg stornieren |
| Mahnen | Create Dunning Notices (F150), My Dunning Proposals (F2435), Display Dunning History (F2328) | AR Accountant | Mahnverfahren 1001 (alle 14 Tage, 4 Stufen) oder 1002 (30 Tage nach Rechnung); Workshop 4 |
| Zinsen | Schedule Interest Calculation Jobs (F4176), Manage Interest Runs (F4485) | AR Accountant | Postenzinsen über Zinskennzeichen 01 |
| Periodisch | Saldenbestätigung (F2366, F2834), Write Off Receivables (F6728), Guarantees Made (F7934) | AR Accountant | Jahresabschluss, Ausbuchung mit Grundcode, Avale |
| Steuern | Accounts Receivable Overview (F3242), Overdue Receivables (F1747, F2539), Future / Total Receivables (F1744, F1748), DSO (F1741), Days Beyond Terms (F1739), Dunning Level Distribution (F1742), Cash Collection Tracker (F2925) | AR Manager | KPIs mit Drilldown nach Buchungskreis, Kunde, Sachbearbeiter |

### A5. Basis-Konfiguration Debitorenbuchhaltung (SSCUI bzw. SAP Central Business Configuration)

Alles im Folgenden ist Standardkonfiguration, die der Configuration Expert (SAP_BR_BPC_EXPERT) über Manage Your Solution oder das CBC-Projekt pflegt. Die Spalte „Quelle“ nennt, woher der Punkt kommt.

| Konfigurationspunkt | Inhalt | Quelle |
|---|---|---|
| Sachbearbeiter (Accounting Clerks) | Kürzel je Buchungskreis mit Benutzer; Pflicht für Mahnvorschläge und Auswertungen | J59 Preliminary Steps |
| Zahlungsbedingungen | Vorgeliefert u. a. 0001 sofort fällig; weitere nach Bedarf (Skonto, Tage, Monatsmitte) | Standard, J59 nutzt 0001 |
| Belegarten und Nummernkreise | DR Kundenrechnung, DG Kundengutschrift, DZ Zahlungseingang, DA Debitorenbeleg (Avale, Anzahlungsanforderung), RV Faktura; Nummernkreise in der Public Cloud fix | J59 |
| Abstimmkonten und Kontenfindung | Abstimmkonto je Kunde im Stamm; Automatic Account Determination für Zahlungsvorgänge, z. B. Vorgangsschlüssel ZDI mit Grundcode 200 auf Konto 62010000 für Forderungsausbuchung | J59 Assign Reason Codes For Write-Off |
| Default Account Assignments | Buchungskreis, Kostenart 41000400, Ergebnisobjekt aktiv; Voraussetzung für den Upload | J59 Manage Default Account Assignments |
| Ausgabesteuerung (BRF+, Output Parameter Determination) | Je Ausgabeobjekt die Schritte Output Type, Receiver, Channel, Form Template, Output Relevance, Printer Settings, Email Settings. Für Accounting Document: INVOICE, SAP21, FIN_FO_CORR_FICUS_INV, FIN_CUSINV_EMAIL_TEMPL. Für Balance Confirmation: LETTER und CHECKLIST mit FIN_FO_BLNC_CNFRM_LTTR / _CHKLST. Für Item Interest Calculation: INTEREST_LETTER mit FFO_ITEM_INTEREST_LETTER_D / _C. Für Dunning: DUNN_NOTICE je Mahnverfahren und Mahnstufe | J59 BRF+ Settings |
| Formulare und E-Mail-Vorlagen | Maintain Form Templates (F1434): Standardvorlage herunterladen, mit Adobe LiveCycle Designer anpassen, als YY1_-Vorlage hochladen; Assign Form Templates und Assign Email Templates (Application Object Type FFO_DUNN, Output Type DUNN_NOTICE) | J59 BRF+ Settings for Dunning Notice |
| Mahnverfahren | 1001 und 1002 vorgeliefert; Mahnstufen, Mahngebühren, Mindestbeträge, Sperrgründe (Disputed, Promise to Pay, Legal, …) | J59, Workshop 4 |
| Zinskennzeichen | 01 Postenzinsen, Zinssätze und Berechnungsregeln | J59 Interest Calculation |
| Geschäftspartner-Zertifikate | Activate Business Partner Certificates Functionality, Define Certificate IDs, Assign Certificates to Country (Pflicht, Anhang, Gültigkeit) | J59, nur wenn gesetzlich nötig |
| Situation Handling | 31N aktivieren, Situationstyp aus Vorlage FIN_PAYMENTADVICEINVOICESKIPPED kopieren (Rechnung im Zahlungsavis übersprungen) | J59 optional |
| Erweiterbarkeit | Custom Fields (F1481), Data Source Extension Customer Line Items | J59 optional |
| RITA | Registrierung für indirekte Steuern im Ausland ohne eigenen Buchungskreis; blendet in FB70 und F4051 das Feld Steuerland ein | J59 optional |
| Kreditmanagement | Kreditsegmente (Create Credit Segment, FLEXIBLE_CHECK), Risikoklassen, Prüfregeln (01 alle Prüfungen), Activate Features FIN_FSCM_REBUILD_DCD; Kommunikationsszenarien nur bei Systemverbund | BD6 |
| Rollen | SAP_BR_AR_ACCOUNTANT, SAP_BR_AR_MANAGER, SAP_BR_BUPA_MASTER_SPECIALIST, SAP_BR_CREDIT_CONTROLLER, SAP_BR_GL_ACCOUNTANT, SAP_BR_CASH_SPECIALIST, SAP_BR_BPC_EXPERT, SAP_BR_ADMINISTRATOR; Launchpad Spaces „Accounts Receivable“ und „Credit Management“ | J59, BD6 |

Nicht in den Skripten, aber bei Basis-AR-Konfiguration regelmäßig gefragt: Toleranzgruppen für Zahlungsdifferenzen (Kunde und Sachbearbeiter), Restpostenbildung und Grundcodes für Abzüge, Zahlwege und SEPA-Mandate (BKX), Buchungsperioden (J58), Feldstatus im Geschäftspartner (Pflichtfelder je Rolle und Gruppierung). Als Fragen in Teil D aufgenommen.

### A6. Prozesskette (für die Einstiegsfolie)

| Schritt | Herkunft | Instrument | Workshop |
|---|---|---|---|
| Kunde anlegen und pflegen | Stammdaten-Team, Vertrieb, Buchhaltung | BP, F0850A, F2640, F4596 (Kreditprofil) | 3 |
| Rechnung manuell | Buchhaltung | FB70, Korrespondenz SAP21 | 3 |
| Rechnung aus Vertrieb | SD-Faktura | Belegart RV, Prozessfluss F2692 | 3 (Erklärung), SD-Workshops |
| Rechnung in Masse | Buchhaltung, Vorsystem | F4051 Upload, API | 3 |
| Offener Posten, Beleg prüfen | Buchhaltung | F0711, F0703A, F0717A, Storno | 3 |
| Konfiguration | Configuration Expert | SSCUI / CBC | 3 |
| Zahlung, Ausgleich, Avise | Bank, Buchhaltung | F1520, F1345, F0773 | 4 |
| Mahnen, Collections, Wertberichtigung | Buchhaltung | F150, F2435, BFC/7MA, 2PD | 4 |

---

## Teil B – Agenda (180 Minuten)

| Zeit | Block | Inhalt | Format |
|---|---|---|---|
| 0:00–0:15 | Einstieg | Ziel, Scope Items J59 und BD6, Rollen, Prozesskette A6, Abgrenzung zu Workshop 4 und zu den SD-Workshops | Präsentation |
| 0:15–0:45 | Debitorenstamm | Prozess A1, Demo 1 (F0850A, BP, F2640, Kreditprofil F4596, DCD F5587A) | Demo + Fragen |
| 0:45–1:00 | Fit-to-Standard Teil 1 | Stammdaten-Governance, Pflichtfelder, Nummern, Abstimmkonten, Zahlungsbedingungen, Sachbearbeiter, Kreditmanagement ja/nein | Diskussion |
| 1:00–1:25 | Manuelle Rechnung | Prozess A2, Demo 2 (FB70, Journal Entry, Posten, Korrespondenz SAP21, Storno) | Demo + Fragen |
| 1:25–1:35 | Pause | | |
| 1:35–2:05 | Automatisierte Rechnung | Prozess A3, Demo 3 (Prozessfluss einer SD-Faktura, Upload F4051 mit Check, Log, Korrektur, Buchen) | Demo + Fragen |
| 2:05–2:20 | Fit-to-Standard Teil 2 | Rechnungsquellen, Upload-Einsatz, Vorsysteme, Ausgabekanal und Formular, Steuerkennzeichen, Erlöskonten und Profit-Center-Ableitung | Diskussion |
| 2:20–2:45 | Buchung und Basis-Konfiguration | Prozess A4 (Ausblick) und A5, Demo 4 (F0711, F0703A, F3242, Konfigurationsrundgang) | Demo + Fragen |
| 2:45–3:00 | Fit-to-Standard Teil 3 und Abschluss | Belegarten, Korrespondenzarten, Toleranzen, Zinsen, Saldenbestätigung, Entscheidungsliste, offene Punkte, nächste Schritte | Diskussion, Entscheidungsliste |

---

## Teil C – Demo-Ablauf

### C0. Vorbereitung am Vortag (Pflicht)

Stammdaten aus den Skripten: Buchungskreis 1010, Kontenplan YCOA, Kostenrechnungskreis A000, Kunden 10100001 und 10100002 (J59), Kunde 10100005 mit Kreditprofil (BD6), Kreditsegment 1000, Erlöskonto 41000400, Profit Center YB700, Kostenstelle 10101101, Hausbank DEBK1 / Konto DEAC1, Bankkonto 11001060 (in den Buchungsschritten; die Stammdatentabelle nennt 11001000), Zahlungsbedingung 0001, Mahnverfahren 1001, Zinskennzeichen 01. Vor dem Workshop im Demosystem prüfen, ob diese Werte existieren.

Checkliste:
1. Benutzer mit Rollen: Master Data Specialist – Business Partner Data, AR Accountant, AR Manager, GL Accountant, Credit Controller, Configuration Expert. Am besten ein Demo-User mit allen Rollen; für den Konfigurationsrundgang den Configuration-Expert-Zugang zum Q-System oder CBC bereithalten.
2. Buchungsperioden offen (J58), Steuermeldedatum zulässig.
3. Sachbearbeiter in Define Accounting Clerks mit dem Demo-User angelegt (z. B. Kürzel 01). Kunde 10100001 bereits mit Sachbearbeiter, Internetadresse, Zinskennzeichen 01, Zahlungsverhalten aufzeichnen und Mahnverfahren 1001 gepflegt; in Demo 1 wird dann nur eine Änderung live gezeigt (z. B. Mahnsperre setzen und wieder entfernen).
4. Zweiten Kunden ohne vollständige Buchungskreisdaten vorbereiten, damit F2640 Lücken zeigt (oder Demo mit vorhandenen Lücken im Demosystem).
5. Default Account Assignment für 1010 / 41000400 mit Ergebnisobjekt eingetragen und mit einem Testupload geprüft.
6. BRF+-Regeln für Accounting Document (INVOICE, SAP21) vollständig aktiviert, Druckwarteschlange DEFAULT vorhanden, Absenderadresse hinterlegt. Vorschau einer SAP21-Korrespondenz am Vortag testen; ohne diese Regeln bringt die Vorschau in Demo 2 nur eine Fehlermeldung.
7. Upload-Datei für Demo 3 fertig und getestet: drei Rechnungen (DR, Vorgang 1) und eine Gutschrift (DG, Vorgang 2) für 10100001 und 10100002, eine Zeile mit absichtlichem Fehler (z. B. fehlendes Steuerkennzeichen), damit Check, Log und Korrektur gezeigt werden können. Datumsformat der Vorlage beachten, Sequenznummern fortlaufend, Bruttobetrag gleich Summe der Positionen.
8. Für den Prozessfluss in Demo 3 einen vorhandenen Fakturabeleg aus BD9 heraussuchen (Belegart Faktura, Nummer notieren). Wenn das Demosystem keinen hat: mit dem SD-Kollegen am Vortag einen Auftrag bis zur Faktura durchbuchen, sonst Screenshots.
9. BD6: Kunde 10100005 mit Scoring, Risikoklasse, Prüfregel 01 und Kreditlimit in Segment 1000. Für einen gesperrten Auftrag das Limit nach Skript bewusst klein setzen (5,00) und einen Kundenauftrag aus BD9 anlegen, damit in F5587A ein DCD-Fall liegt. Kreditanalyst (Mitarbeiter) zugeordnet. Feature FIN_FSCM_REBUILD_DCD aktiv.
10. Fallback: Screenshots jeder Demo-App und ein gebuchtes Beispiel je Demo, falls Buchungen im Workshop scheitern.

### C1. Demo 1 – Debitorenstamm und Kreditprofil (ca. 20 Minuten)

Story: Neuer Kunde wird vom Vertrieb angelegt, die Buchhaltung ergänzt die Buchungskreisdaten, der Credit Controller setzt das Kreditlimit.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | Master Data Specialist | Manage Customer Master Data (F0850A) | Kunde 10100001 suchen, Detail öffnen | Allgemeine Daten, Adressen, Kommunikation (E-Mail für Rechnung und Mahnung), Steuernummern |
| 2 | Master Data Specialist | F0850A, Register Company Codes, 1010 | Register Finance: Abstimmkonto, Zahlungsbedingung, Zinskennzeichen 01, Zahlungsverhalten aufzeichnen | Welche Felder FI steuern |
| 3 | Master Data Specialist | F0850A, Register Correspondence und Dunning Data | Edit: Sachbearbeiter prüfen, Mahnverfahren 1001, Mahnsperre kurz setzen, Apply, Save; danach wieder entfernen | Pflege im Fiori-Objekt, Änderungsbelege |
| 4 | Master Data Specialist | F0850A, Register Sales Areas | Vertriebsbereichsdaten nur zeigen | Trennung FI / SD, Verantwortung |
| 5 | AR Accountant | Maintain Business Partner (BP) | 10100001 in Rolle Customer (Fin. Accounting) anzeigen, Rollenliste, optional Register Certificates | Rollenkonzept FLCU00 / FLCU01 / UKM000, Gruppierung und Nummer |
| 6 | AR Accountant | Display Customer List (F2640) | Buchungskreis 1010, Go | Lückenprüfung (fehlende E-Mail, Sachbearbeiter, Mahnverfahren), Absprung über Kundennummer in Posten und Ausgleich |
| 7 | Credit Controller | Manage Credit Accounts (F4596) | 10100005: Register Scoring (Regel, Risikoklasse, Prüfregel 01), Credit Segments 1000 mit Limit und Gültigkeit, Kreditanalyst | Was das Kreditprofil ist, Limitwährung |
| 8 | Credit Controller | Display Credit Account Data (F4825) | 10100005, Segment 1000 | Obligo, Limit, Auslastung, Sperrgrund |
| 9 | Credit Controller | Manage Documented Credit Decision – New Version (F5587A) | 10100005, Segment 1000, gesperrten Auftrag öffnen, Set To In Process, Release mit Notiz (oder Reject zeigen) | Wie eine Kreditsperre aufgelöst wird, Protokoll |
| 10 | Credit Controller | Schedule Credit Management Jobs (F3748) | Vorlage „Check Credit on SD Documents“ nur zeigen | Tägliche Nachprüfung |

Fragen an die Teilnehmer nach Demo 1: Wer legt heute Kunden an, in welchem System? Welche Felder sind heute Pflicht? Gibt es Kreditlimits, wer entscheidet bei Überschreitung?

### C2. Demo 2 – Manuelle Rechnung ohne Auftragsbezug (ca. 20 Minuten)

Story: Weiterberechnung einer Beratungsleistung an 10100001 über 1.000 EUR netto, 19 % Steuer, brutto 1.190 EUR, sofort fällig.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | AR Accountant | Create Outgoing Invoices (FB70) | Buchungskreis 1010; Kunde 10100001, Rechnungs- und Buchungsdatum heute, Referenz z. B. WS3-001, Betrag 1.190 EUR, Steuer rechnen | Kopfdaten, Bedeutung der Referenz |
| 2 | AR Accountant | FB70, Register Zahlung | Basisdatum heute, Zahlungsbedingung 0001 | Fälligkeitslogik |
| 3 | AR Accountant | FB70, Positionen | Sachkonto 41000400, Haben, 1.190, Steuerkennzeichen Ausgangssteuer 19 % | Steuer wird aus dem Bruttobetrag herausgerechnet |
| 4 | AR Accountant | FB70, Profitability Segment | Kunde 10100001, Profit Center, Derivation, Continue | Warum das Ergebnisobjekt nötig ist |
| 5 | AR Accountant | FB70, Simulate, dann Post | Buchen | Belegnummer, Belegart DR |
| 6 | GL Accountant | Manage Journal Entries (F0717A) | Beleg öffnen | Zeilen Kunde / Erlöse / Steuer, Abstimmkonto, Ergebnisobjekt |
| 7 | AR Accountant | Manage Customer Line Items (F0711) | 10100001, 1010, offene Posten | Fälligkeit, Referenz, Mahndaten, Zahlsperre; Edit Line Items kurz öffnen |
| 8 | AR Accountant | F0717A, Create Correspondence oder Create Correspondence (F0744A) | SAP21 FI Customer Invoice, Journal Entry, Geschäftsjahr, Preview | PDF-Rechnung aus FI, Optionen Print und E-Mail |
| 9 | AR Accountant | Display Correspondence History (F2934) | 1010, Kunde | Nachweis des Versands |
| 10 | AR Accountant | Display Process Flow – Accounts Receivable (F2692) | Belegart Journal Entry, Belegnummer | Nur Journal Entry, kein Vertriebsbeleg; Ausgleich fehlt noch |
| 11 | GL Accountant | F0717A, Reverse | Nur Dialog zeigen (Stornogrund, Buchungsdatum), nicht ausführen; Posten bleibt für Workshop 4 | Stornoprozess |

Fragen an die Teilnehmer nach Demo 2: Welche Rechnungen entstehen heute ohne Auftrag, wie viele pro Monat? Wer darf buchen, gibt es ein Vier-Augen-Prinzip? Wie wird die Rechnung heute verschickt (Papier, E-Mail, Portal)?

### C3. Demo 3 – Automatisierte Rechnungserstellung (ca. 25 Minuten)

Story Teil a: Ein Kundenauftrag aus BD9 wurde geliefert und fakturiert, die Buchhaltung sieht den Posten ohne eigenes Zutun.
Story Teil b: Das Abrechnungssystem für Nebenkosten liefert monatlich eine Liste mit 400 Rechnungen; die Buchhaltung lädt sie hoch.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | AR Accountant | Display Process Flow – Accounts Receivable (F2692) | Belegart Faktura, vorbereitete Fakturanummer, 1010 | Kette Kundenauftrag, Lieferung, Faktura, Journal Entry; Belegart RV |
| 2 | AR Accountant | Manage Customer Line Items (F0711) | Posten zur Faktura | Referenz gleich Fakturanummer, Zahlungsbedingung aus Auftrag |
| 3 | GL Accountant | Manage Journal Entries (F0717A) | Faktura-Journal-Entry öffnen | Erlöskonten aus SD-Kontenfindung, Steuer, Ergebnisobjekt automatisch |
| 4 | Erklärung | – | Nachrichtensteuerung der Faktura, Rolle des SD-Beraters, Schnittstelle als Alternative | Grenze Finance / SD |
| 5 | AR Accountant | Upload Customer Open Items (F4051) | Download Template (xlsx) öffnen | Aufbau Kopf und Positionen, Sequenznummer, DR/DG, 500 Positionen je Datei |
| 6 | AR Accountant | F4051, Browse | Vorbereitete Datei hochladen | Arbeitsliste mit Status Entwurf |
| 7 | AR Accountant | F4051, Check, Show Log | Alle markieren, prüfen | Grüne Flaggen, eine rote Zeile mit Fehlermeldung |
| 8 | AR Accountant | F4051, fehlerhafte Zeile öffnen | Steuerkennzeichen ergänzen, zurück zur Arbeitsliste | Korrektur in der Kundenrechnungs-App, Status wird grün |
| 9 | AR Accountant | F4051, Post | Alle buchen | Journal Entries je Zeile |
| 10 | AR Accountant | Manage Customer Line Items (F0711) | 10100001 und 10100002 | Neue offene Posten, Gutschrift als Habenposten |
| 11 | Configuration Expert | Manage Your Solution, Manage Default Account Assignments | Eintrag 1010 / 41000400 / Ergebnisobjekt zeigen | Warum der Upload ohne Ergebnisobjekt-Dialog durchläuft |

Kernaussage: Drei Wege in denselben offenen Posten. Der Kunde entscheidet je Rechnungsquelle, welcher Weg gilt; Upload ist der Mittelweg zwischen manueller Erfassung und Schnittstelle.

### C4. Demo 4 – Buchung, Auswertung und Konfigurationsrundgang (ca. 20 Minuten)

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | AR Accountant | Display Customer Balances (F0703A) | 10100001, 1010, aktuelles Jahr; Views Balances, Special GL | Saldenentwicklung, Sonderhauptbuch (Anzahlungen, Avale) |
| 2 | AR Manager | Accounts Receivable Overview (F3242) | EUR, Intervalle 30/60/90, 1010 | Karten AR Aging, DSO, Top 10 Debtors, Cash Collection Tracker; Ausblick Workshop 4 |
| 3 | AR Manager | Display Item Change Log – Customer (F7796) | 1010, heute | Änderung aus Demo 2 Schritt 7 nachvollziehen (falls dort etwas geändert wurde) |
| 4 | Configuration Expert | Manage Your Solution, Configure Your Solution | Define Accounting Clerks | Sachbearbeiter als Steuerungsobjekt |
| 5 | Configuration Expert | Finance, General Settings, Journal Entries | Manage Default Account Assignments | Siehe Demo 3 |
| 6 | Configuration Expert | Finance, General Ledger, Chart of Accounts | Automatic Account Determination: Define Accounts for Payment Transactions, Schlüssel ZDI, YCOA, Grundcode 200 | Kontenfindung für Ausbuchung, Prinzip der Kontenfindung |
| 7 | Administrator | Output Parameter Determination (APOC_WD_BRF_DEC_TAB_MAINTAIN) | Show Rules for Accounting Document, Schritte Output Type, Channel, Form Template | Wie die FI-Rechnung ihr Formular und ihren Kanal findet |
| 8 | Administrator | Maintain Form Templates (F1434) | Predelivered Templates FIN_FO_CORR_FICUS_INV und FIN_FO_DUNN_NOTE, Custom Templates YY1_ | Formularanpassung mit Adobe LiveCycle Designer |
| 9 | Configuration Expert | Zahlungsbedingungen und Mahnverfahren (SSCUI) | Nur anzeigen, 0001, 1001, 1002 | Was in Workshop 4 vertieft wird |
| 10 | Configuration Expert | Activate Features | FIN_FSCM_REBUILD_DCD | Feature-Aktivierung als Konfigurationsschritt in BD6 |

Alle Konfigurationsschritte nur zeigen, nichts ändern. Änderungen gehören ins CBC-Projekt und in die Entscheidungsliste.

---

## Teil D – Fit-to-Standard-Fragen und Entscheidungsbedarf (KDD-Kandidaten)

**Debitorenstammdaten**
1. Wer legt Kunden an (Vertrieb, Stammdaten-Team, Buchhaltung) und in welcher Reihenfolge werden allgemeine Daten, Vertriebsbereich und Buchungskreis gepflegt? Genehmigungsworkflow für Geschäftspartner gewünscht?
2. BP-Gruppierungen und Nummernvergabe: interne Nummern oder Übernahme der Altnummern (extern) für migrierte Kunden?
3. Pflichtfelder je Rolle (E-Mail für Rechnungs- und Mahnversand, USt-IdNr., Bankverbindung, Sachbearbeiter, Mahnverfahren) und Dublettenprüfung.
4. Abstimmkonten: Inland, Ausland, verbundene Unternehmen, Mitarbeiter als Debitoren, Einmalkunden.
5. Zahlungsbedingungen: Liste der benötigten Bedingungen mit Skonto und Fälligkeitslogik; Standard im Kundenstamm.
6. Zahlwege: Überweisung, SEPA-Lastschrift (Mandate, BKX), Kreditkarte; Hausbank je Kunde.
7. Sachbearbeiterstruktur: nach Kundengruppen, Regionen, Buchstaben; gleicher Sachbearbeiter für Mahnung und Korrespondenz?
8. Zinskennzeichen und Zahlungsverhalten aufzeichnen als Standard?
9. Geschäftspartner-Zertifikate nötig (länderspezifische Anforderungen)?
10. Kreditmanagement: BD6 aktiv nutzen? Kreditsegmente (eins oder je Geschäftsbereich), Risikoklassen, Prüfregel, Kreditlimits je Kundengruppe, wer gibt gesperrte Aufträge frei, Kreditanalysten als Mitarbeiterstamm.

**Manuelle Rechnung**
11. Welche Rechnungsfälle laufen ohne Kundenauftrag und wie viele pro Monat?
12. Erlöskonten und Kontierung für diese Fälle; Profit-Center-Ableitung und Ergebnisobjekt-Merkmale (Kunde, Produkt, Region).
13. Steuerkennzeichen: Inland, EU, Drittland, steuerfrei; RITA nötig?
14. Vorerfassung und Freigabe: wer erfasst, wer bucht; reicht Vorerfassung ohne Workflow?
15. Rechnungsausgabe aus FI: Druck oder E-Mail, Absenderadresse, Formular anpassen (Logo, Fußzeile, Sprachen), Korrespondenzarten SAP06/08/13 für Kontoauszüge.
16. Referenz- und Kopftext-Konventionen, damit Zahlungseingang und Mahnung sauber zuordnen können.

**Automatisierte Rechnung**
17. Welche Rechnungen kommen aus dem Vertrieb (SD-Faktura), welche aus Vorsystemen, welche manuell? Mengengerüst je Quelle.
18. Vorsysteme: Schnittstelle (API) oder Upload (F4051)? Verantwortung für Upload, Prüfung und Buchung; Dateiformat und 500er-Grenze.
19. Gutschriften in Masse über Upload (DG) zulässig?
20. Cut-over: offene Posten über Migrationscockpit, nicht über Upload; Stichtag und Abstimmung mit Altsystem.
21. Konzerninterne Rechnungen: Intercompany-Prozess oder manuelle FB70?

**Buchung und Basis-Konfiguration**
22. Belegarten und Referenzpflicht; Buchungsperioden-Steuerung für Debitoren (J58).
23. Toleranzgruppen für Zahlungsdifferenzen und Restposten (Kunde, Sachbearbeiter), Grundcodes für Abzüge, Konten für kleine Differenzen.
24. Ausbuchung uneinbringlicher Forderungen: Grundcodes, Konten (ZDI), Betragsgrenzen, Freigabe.
25. Zinsberechnung auf Posten: ja/nein, Zinssätze, Mindestbeträge, Versandkanal.
26. Saldenbestätigung zum Jahresabschluss: Verfahren (mit oder ohne Rückantwort), Formular, Versand.
27. Situation Handling (31N) und Custom Fields für Posten gewünscht?
28. Rollenzuschnitt: wer bekommt AR Accountant, AR Manager, Credit Controller, Configuration Expert.

**Ausblick Workshop 4**
29. Zahlungseingang über Kontoauszug (BFB), Regeln, Cash Application Intelligence (1MV, Zusatzlizenz).
30. Mahnverfahren, Mahnstufen, Mahnsperren, Collections und Disputes (BFC, 7MA, Zusatzlizenz), Wertberichtigung (2PD).

---

## Teil E – Fallstricke aus den Skripten

- FB70: Ohne Ergebnisobjekt lässt sich die Erlösposition nicht buchen. In der Demo den Profitability-Segment-Dialog bewusst zeigen, nicht überspringen.
- F4051: Ohne Default Account Assignment für das Erlöskonto bleibt der Upload im Check stehen. Sequenznummern sind manuell fortlaufend, Belegart muss zum Vorgang passen (1/DR, 2/DG), Datumsformat der Vorlage prüfen, maximal 500 Positionen je Datei. Hochgeladene Zeilen sind Entwürfe des hochladenden Benutzers; erst Post bucht.
- SAP21-Vorschau funktioniert nur mit vollständig aktivierten BRF+-Regeln für Accounting Document (alle Schritte inklusive Output Relevance und Printer Settings). Am Vortag testen.
- Formularanpassung braucht Adobe LiveCycle Designer (Install Additional Software F1261); im Starter-System ist Key-User-Extensibility für neue Vorlagen deaktiviert (SAP-Hinweis 2283716).
- J59 verlangt für die Mahndemo Posten, die überfällig sind, und eine Mahnhistorie, die mindestens 14 Tage alt ist. Deshalb Mahnen bewusst in Workshop 4, dort rechtzeitig überfällige Posten erzeugen (Buchungsdatum in der Vergangenheit).
- BD6: Das Skript setzt das Kreditlimit auf 5,00, damit der Auftrag sicher sperrt. Limitwährung ist die Konzernwährung. Kreditprüfung greift nur in Vertriebsbelegen mit kreditaktiver Positionsart; FB70-Belege sperren nichts. Das Skript nennt in einem Schritt Kunde 10100011, überall sonst 10100005; mit 10100005 arbeiten.
- BD6: DCD-Bearbeitung braucht einen Kreditanalysten mit Mitarbeiterstamm. Vorher anlegen, sonst scheitert Schritt „Assign Credit Analyst“.
- Set-Up-Guides: J59 nur China (SAP_COM_0554), BD6 nur Systemverbund (SAP_COM_0B25 / SAP_COM_0173). Nicht als Pflichtaufgabe für LOH kommunizieren.
- Manage Payment Advices (F2550) ist als deprecated markiert; in Workshop 4 die neue Version F2550A verwenden.
- Demodaten: Vorgelieferte Demodaten im Starter- oder Partnersystem nicht inkompatibel ändern (Hinweis in beiden Skripten), sonst drohen Aktivierungsfehler bei Scope-Erweiterungen. Für die Demo eigene Referenzen und kleine Beträge verwenden.
- Buchungsperioden (J58) und Steuermeldedatum vor dem Workshop prüfen; die häufigste Ursache für eine scheiternde Live-Buchung.
- App-IDs für Create Outgoing Credit Memos, die Zahlungsbedingungs- und Mahnverfahrens-SSCUIs sowie die Mass-Maintenance-Apps für Geschäftspartner wurden hier ohne F-Nummer genannt und sollten im Demosystem per App Finder geprüft werden.
