# F2S-Workshop 2 – PO-basierte Rechnungserfassung, Three-Way-Match, GR/IR-Monitoring (ML), SES-Accruals, PO-Accruals

Vorbereitung für den Berater (Finance), 2 Stunden, SAP S/4HANA Cloud Public Edition Release 2608.
Basis: Testskripte im Ordner `LOH/2_F2SWS`.

| Scope Item | Titel | Rolle im Workshop |
|---|---|---|
| J60 | Accounts Payable | Rahmen: Kreditorenbuchhaltung, Zahlsperren, Prozessfluss-App |
| 2V7 | Monitoring of Goods and Invoice Receipts | GR/IR-Monitor (Fiori-Apps F3302 / F3303 / F5796), Situation Handling |
| 2ZS | Machine Learning for Monitoring of Goods and Invoice Receipts | ML-Statusvorschläge für den GR/IR-Monitor (Intelligent Scenario FI_GRIR_RECONCILE) |
| 2VB | Purchase Order Accruals | Bestellabgrenzungen über die Accrual Engine (Komponente POAC) |
| 63L | Service Entry Sheet Based Accruals | Abgrenzung auf Basis nicht freigegebener Leistungserfassungsblätter (Komponente SSAC) |

**Wichtige Lücke im Ordner:** Die PO-basierte Rechnungserfassung selbst (Logistik-Rechnungsprüfung mit Three-Way-Match) ist kein eigenes Finance-Scope-Item. Sie steckt in den Procurement-Scope-Items J45 (Procurement of Direct Materials), BNX (Consumable Purchasing, dort auch der flexible Workflow für Lieferantenrechnungen) und 22Z (Procurement of Services, Lean Service / Leistungserfassungsblatt). J60 setzt J45 ausdrücklich voraus („Invoices are created and posted to accounting“). Für den Workshop reicht es, den Prozess aus Finance-Sicht zu erklären und in der Demo eine Bestellung, einen Wareneingang und eine PO-Rechnung zu buchen. Wenn der Procurement-Berater im Workshop sitzt, Verantwortung für Toleranzen und Sperrgründe klar abstimmen.

---

## Teil A – Prozesserklärungen

### A1. PO-basierte Rechnungserfassung (Logistik-Rechnungsprüfung)

**Grundidee.** Die Rechnung wird nicht frei kontiert, sondern gegen die Bestellung erfasst. Das System schlägt Positionen, Mengen, Preise, Kontierung und Steuerkennzeichen aus Bestellung und Bestellentwicklung (Wareneingänge) vor. Der Buchhalter prüft nur noch Abweichungen.

**App.** Create Supplier Invoice (F0859), Rolle Accounts Payable Accountant (SAP_BR_AP_ACCOUNTANT). Referenz wählbar: Bestellung, Lieferschein, Leistungserfassungsblatt, Lieferant. Übersicht und Nachbearbeitung über Supplier Invoices List bzw. Manage Supplier Invoices.

**Ablauf in der App.**
1. Kopfdaten: Vorgang „Rechnung“, Rechnungssteller, Buchungskreis, Bruttobetrag, Währung, Rechnungs- und Buchungsdatum, Referenz (Lieferantenrechnungsnummer, Grundlage der Doppelerfassungsprüfung).
2. Bezug: Bestellnummer eingeben, Positionen werden vorgeschlagen. Bei WE-bezogener Rechnungsprüfung (Kennzeichen „GR-based IV“ in Bestellposition bzw. Lieferantenstamm) schlägt das System je Wareneingang eine Zeile vor, sonst die noch nicht fakturierte Bestellmenge.
3. Saldo prüfen: Rechnungsbetrag minus Summe Positionen plus Steuer muss null sein. Grüne Ampel = buchbar.
4. Buchen. Ergebnis: Logistik-Rechnungsbeleg (MM) plus Buchhaltungsbeleg (Journal Entry). J60 weist darauf hin, dass die Belegnummer in der App die Logistiknummer ist. Die FI-Belegnummer findet man über Manage Supplier Line Items (F0712).

**Varianten, die Kunden meistens fragen.**
- Vorerfassen (Park) und später buchen, inkl. Freigabe über den flexiblen Workflow für Lieferantenrechnungen (Aktivierung ist in BNX beschrieben).
- Nachbelastung / Nachentlastung (Subsequent Debit/Credit) für nachträgliche Preisänderungen ohne Mengenbezug.
- Gutschrift mit Bestellbezug (Credit Memo) bei Rückgabe oder Preisnachlass.
- Rechnungskürzung (Invoice Reduction) bei Lieferantenfehler: System bucht Rechnung wie vom Lieferanten gestellt und erzeugt automatisch eine Gutschrift über die Differenz.
- Nicht geplante Bezugsnebenkosten (unplanned delivery costs).
- Rechnungen ohne Bestellbezug (J60-Standardfall, freie Kontierung mit Sachkonto und Kostenstelle) und Einmallieferanten.

**Buchungslogik (Standardfall Lagermaterial oder kontierte Verbrauchsbestellung).**

| Schritt | Soll | Haben | Bewertung |
|---|---|---|---|
| Wareneingang (WE) | Bestand bzw. Aufwand/Kostenstelle | WE/RE-Verrechnungskonto (GR/IR) | WE-Menge × Bestellpreis |
| Rechnungseingang (RE) | WE/RE-Verrechnungskonto + Vorsteuer | Kreditor | Rechnungsmenge × Rechnungspreis |
| Preisabweichung | Bestand (gleitender Preis) oder Preisdifferenzkonto / Aufwand | – | Rechnungspreis minus Bestellpreis |

Das GR/IR-Konto ist damit ein Verrechnungskonto: Es geht genau dann auf null, wenn WE-Menge und RE-Menge zu einer Bestellposition übereinstimmen. Im Kontenplan YCOA ist das Standardkonto 21310000 (Verbindlichkeiten aus WE/RE), offene-Posten-geführt mit Einkaufsbelegnummer und Position als Zuordnung.

### A2. Three-Way-Match (Bestellung / Wareneingang / Rechnung)

**Was geprüft wird.** Beim Buchen der Rechnung vergleicht das System die Rechnungsposition mit Bestellung und Wareneingängen:
- **Preis**: Rechnungspreis gegen Bestellpreis (Toleranzschlüssel PP, absoluter und prozentualer Grenzwert).
- **Menge**: Rechnungsmenge gegen gelieferte, noch nicht fakturierte Menge (Toleranzschlüssel DQ, Mengenabweichung bewertet mit Preis).
- **Termin**: Rechnung vor Lieferdatum (DW, Terminabweichung).
- **Betrag je Position** (AN, AP) und **Gesamtbetrag** (BD, kleiner Differenzbetrag, der automatisch auf ein Konto für kleine Differenzen gebucht wird).

Zwei-Wege-Abgleich (nur Bestellung gegen Rechnung) entsteht in der Public Cloud, wenn für die Bestellposition kein Wareneingang vorgesehen ist (Kennzeichen „Wareneingang“ nicht gesetzt, typisch bei bestimmten Dienstleistungen, Lizenzen, Abos). Bei Lean Services ist das Leistungserfassungsblatt (Service Entry Sheet, SES) der „Wareneingang“: Erst die Freigabe des SES erzeugt die WE-Buchung, erst danach lässt sich die Rechnung gegen das SES prüfen.

**Was bei Abweichung passiert.** Die Rechnung wird gebucht, aber mit Zahlsperre R (Sperre aus Rechnungsprüfung) versehen. Der Kreditor hat einen offenen Posten, der Zahllauf greift ihn nicht. Die Sperrgründe (Preis, Menge, Termin, Qualität) stehen am Beleg. Freigabe über die App Release Blocked Invoices durch den AP Accountant, entweder manuell oder automatisch, wenn der Sperrgrund entfällt (z. B. Wareneingang wird nachgebucht). Zusätzlich gibt es manuelle Zahlsperren auf Lieferanten- oder Postenebene über Manage Payment Blocks (F0593A), siehe J60 Abschnitt 4.5.2.

**Toleranzen in der Public Cloud.** Die Toleranzgrenzen je Buchungskreis sind Konfiguration (SSCUI „Set Tolerance Limits“ im Bereich Invoice Verification). Vorbelegt sind Werte für 1010. Im Workshop klären: Wer darf welche Abweichungen freigeben, welche Prozent- und Absolutgrenzen sind gewünscht, soll es „kleine Differenzen“ geben.

**Transparenz.** Display Process Flow – Accounts Payable (F2691, J60 Anhang) zeigt Bestellung, Warenbewegung, Rechnung, Journal Entry und Ausgleich als Prozesskette und zeigt fehlende Objekte. Gute Demo-App, um den Three-Way-Match sichtbar zu machen.

### A3. GR/IR-Monitoring mit ML-Unterstützung (2V7 + 2ZS)

**Problem.** Jede Bestellposition, bei der WE-Menge und RE-Menge nicht übereinstimmen, lässt einen Saldo auf dem GR/IR-Konto stehen. Typische Ursachen: Teillieferung ohne Restlieferung, Rechnung vor Lieferung, Lieferant stellt zu viel oder zu wenig in Rechnung, Bestellung läuft aus, Wareneingang vergessen. Die Buchhaltung muss zum Periodenende entscheiden: Lieferung anmahnen, Rechnung anfordern, Gutschrift anfordern, Bestellung schließen oder Rest abschreiben.

**Klassische Hilfsmittel (nicht Teil des Ordners, aber Standardfunktionen).**
- Automatisches Ausgleichen des GR/IR-Kontos (Job in Schedule General Ledger Jobs, F.13-Logik): gleicht Posten aus, deren Saldo je Bestellposition null ist.
- Saldenumgliederung GR/IR zum Stichtag (F.19-Logik): „geliefert, nicht berechnet“ als Verbindlichkeit, „berechnet, nicht geliefert“ als Forderung auswerten, am nächsten Tag Storno.
- Pflege des GR/IR-Kontos (MR11-Logik): Restmengen abschreiben, wenn keine Rechnung oder keine Lieferung mehr erwartet wird.

**Der GR/IR-Monitor (2V7) setzt davor an.** Drei Apps für den General Ledger Accountant (SAP_BR_GL_ACCOUNTANT):

| App | Zweck |
|---|---|
| Reconcile GR/IR Accounts (F3302) | Arbeitsliste je Einkaufsbeleg mit Registern Übersicht (WE-Menge, RE-Menge, Werte), FI-Posten, Bestellentwicklung, Kontakte (Einkäufer, Lieferant), Notizen. Über „Process Item“ wird der Fall mit Bearbeitungsstatus, Priorität, Abteilung, Bearbeiter, Ursache und Notiz an den Verantwortlichen geschickt. |
| Monitor GR/IR Account Reconciliation – Overview (F3303) | KPI-Übersicht: offene FI-Posten nach Buchungskreis, Buchungsdatum, Lieferant; Bestellpositionen mit WE-Überschuss, RE-Überschuss, WE gleich RE, Prozessinformationen. Drilldown nach Kostenrechnungskreis, Buchungskreis, Profit Center, Lieferant, Werk, Einkaufsorganisation, Warengruppe. |
| GR/IR Process Insights (F5796) | Auswertung der abgeschlossenen Fälle: Statusübergänge, Verteilung nach Status, Abteilung, Bearbeiter, Priorität, Ursache. |

Bearbeitungsstatus sind z. B. „Request Completion of Delivery“, „Request Invoice“, „Request Credit Memo“, „Close Purchase Order“, „Write Off“. Die Ursachen (Root Cause) wie „Incomplete goods receipt“ sind die Trainingsgrundlage für das ML-Modell.

**Situation Handling (optional, Scope Item 31N nötig).** Zwei vorgelieferte Situationsvorlagen:
- FIN_GRIRPROCESSORCHANGED: Benachrichtigung an den neuen Bearbeiter, sobald ihm ein Fall zugewiesen wird.
- FIN_GRIRDEVIATIONEXCEEDSTRHSHLD: Benachrichtigung, wenn der Saldo einer Bestellposition einen Schwellwert überschreitet, per Batch-Job, Empfänger über Teams (Manage Teams and Responsibilities F2412, Teamtyp FIGRIR, Verantwortung nach Buchungskreis).

**ML-Unterstützung (2ZS).** Das Intelligent Scenario FI_GRIR_RECONCILE schlägt für jeden offenen Fall Status, Priorität, Ursache, Abteilung und Bearbeiter vor. Grundlage ist die Historie der manuell bearbeiteten Fälle aus F3302.
- Voraussetzungen: 2V7 aktiv, 2ZS aktiv (Aktivierung per Ticket auf XX-S4C-OPR-SRV), SAP-managed Kommunikationsszenario SAP_COM_1042 aktiv, mindestens 100 manuell bearbeitete GR/IR-Fälle als Trainingsdaten.
- Rolle Analytics Specialist: Intelligent Scenario Management (F4470), Modell trainieren (Filter z. B. Buchungskreis, Zielfelder GRIRCLEARINGPROCESSSTATUS, …PRIORITY, …ROOTCAUSE, RESPONSIBLEDEPARTMENT, RESPONSIBLEPERSON), Training deployen, Deployment aktivieren (für alle oder nur für mich).
- Rolle GL Accountant: Job „Prepare GR/IR Status Predictions (DAR ML model)“ in Schedule General Ledger Jobs (F1927) einplanen. Danach erscheinen die Vorschläge in F3302 und können übernommen oder geändert werden.
- Botschaft für den Kunden: ML ersetzt nicht die Entscheidung, es reduziert die Bearbeitungszeit, indem es Routinefälle vorbelegt. Es braucht Betriebsdaten; in den ersten Monaten nach Go-live läuft der Monitor ohne ML. Qualität der Root-Cause-Pflege entscheidet über Qualität der Vorschläge.

### A4. Bestellabgrenzungen (Purchase Order Accruals, 2VB)

**Problem.** Leistungen oder Lieferungen sind zum Periodenende erbracht, aber noch nicht als Wareneingang oder Rechnung gebucht. Nach Periodenabgrenzung muss der Aufwand trotzdem in der Periode stehen. Klassisch: manuelle Abgrenzungsbuchungen auf Basis von Listen aus dem Einkauf.

**Lösung.** Die Accrual Engine erzeugt je Bestellposition ein Abgrenzungsobjekt (Komponente POAC). Geplante Kosten, Laufzeit und Kontierung kommen aus der Bestellung. Monatlich wird der Fertigstellungsgrad (Percentage of Completion, PoC) linear über die Laufzeit ermittelt, daraus die kumuliert fälligen Kosten, abzüglich bereits gebuchter Istkosten (Wareneingänge, Rechnungen). Die Differenz wird als Abgrenzung gebucht und in der Folgeperiode storniert.

**Welche Bestellungen.** Standardmäßig nur Belegart NB mit leerer Positionstyp und Kontierung (Verbrauchsmaterial, Kostenstelle, Auftrag, PSP). Lagermaterial ohne Kontierung wird nicht abgegrenzt, weil der Wareneingang dort direkt den Bestand bewertet. Das Abgrenzungsobjekt entsteht erst, wenn die Bestellung freigegeben ist (Status „In Release“ wird nicht übernommen). Abgrenzungen sind möglich für Lean Service (Positionstyp leer, Produkttypgruppe 2), erweiterte Limitpositionen (Positionstyp E) und Verbrauchsprodukte (Produkttypgruppe 1).

**Konfiguration (SSCUI oder SAP Central Business Configuration).**
- Define Accrual Item Types and Methods for MM Purchase Order Items: Zuordnung Buchungskreis zu Transfervariante. SDEF ist die Standardvariante (nur Abgrenzungen). SDFR aktiviert zusätzlich Deferrals (Rechnungsabgrenzung, wenn Rechnungen vor der Leistung kommen).
- Define Threshold Variants: untere und obere Schwelle je Periodenbetrag. Darunter keine Prüfung (Review-Typ B), dazwischen automatische Prüfung (A), darüber manuelle Prüfung (E).
- Kontenfindung über die vorgelieferten Accrual-Item-Types (z. B. SCSTPLN für geplante Kosten). Review-Aktivierung je Item Type.

**Prozess und Apps.**

| Schritt | Rolle | App |
|---|---|---|
| Workflow für Review anlegen und aktivieren | GL Accountant | Manage Workflows for Purchase Order Accruals Review (F3625), Schritt „Review Purchase Order Accrual“, Empfänger z. B. Rolle „automatisch ermittelt“ (Einkäufer der Bestellung) |
| Bestellungen übertragen (nur einmalig für Altbestand) | GL Accountant | Schedule Accruals Jobs (F3778), Vorlage „Purchase Order Accruals – Transfer Purchase Orders to Accrual Engine“ |
| Periodische Abgrenzung vorschlagen | GL Accountant | F3778, Vorlage „… Propose Periodic Accruals“, Parameter letzter Tag der Periode, Buchungskreis |
| Review durch den Einkäufer | Purchaser | My Inbox (F0862): „Revised Planned Costs“ oder PoC anpassen, Anpassungsgrund (z. B. S1 „Vorschlag zu hoch“), bestätigen |
| Review durch Controlling (Vier-Augen-Prinzip) | Cost Accountant – Overhead | Review Purchase Order Accruals – For Cost Accountant (F3552), Filter Review-Typ E, Register „Unreviewed“, Bearbeiten, Confirm Review |
| Abgrenzung buchen | GL Accountant | F3778, Vorlage „… Post Periodic Accruals“, Option „Rev. on First Day of Next Period“ (sonst Storno am letzten Tag der Folgeperiode) |
| Auswerten | GL Accountant | Analyze Accrual Postings (F3732), Display Purchase Order Accruals (F3928, Lifecycle, Review-Historie, Buchungen), Display Accrual Object Items (F4899), Display Periodic Accrual Amounts (F4900) |
| Simulieren | GL Accountant | F3778 „… Simulate Accrual Postings“, dann Accrual Postings – With Simulation (W0183) und Accrual Postings – Simulated / Posted (W0184) |

**Buchung.** Aufwand (Kontierung aus der Bestellung, z. B. Kostenstelle) an Abgrenzungskonto (sonstige Verbindlichkeit). Ledgergruppe optional, also auch nur im lokalen Ledger möglich.

### A5. Abgrenzung auf Basis von Leistungserfassungsblättern (63L)

**Problem.** Bei Lean Services (22Z) erfasst der Dienstleister oder der Fachbereich ein Leistungserfassungsblatt (SES). Die Kostenbuchung (Wareneingang) entsteht erst mit der Freigabe des SES. Liegt am Periodenende ein eingereichtes, aber nicht freigegebenes SES vor, fehlt der Aufwand in der Periode.

**Lösung.** Die Accrual Engine (Komponente SSAC) repliziert Lean-Service-Bestellungen als Abgrenzungsobjekte und schlägt als Abgrenzungsbetrag den Wert der eingereichten, nicht freigegebenen SES vor. Nach Review wird die Abgrenzung gebucht und in der Folgeperiode storniert. Mit der Freigabe des SES kommt der echte Wareneingang.

**Abgrenzung zu 2VB.** 2VB arbeitet mit geplanten Kosten und zeitlichem PoC, 63L mit tatsächlich erfassten Leistungen. Wenn eine Bestellung für beide Komponenten in Frage kommt, entscheidet die Transferpriorität (SSCUI „Adjust Transfer Priorities for Accruals“: SSAC auf Priorität 1). Außerdem muss der Buchungskreis der Transfervariante SSES zugeordnet sein („Define Accrual Item Types and Methods for Purchase Orders of Service“). Voraussetzung ist 22Z oder 22K (Fieldglass).

**Prozess und Apps.**

| Schritt | Rolle | App |
|---|---|---|
| Bestellungen übertragen (nur wenn Online-Integration deaktiviert) | GL Accountant | F3778, Vorlage „Service Entry Sheet Accruals – Transfer Purchase Orders to Accrual Engine“ |
| Abgrenzung vorschlagen (optional, nur für Review nötig) | GL Accountant | F3778, Vorlage „… Propose Periodic Accruals“ |
| Review (nur Anzeige) | Cost Accountant – Overhead | Review Service Entry Sheet Accruals – For Cost Accountant (F6108) |
| Buchen | GL Accountant | F3778, Vorlage „… Post Periodic Accruals“, Stornooption wie bei 2VB |
| Anzeigen | GL Accountant | Display Service Entry Sheet Accruals (F6107) |
| Simulieren und vergleichen | GL Accountant | F3778 „… Simulate Accrual Postings“, W0183, W0184 mit Komponente SSAC |

### A6. Zusammenhang der fünf Themen (für die Einstiegsfolie)

| Situation zum Periodenende | Was fehlt | Welches Instrument |
|---|---|---|
| WE gebucht, Rechnung fehlt | Verbindlichkeit gegenüber Lieferant | Nichts zu tun, GR/IR-Konto zeigt „geliefert, nicht berechnet“; Umgliederung zum Stichtag |
| Rechnung gebucht, WE fehlt | Leistung/Bestand | GR/IR-Konto zeigt „berechnet, nicht geliefert“; Monitor klärt, ob Lieferung oder Gutschrift kommt |
| WE und RE weichen dauerhaft ab | Entscheidung | GR/IR-Monitor (2V7), ML-Vorschlag (2ZS), Abschreibung |
| Weder WE noch RE, Leistung läuft aber | Aufwand | PO-Accruals (2VB) auf Basis Plan und PoC |
| SES erfasst, aber nicht freigegeben | Aufwand | SES-Accruals (63L) auf Basis erfasster Leistung |
| Rechnung weicht von Bestellung ab | Zahlfreigabe | Three-Way-Match, Zahlsperre R, Release Blocked Invoices |

---

## Teil B – Agenda (120 Minuten)

| Zeit | Block | Inhalt | Format |
|---|---|---|---|
| 0:00–0:10 | Einstieg | Ziel des Workshops, Scope Items, Begriffe (GR/IR, Three-Way-Match, Accrual Engine), Zusammenhangsfolie A6 | Präsentation |
| 0:10–0:35 | PO-Rechnung und Three-Way-Match | Prozess A1/A2, Demo 1 (Bestellung, WE, Rechnung mit Abweichung, Sperre, Freigabe, Prozessfluss) | Demo + Fragen |
| 0:35–0:50 | Fit-to-Standard Teil 1 | Toleranzen, GR-basierte Rechnungsprüfung, Sperrgründe, Freigabeverantwortung, Workflow für Lieferantenrechnungen | Diskussion |
| 0:50–1:10 | GR/IR-Monitoring mit ML | Prozess A3, Demo 2 (F3303, F3302 Fall bearbeiten, Situation, F5796, ML-Vorschlag oder Erklärung) | Demo + Fragen |
| 1:10–1:15 | Pause | | |
| 1:15–1:35 | PO-Accruals | Prozess A4, Demo 3 (Vorschlag, Review in My Inbox und F3552, Buchen, F3928) | Demo + Fragen |
| 1:35–1:45 | SES-Accruals | Prozess A5, Demo 4 (SES nicht freigegeben, F6108, Buchen, F6107) | Demo kurz |
| 1:45–2:00 | Fit-to-Standard Teil 2 und Abschluss | Schwellwerte, Review-Rollen, Stornotermin, Deferrals, ML ja/nein, offene Punkte, nächste Schritte | Diskussion, Entscheidungsliste |

---

## Teil C – Demo-Ablauf

### C0. Vorbereitung am Vortag (Pflicht)

Stammdaten aus den Skripten (Buchungskreis 1010, Kontenplan YCOA, KoRe A000): Lieferant 10300001, Material TG0011, Werk 1010, Einkaufsorganisation 1010, Einkäufergruppe 001, Sachkonto 51600000, Kostenstelle 10101101 (2VB) bzw. 10101001 (2V7). Vor dem Workshop im Demosystem prüfen, ob diese Werte existieren.

Checkliste:
1. Benutzer mit Rollen: Purchaser, Purchasing Manager, AP Accountant, GL Accountant, Cost Accountant – Overhead, Analytics Specialist, Business Process Specialist. Am besten ein personalisierter Demo-User mit allen Rollen plus ein zweiter für den Einkäufer (My Inbox).
2. Buchungsperioden FI und MM offen (J58, BNZ).
3. Flexibler Workflow für Bestellfreigabe aktiv (automatische Freigabe läuft nach wenigen Sekunden).
4. 2VB: Workflow in F3625 angelegt und aktiviert. Buchungskreis 1010 auf Transfervariante (SDEF oder SDFR) geprüft. Schwellwerte so setzen, dass die Demo-Bestellung in Review-Typ E fällt (obere Schwelle unter dem Monatsbetrag der Demo-Bestellung).
5. 63L: Transferpriorität SSAC = 1 und Buchungskreis 1010 auf SSES zugeordnet. Eine Lean-Service-Bestellung (22Z) mit eingereichtem, nicht freigegebenem SES anlegen.
6. 2V7: Mindestens 5 bis 10 Bestellungen mit GR/IR-Differenz vorhanden (Teillieferungen, Rechnung ohne WE). Ein bis zwei Fälle bereits mit Status bearbeitet, damit F5796 etwas zeigt. Team ZGRIR_TEAM (Typ FIGRIR) und die beiden Situationstypen anlegen, falls 31N aktiv.
7. 2ZS: Prüfen, ob im Demosystem ein aktives Deployment für FI_GRIR_RECONCILE existiert und der Job „Prepare GR/IR Status Predictions“ gelaufen ist. Wenn nicht: In der Demo nur F4470 zeigen und die Vorschläge erklären (Trainingsdaten fehlen).
8. Vorlauf-Belege: Demo 1 und 3 brauchen je eine Bestellung. Eine davon am Vortag anlegen, Wareneingang buchen, damit in Demo 1 nur noch die Rechnung live erfasst wird. Zweite Bestellung ohne WE für Demo 3.
9. Jobs F3778 „Propose Periodic Accruals“ am Vortag laufen lassen, damit der Review-Fall in My Inbox und F3552 steht. Live im Workshop nur „Post Periodic Accruals“ starten.
10. Fallback: Screenshots jeder Demo-App, falls Jobs im Workshop hängen.

### C1. Demo 1 – PO-Rechnung mit Three-Way-Match (ca. 15 Minuten)

Story: Bestellung 10 Stück TG0011 à 100 EUR auf Kostenstelle. Lieferant liefert 8 Stück, stellt aber 10 Stück à 110 EUR in Rechnung.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | Purchaser | Create Purchase Order – Advanced (ME21N) oder Manage Purchase Orders | Bestellung vom Vortag aufrufen: Lieferant 10300001, Kontierung K, Material TG0011, 10 PC, 100 EUR, Sachkonto 51600000, Kostenstelle 10101101 | Kennzeichen „Wareneingang“ und „GR-based IV“, Status freigegeben |
| 2 | Warehouse Clerk oder Purchaser | Post Goods Receipt for Purchasing Document | Wareneingang 8 PC (am Vortag gebucht, nur zeigen) | Bestellentwicklung: WE-Menge 8, Wert 800 |
| 3 | GL Accountant | Display Journal Entries / Manage Journal Entries | WE-Beleg: Aufwand 800 an GR/IR 800 | Verrechnungskonto und Zuordnung Bestellnummer/Position |
| 4 | AP Accountant | Create Supplier Invoice (F0859) | Rechnung live: Referenz Bestellung, Bruttobetrag 1.309 EUR (10 × 110 + 19 %), Menge 10, Preis 110 | System schlägt 8 PC à 100 vor, Erfasser überschreibt; Saldo null, Warnmeldung Preis- und Mengenabweichung |
| 5 | AP Accountant | F0859, Buchen | Rechnung buchen | Belegnummern; Hinweis Zahlsperre R |
| 6 | AP Accountant | Supplier Invoices List oder Manage Supplier Line Items (F0712) | Offener Posten mit Zahlsperre | Sperrgründe Preis und Menge |
| 7 | AP Accountant | Release Blocked Invoices | Positionen zeigen, nicht freigeben (bleibt für Demo 2 offen) | Wer darf freigeben, automatische Freigabe nach WE-Nachbuchung |
| 8 | AP Accountant | Display Process Flow – Accounts Payable (F2691) | Belegart Einkaufsbeleg, Bestellnummer | Kette Bestellung → Warenbewegung → Rechnung → Journal Entry, fehlender Ausgleich |

Fragen an die Teilnehmer nach Demo 1: Wie oft kommen Mengen- oder Preisabweichungen heute vor? Wer klärt sie? Welche Toleranzen gelten heute?

### C2. Demo 2 – GR/IR-Monitoring mit ML (ca. 15 Minuten)

Story: Die Bestellung aus Demo 1 hat jetzt WE 8 und RE 10. Der GL Accountant findet den Fall im Monitor.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | GL Accountant | Monitor GR/IR Account Reconciliation – Overview (F3303) | Buchungskreis 1010 | KPIs: Bestellpositionen mit RE-Überschuss, Drilldown nach Lieferant |
| 2 | GL Accountant | Reconcile GR/IR Accounts (F3302) | Buchungskreis 1010, Demo-Bestellung auswählen, Details | Register Übersicht (8 vs 10), FI-Posten, Bestellentwicklung, Kontakte (Einkäufer) |
| 3 | GL Accountant | F3302 | Falls ML aktiv: vorgeschlagenen Status, Priorität, Ursache zeigen | ML-Vorschlag und Herkunft (Historie) |
| 4 | GL Accountant | F3302, Process Item | Status „Request Completion of Delivery“, Priorität hoch, Abteilung, Bearbeiter (Einkäufer), Ursache „Incomplete goods receipt“, Notiz, Sichern | Fall ist zugewiesen |
| 5 | Purchaser | Launchpad-Benachrichtigungen | Benachrichtigung „als Bearbeiter zugewiesen“ öffnen (nur wenn Situation Handling aktiv) | Situation FIN_GRIRPROCESSORCHANGED |
| 6 | GL Accountant | GR/IR Process Insights (F5796) | Buchungskreis 1010, Insights nach Status, Ursache, Abteilung | Durchlaufzeiten, Verteilung |
| 7 | Analytics Specialist | Intelligent Scenario Management (F4470) | Szenario FI_GRIR_RECONCILE, Modell, Trainings, Deployments | Trainingsfilter, Zielfelder, Status aktiv; nur zeigen, nicht neu trainieren |
| 8 | GL Accountant | Schedule General Ledger Jobs (F1927) | Vorlage „Prepare GR/IR Status Predictions (DAR ML model)“ zeigen | Wie die Vorschläge in F3302 kommen |

Kernaussage: Der Monitor ersetzt die Excel-Liste aus der GR/IR-Analyse. Jeder Fall bekommt Status, Verantwortlichen und Ursache; die Ursachen trainieren später das Modell.

### C3. Demo 3 – PO-Accruals (ca. 15 Minuten)

Story: Beratungsbestellung (Verbrauch, Kostenstelle) über 12.000 EUR mit Laufzeit über drei Monate, noch kein WE und keine Rechnung. Monatsende: 4.000 EUR sind abzugrenzen.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | Purchaser | Manage Purchase Orders | Bestellung vom Vortag zeigen: NB, Kontierung K, Lieferdatum, Status freigegeben | Was ein Abgrenzungsobjekt auslöst |
| 2 | GL Accountant | Display Purchase Order Accruals (F3928) | Buchungskreis 1010, Lifecycle P | Abgrenzungsobjekt mit Laufzeit, geplanten Kosten, Kontierung, Item Type |
| 3 | GL Accountant | Schedule Accruals Jobs (F3778) | Job „Propose Periodic Accruals“ vom Vortag zeigen (Log) | Parameter letzter Tag der Periode |
| 4 | Purchaser | My Inbox (F0862) | Review-Aufgabe öffnen, PoC z. B. auf 30 % korrigieren, Grund S1, bestätigen | Einkäufer kennt den Leistungsstand |
| 5 | Cost Accountant – Overhead | Review Purchase Order Accruals – For Cost Accountant (F3552) | Periode, 1010, Review-Typ E, Register Unreviewed, Bearbeiten, Confirm Review | Vier-Augen-Prinzip, Review-Typen A/B/E |
| 6 | GL Accountant | F3778 | Job „Post Periodic Accruals“ live starten, Option Storno am ersten Tag der Folgeperiode | Buchung und Storno |
| 7 | GL Accountant | Analyze Accrual Postings (F3732) | 1010, Periode, Offsetting Line Items | Aufwand auf Kostenstelle an Abgrenzungskonto |
| 8 | GL Accountant | F3928, Details | Review-Historie und Buchungen zur Position | Nachvollziehbarkeit |
| 9 | GL Accountant | Accrual Postings – Simulated / Posted (W0184) | Komponente POAC, Abgrenzungsobjekt | Simulation gegen Ist (optional) |

### C4. Demo 4 – SES-Accruals (ca. 8 Minuten)

Story: Lean-Service-Bestellung Reinigung, SES über 2.500 EUR für den laufenden Monat eingereicht, Freigabe durch den Fachbereich steht aus.

| # | Rolle | App | Aktion | Zeigen |
|---|---|---|---|---|
| 1 | Purchaser | Manage Service Entry Sheets – Lean Services | SES im Status „eingereicht“ zeigen | Kein WE, kein Aufwand gebucht |
| 2 | Cost Accountant – Overhead | Review Service Entry Sheet Accruals – For Cost Accountant (F6108) | Letzter Tag der Periode, 1010, Bestellung | Vorgeschlagener Betrag = SES-Wert |
| 3 | GL Accountant | Schedule Accruals Jobs (F3778) | „Service Entry Sheet Accruals – Post Periodic Accruals“ starten | Buchung |
| 4 | GL Accountant | Display Service Entry Sheet Accruals (F6107) | 1010, Bestellung, Details | Abgrenzungsobjekt SSAC |
| 5 | Erklärung | – | Nächste Periode: SES wird freigegeben, WE bucht Aufwand, Abgrenzung wird storniert | Kein doppelter Aufwand |

---

## Teil D – Fit-to-Standard-Fragen und Entscheidungsbedarf (KDD-Kandidaten)

**Rechnungserfassung und Three-Way-Match**
1. Welche Bestellarten laufen mit Wareneingang (Three-Way), welche ohne (Two-Way)? Dienstleistungen immer über SES?
2. WE-bezogene Rechnungsprüfung als Standard im Lieferantenstamm?
3. Toleranzgrenzen je Buchungskreis (Preis, Menge, Termin, kleine Differenzen) in Prozent und absolut.
4. Wer gibt gesperrte Rechnungen frei (Einkauf, Buchhaltung, Fachbereich), manuelle oder automatische Freigabe nach WE-Nachbuchung?
5. Flexibler Workflow für Lieferantenrechnungen: ja/nein, ab welchem Betrag, Vorerfassung durch wen?
6. Doppelerfassungsprüfung, Referenzpflicht, Rechnungseingangsdatum für DPO-Kennzahlen.

**GR/IR-Monitoring**
7. Wer ist Prozessverantwortlicher für GR/IR-Differenzen (Buchhaltung oder Einkauf)? Teams und Verantwortlichkeiten je Buchungskreis oder Einkaufsorganisation.
8. Welche Statuswerte und Ursachen sollen genutzt werden (Einheitlichkeit für das ML-Training)?
9. Situation Handling: Schwellwert für Benachrichtigung, Batch-Zeitpunkt, 31N im Scope?
10. ML: gewünscht ab Go-live oder erst nach Aufbau der Historie? Ticket für SAP_COM_1042 einplanen.
11. Periodische Jobs: automatischer GR/IR-Ausgleich, Umgliederung zum Stichtag, Abschreibung von Restmengen (Berechtigung, Betragsgrenze).

**PO-Accruals**
12. Welche Bestellungen sollen abgegrenzt werden (nur NB mit Kontierung, Lean Services, Limitpositionen)?
13. Deferrals aktivieren (SDFR) oder nur Accruals (SDEF)?
14. Schwellwerte für Review-Typen A/B/E, Review durch Einkäufer, Controlling oder beide?
15. Stornotermin: erster Tag oder letzter Tag der Folgeperiode?
16. Ledgergruppe: alle Ledger oder nur lokal/IFRS?
17. Abgrenzungskonten im YCOA (sonstige Verbindlichkeiten, Aufwandskonto aus der Bestellung) und Belegart.
18. Zeitplan im Monatsabschluss: Propose am Vortag, Review-Deadline, Post am Arbeitstag X.

**SES-Accruals**
19. Werden Lean Services (22Z) oder Fieldglass (22K) genutzt? Ohne diese kein 63L.
20. Fristen für SES-Freigabe im Fachbereich, damit die Abgrenzung die Ausnahme bleibt.
21. Transferpriorität SSAC vor POAC bestätigen.

---

## Teil E – Fallstricke aus den Skripten

- 2VB/63L: Abgrenzungsobjekt entsteht erst nach Bestellfreigabe. In der Demo auf den Status achten.
- 2VB: Nur Review-Typ E erscheint in My Inbox. Schwellwerte vorher passend setzen.
- 2VB: Werte in F4899 (kumuliert, Periode, Rest) stimmen erst nach dem Simulationsjob.
- 2VB/63L: Nach dem Buchen zeigt W0183 nur noch die Istwerte, keine Simulation mehr.
- 2ZS: Mindestens 100 bearbeitete Fälle, Kommunikationsszenario per Ticket. Im Kundensystem ist ML ein Thema für Monate nach Go-live.
- 2V7: Situation Handling braucht 31N, Team vom Typ FIGRIR und kopierte Situationstypen.
- J60: Belegnummer aus F0859 ist die Logistiknummer, nicht der Journal Entry. Teilnehmer stolpern regelmäßig darüber.
- J60: Periodenprüfung für Materialstamm lässt sich abschalten, gilt aber nicht für Rechnungen mit Bestellbezug.
- App-IDs für Release Blocked Invoices, Wareneingangsbuchung und Manage Service Entry Sheets wurden hier bewusst ohne F-Nummer genannt und sollten im Demosystem per App Finder geprüft werden.
