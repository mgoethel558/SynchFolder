# F2S-Workshop 4: Collections & Dispute Management (3 h)

**Thema:** Automated collection workflow, worklist management, dispute case creation and resolution, collections strategy configuration
**Basis:** Scope-Items im Ordner `LOH/4_F2SWS` (Release S4CLD 2608)

| Scope-Item | Titel | Rolle im Workshop |
|---|---|---|
| J59 | Accounts Receivable | Grundlage: Kundenposten, Mahnwesen, Korrespondenz, AR-Reporting |
| BFC | Collections and Dispute Management | Kernthema: Strategien, Worklist, Dispute Cases (klassische UDM-/Case-Management-Apps) |
| 7MA | Collections and Dispute Automation | Alternative der neuen Generation (BRF+-Automatisierung, Teams, Receivable Items) |
| 2PD | Provisioning of Overdue Receivables | Abschluss: Wertberichtigung (IFRS 9 ECL) und Ausbuchung uneinbringlicher Forderungen |

**Wichtigste Vorentscheidung:** BFC und 7MA schließen sich faktisch aus. SAP weist in 7MA ausdrücklich darauf hin, vor der Wahl von 7MA den Help-Portal-Abschnitt "Integration with Other Components" zu lesen. J59 vermerkt, dass beide Scope-Items eine zusätzliche Lizenz erfordern. Im Workshop muss geklärt werden, welche Variante der Kunde lizenziert hat bzw. anstrebt. Der Demo-Ablauf unten ist auf **BFC** ausgelegt (vollständigere Reporting-Apps, Standard-Demodaten); 7MA wird als Ausblick gezeigt.

---

## Teil 1: Prozesserklärung

### 1.1 End-to-End-Bild (so erzähle ich es im Workshop)

```
Rechnung in FI-AR gebucht
        │
        ▼ Fälligkeit überschritten
  ┌─────┴──────────────────────────────────────────┐
  │                                                │
  ▼                                                ▼
MAHNWESEN (J59)                         COLLECTIONS MANAGEMENT (BFC)
Mahnverfahren 1001/1002                 Täglicher Job: FI-AR-Daten → Collections
Mahnlauf F150 / My Dunning              Täglicher Job: Worklist aus Strategie
Proposals F2435                         Spezialist arbeitet Worklist ab (F0380)
Mahnhistorie F2328                      Kundenkontakt in Process Receivables (F0106A)
  │                                        │
  │   Mahnsperre, wenn Dispute offen       ├─ Promise to Pay (automatisch kept/broken)
  │   oder Zahlungsversprechen offen       ├─ Resubmission (Wiedervorlage, Kunde raus aus Worklist)
  │                                        ├─ Dispute Case anlegen
  │                                        ├─ Korrespondenz / E-Mail
  │                                        └─ Kundenkontakt dokumentieren (Contact History)
  │                                                │
  ▼                                                ▼
DISPUTE MANAGEMENT (BFC)  ◄──── Anlage auch aus Unterzahlung (F1520) oder Job (F3578)
Koordinator weist zu (F0702A) → Bearbeiter prüft → Entscheidung:
   berechtigt     → Gutschrift, Ausgleich → Case schließt automatisch
   nicht berechtigt → Status "Not justified" → zurück ins Collections
   Fehlanlage     → Void
   eskaliert      → Job "Automatic Write-Off of Dispute Cases"
        │
        ▼ Forderung bleibt uneinbringlich
WERTBERICHTIGUNG / AUSBUCHUNG (2PD)
Bewertungslauf F107 (Provision Matrix) → Analyse F3246 → Ausbuchung F0773
```

### 1.2 Organisation und Stammdaten in BFC

Das Collections Management hat eine eigene Organisationsstruktur, die neben Buchungskreis und Mahnwesen existiert:

| Objekt | Bedeutung | Pflege |
|---|---|---|
| **Collection Segment** | Organisatorische Einheit, z. B. je Buchungskreis, Land oder Kundengruppe. Enthält die Buchungskreise. | Konfiguration (SSCUI), Demo-Wert `YT_SEGMT01` |
| **Collection Profile** | Bündel von Segmenten; wird dem Geschäftspartner zugeordnet. Daraus wird die Priorität in der Worklist abgeleitet. | Konfiguration, Demo-Wert `YT_PRF:01` |
| **Collection Group** | Team von Spezialisten. Jede Gruppe hat genau **eine Strategie**. Vertretungsregelung (Urlaub, Krankheit) auf Spezialistenebene. | App Manage Collection Groups (UDM_GROUP) |
| **Collection Specialist** | Benutzer, der die Worklist bearbeitet. Muss der Gruppe als Processor zugeordnet sein. | UDM_GROUP, Dialogstruktur "Assign Processor to Collection Group" |
| **Zuordnung Gruppe ↔ Segment** | Welche Gruppen dürfen Kunden eines Segments bearbeiten; eine Gruppe ist Default-Gruppe. | App Assign Collection Groups to Segments (UDM_GROUP2SGMT) |
| **Collection Strategy** | Regelwerk zur Priorisierung (siehe 1.3) | App Manage Collection Strategies (F2946) |

**Geschäftspartner:** Der Kunde braucht die Rolle "Collections Management" (UDM0000). Pflege einzeln über **Manage Collections Master Data (F5400)** (Profil wählen, Segment wird automatisch ergänzt, Gruppe und Spezialist je Segment eintragen) oder massenhaft über **Schedule Collections Management Jobs – Mass Changes (F3918)** mit Job-Template "Assignment of Collection Profiles to Business Partners". Praxisbeispiel aus dem BPD: Nur Kunden kritischer Risikoklassen aus dem Credit Management ins Collections aufnehmen.

**Für das Mahnwesen zusätzlich:** Sachbearbeiter (Accounting Clerk) über Define Accounting Clerks (S_ALR_87003335) anlegen und im Kundenstamm (Buchungskreisdaten, Reiter Korrespondenz und Mahndaten) Mahnverfahren `1001`, Mahnsperre leer, Mahnsachbearbeiter `01` eintragen. Ohne Sachbearbeiterzuordnung funktioniert My Dunning Proposals nicht.

### 1.3 Collection Strategy: Konfiguration und Wirkungsweise

Die Strategie beantwortet die Frage: **Welcher Kunde steht morgen ganz oben auf der Worklist meines Spezialisten?**

Eine Strategie steuert laut BPD:
- Priorisierung der Geschäftspartner auf der Worklist
- Währung der Beträge in der Worklist
- Zeitintervalle (Aging Periods), nach denen Forderungen sortiert werden
- Art der Integration mit dem Mahnwesen
- Einfluss der Zahlungsbedingungen (proaktive Bearbeitung vor Fälligkeit)

**Aufbau in Manage Collection Strategies (F2946):**
1. Kopf: Strategie-ID (z. B. `YT_ST1010`), Name, Währung EUR, Maximale Bewertung (wird nach Regelpflege gesetzt). Neue Strategie ist zunächst **Inactive**.
2. Collection Rules hinzufügen: vorgefertigte Regeln (`CR000000nn`) mit Bedingungen und einer **Bewertung in Punkten**.
3. Aging Periods: Überfälligkeitsperioden (1–30, 31–60, 61–90, >90 Tage) und Fälligkeitsperioden.
4. "Show Assignment": zeigt, welche Gruppen die Strategie nutzen.

**Beispielregeln aus dem BPD (gut für die Demo):**

| Regel | Bedingung | Punkte | Fachliche Aussage |
|---|---|---|---|
| CR00000002 | Summe überfällig > 1.500 und ≥ 5 Tage überfällig | 15 | Großer Gesamtrückstand |
| CR00000003 | Einzelposten > 5.000 und ≥ 5 Tage überfällig | 10 | Eine große Rechnung |
| CR00000013 | Summe Zahlungsversprechen > 500 | 10 | Offene Promises nachhalten |
| CR00000019 | Tage seit letztem Kontakt ≥ 10 | 5 | Lange nicht kontaktiert |

Die Punkte der erfüllten Regeln werden addiert; aus dem Verhältnis zur maximalen Bewertung ergibt sich die Priorität des Kunden (sehr hoch bis niedrig). Kunden ohne Punkte landen nicht auf der Worklist.

**Wichtig für die Demo:** Die Worklist wird in der Public Cloud durch **tägliche, von SAP betriebene Jobs** erzeugt (Transfer FI-AR-Daten, Worklist-Erstellung). Eine im Workshop geänderte Strategie wirkt erst nach dem nächsten Lauf. Strategie und Stammdaten deshalb **vor** dem Workshop einrichten.

### 1.4 Worklist Management

**Sicht Spezialist: Process Collections Worklist (F0380)**
- Reiter "My Open Items" und "My Completed Items", sortiert nach Priorität.
- Doppelklick auf Kunde: Dialog mit Adresse, Kontakt, Links zu Clear Incoming Payments, Display Customer Balances, Manage Customer Line Items, Post Incoming Payments, **Process Receivables**.
- "Assigned to Others": Worklists anderer Spezialisten einsehen (Vertretung).
- **Massenkorrespondenz:** mehrere Kunden markieren → Create Correspondences → Korrespondenzart, Datum, E-Mail-Template → Vorschau → Bestätigen. Kunden wandern nach "Completed", Kontaktergebnis "Correspondence Sent".

**Sicht Manager: Supervise Collections Worklist (F2375)**
- Alle Geschäftspartner mit überfälligen Forderungen, Zuordnung zu Spezialisten ("Assign to Specialist"), Drilldown auf Kundenposten, Mahn- und Zahlsperren setzen.

**Kundencockpit: Process Receivables (F0106A)**
Reiter: Invoices, Dispute Cases, Promises to Pay, Resubmissions, Collection Contacts, Contact History. Aktionen aus dem Kontakt heraus:

| Aktion | App im Hintergrund | Wirkung |
|---|---|---|
| Create Promise to Pay | Manage Promises to Pay (F4710) | Betrag und Datum; Status Open → automatisch Kept/Broken durch FI-AR-Integration; gebrochenes Versprechen kann Regel in der Strategie auslösen; Posten wird nicht gemahnt, solange Versprechen nicht gebrochen |
| Create Resubmission | Manage Resubmissions (F4709) | Wiedervorlagedatum + Grund (z. B. "Contact Person Requests Callback"); Kunde verschwindet bis dahin von der Worklist |
| Create Dispute Case | Manage Dispute Cases (F0702A) | Siehe 1.5; Posten wird aus dem Mahnlauf ausgeschlossen |
| Collection Contacts → Create | Manage Collection Contact Persons (F4708) | Ansprechpartner mit Telefon/E-Mail |
| Finish Customer Contact | Manage Customer Contacts (F4707) | Kontaktergebnis dokumentieren; Notiz wird mit allen im Kontakt angelegten Promises/Resubmissions/Disputes vorbefüllt; optional E-Mail mit Template "Customer Contact Recap" |

**Mahnwesen aus dem Collections heraus:** My Dunning Proposals (F2435) erzeugt Mahnvorschläge für die Kunden des Sachbearbeiters, Vorschau als PDF, Versand per E-Mail oder Drucker, Mahnsperre mit Grund (Disputed, Promise to Pay, To be clarified with Sales, Legal, Other). Mahnverfahren im Standard: `1001` alle 14 Tage mit 4 Stufen, `1002` 30 Tage nach Rechnung.

### 1.5 Dispute Case: Anlage und Lösung

**Drei Anlagewege:**
1. **Manuell aus Process Receivables (F0106A):** Rechnung markieren → Create Dispute Case → Titel, Grund (z. B. Price Differences), Priorität, Bearbeiter, Ansprechpartner, Notiz, Anhang.
2. **Aus Unterzahlung beim Kontoauszug:** Reprocess Bank Statement Items (F1520) → Zahlung kleiner als Rechnung → Rechnung ausgleichen, Restposten → Create Dispute direkt im Clearing-Dialog → Buchen. Achtung: Die App ist dem Cash Management Specialist standardmäßig nicht zugeordnet, der Dispute-Katalog muss der Rolle hinzugefügt werden (Maintain Business Roles F1492).
3. **Automatisch per Job:** Schedule Dispute Management Jobs (F3578), Template "Automatic Creation of Dispute Cases": erzeugt Cases für Restposten aus automatischer Zahlungsverarbeitung (Kontoauszug, Lockbox, Nachbearbeitung). Testlauf möglich.

**Bearbeitung in Manage Dispute Cases – As Coordinator (F0702A):**
- **Zuweisen:** Koordinator filtert unzugewiesene Cases (Processor leer), trägt Bearbeiter ein, Notiz.
- **Bearbeiten:** Bearbeiter filtert nach eigener User-ID, setzt Status "In Process", Notizen, E-Mail an Kunden direkt aus dem Case, Rückgabe an Koordinator.
- **Entscheidung A (berechtigt):** Gutschrift an Kunden. Sobald die Rechnung mit der Gutschrift ausgeglichen ist, **schließt der Case automatisch**.
- **Entscheidung B (nicht berechtigt):** Status "Not justified" → Case wird reklassifiziert und ans Collections Management weitergegeben; Forderung wird wieder eingetrieben.
- **Korrektur:** "Void Dispute Case", wenn die Anlage ein Fehler war.
- **Abschreibung:** Job "Automatic Write-Off of Dispute Cases" (F3578) für zuvor eskalierte Cases (Case Type, Escalation Reason, Case-ID-Bereich).

**Reporting Disputes (Rolle AR Manager):**
Dispute Management Reporting – Open Today (F4370, Reiter Open / Processing Days / New and Solved / Solved), Open Disputes – Today (F1752), Overdue Receivables – In Dispute (F2540), Solved Disputes – Last 12 Months (F2521), New Versus Solved Disputes (F2523), Processing Days of Open Disputes (F2522). Dimensionen: Priorität, Grund, Root Cause, Buchungskreis, Bearbeiter, Koordinator, Kunde.

**Reporting Collections:**
Collections Management Reporting – Collection Progress (F4495, Reiter Collection Progress / Promise to Pay), Collection Progress – Current Run (F1738), Promise To Pay – Today (F1753, inkl. gebrochene Versprechen der letzten 12 Monate), Display Dunning History (F2328), Cash Collection Tracker (F3182, nach Kunde, Gruppe, Spezialist, Profil, Segment, Strategie).

### 1.6 Ausblick 7MA: Collections and Dispute Automation

7MA ist die Neuentwicklung mit eigenen Apps und Datenmodell. Zentrale Unterschiede zu BFC:

| Thema | BFC | 7MA |
|---|---|---|
| Datenbasis | FI-AR-Posten werden ins Collections übertragen | Eigene "Receivable/Payable Items" (RPI), Replikation muss je Buchungskreis aktiviert und initial geladen werden (F8418, F8377) |
| Org-Struktur | Segment, Profil, Gruppe, Strategie | Debt Collections Company Code (Mapping auf FI-Buchungskreis), Collection Segment + **Segment Group** (SSCUI), **Teams** (Manage Teams and Responsibilities F2412, Typ S_DCO_COLLECTOR_GROUP) |
| Priorisierung | Collection Strategy (F2946) | **Account Prioritization Rule** (F8833): Collections Rules mit Bewertung + Basic Rules (S_BR_00001 Gesamtbetrag, S_BR_00003 Einzelbetrag, S_BR_00009 Dispute, S_BR_00006 offene Task) |
| Automatisierung | Jobs für Dispute-Anlage/Write-Off, Massenänderungen | **BRF+-Entscheidungstabellen** (WDA0483): automatische Dispute-Anlage mit Grund aus Zahlungsdifferenzgrund, Zuordnung Collector Group / AR Accountant Group / Prioritization Rule, Mahn-/Zahlsperren, Eskalation |
| Kundenstamm | F5400 | Manage Master Data in C&D Automation (F8606): Segment Group, Kategorie, Account Classification (A-Kunde), je Segment Prioritization Rule + Collector Group |
| Worklist | F0380 / F0106A | Process Worklist (F8832) → "Start Activity" → Process Accounts (F8607) |
| Objekte im Kontakt | Promise to Pay, Resubmission, Dispute, Customer Contact | Promise to Pay, **Task** (ersetzt Resubmission, kann Kunde bis Fälligkeit aus Worklist nehmen), Dispute, **Activity** (ersetzt Customer Contact; Manage Activities F8610) |
| Dispute | Case mit Status, Koordinator/Bearbeiter | Manage Disputes (F7876) mit **Prozessschritten** Classify → Evaluate → Decide (Entscheidung je Receivable Item: Justified / Amount to Be Corrected) → Finalize; Anlage auch aus Manage Receivable Items (F7877) |
| Jobs | SAP-betrieben | Kunde plant selbst: Create Worklist (F8376), Escalate Disputes (F8713), P2P-Judge, Payment Behavior |
| Migration | – | Migrationsjobs für Stammdaten, Activities, Disputes, P2P, Tasks aus BFC vorhanden |

Einordnung für den Workshop: 7MA bietet mehr Automatisierung (BRF+), verlangt aber Regelpflege-Know-how und mehr Setup (RPI, Mapping, Aktivierung je Buchungskreis). BFC ist eingeschwungen und bringt die vollständigen Reporting-Apps mit. Falls der Kunde 7MA nicht explizit anstrebt, BFC als Standardempfehlung setzen und 7MA als Entscheidungspunkt dokumentieren.

### 1.7 2PD: Wertberichtigung und Ausbuchung

- **Fachlicher Rahmen:** IFRS 9 Expected Credit Loss über Provision Matrix: feste Wertberichtigungssätze je Überfälligkeitsintervall.
- **Stammdaten:** Wertberichtigungsschlüssel (z. B. `R1`) im Kundenstamm, Buchungskreisdaten, Reiter Finance, Feld "Value Adjustment". Eigene Schlüssel über SSCUI "Define Value Adjustment Key".
- **Bewertungslauf:** Perform Further Valuations (F107), Bewertungsmethode 3, Währungstyp 10, Buchung am Stichtag + automatische Stornobuchung am Folgetag, Belegart SA. Ablauf: Parameter → Dispatch → Display → Sample Posting → Forward (Transfer) → Log.
- **Analyse:** Doubtful Accounts Valuation (F3246) mit Intervallen 30/60/90 Tagen, Sichten nach Kunde, Land, Risikoklasse, Mahnsperre, Drilldown in Kundenposten.
- **Ausbuchung:** Clear Incoming Payments – Manual Clearing (F0773), "Transfer Posting" ein, Belegart DA, Reiter "Post to G/L Account": Aufwandskonto (z. B. 62000000), Steuerkennzeichen, Kostenstelle; Buchungsschlüssel 17.
- **Einschränkung:** Funktioniert nicht, wenn Advanced Foreign Currency Valuation aktiv ist (dann greift die klassische Umgliederung nicht). Voraussetzung: Fremdwährungsbewertung aus J58 mit gleichem Buchungs-/Stornodatum.

---

## Teil 2: Agenda (3 Stunden)

| Zeit | Block | Inhalt | Ziel |
|---|---|---|---|
| 0:00–0:10 | Einstieg | Ziele, Scope-Items, Rollen (AR Accountant, AR Manager, Cash Specialist), Entscheidung BFC vs. 7MA ansprechen | Erwartungen abgleichen |
| 0:10–0:35 | Prozessüberblick | End-to-End-Bild aus 1.1, Begriffe Segment/Profil/Gruppe/Strategie, Zusammenspiel Mahnwesen ↔ Collections ↔ Dispute | Gemeinsames Vokabular |
| 0:35–1:20 | Demo Block 1 | Stammdaten, Strategie, Worklist, Kundenkontakt mit Promise/Resubmission/Korrespondenz | Collections-Workflow verstanden |
| 1:20–1:30 | Pause | | |
| 1:30–2:10 | Demo Block 2 | Dispute-Lebenszyklus: Anlage (3 Wege), Zuweisung, Bearbeitung, Lösung berechtigt/nicht berechtigt, Mahnintegration | Dispute-Prozess verstanden |
| 2:10–2:35 | Reporting + Ausblick | Manager-Apps, Mahnwesen-Apps, 7MA-Kurzvorstellung, 2PD in 5 Minuten | Steuerungssicht und Alternativen |
| 2:35–2:55 | Fit/Gap | Fragenkatalog Teil 4 durchgehen, Entscheidungen und offene Punkte festhalten | KDD-Kandidaten |
| 2:55–3:00 | Abschluss | Nächste Schritte, Verantwortliche, Termine | |

---

## Teil 3: Demo-Ablauf (BFC)

### 3.1 Vorbereitung vor dem Workshop (Checkliste)

- [ ] Demodaten prüfen: Buchungskreis `1010`, Kunde `S10100251` (alternativ `10100001`, `10100002`) hat mindestens drei offene, überfällige Rechnungen; eine davon > 5.000 EUR, Summe > 1.500 EUR, mindestens 5 Tage überfällig (damit die Beispielregeln ziehen). Falls nötig über Sales-Prozess (BD9/J14) oder Enter Invoice Without Sales Order (J59) nachbuchen und Buchungsdatum zurückdatieren.
- [ ] Accounting Clerk `01` angelegt und mit Demo-User verknüpft (S_ALR_87003335).
- [ ] Kundenstamm: Mahnverfahren `1001`, Mahnsachbearbeiter `01`, keine Mahnsperre; Wertberichtigungsschlüssel `R1` (für 2PD).
- [ ] Collection-Strategie `YT_ST1010` mit den vier Regeln aus 1.3 angelegt und **aktiviert**; Gruppe `YT_GR1010` mit Strategie und Demo-User als Processor; Gruppe dem Segment `YT_SEGMT01` zugeordnet.
- [ ] Kunde in F5400 mit Profil `YT_PRF:01`, Gruppe `YT_GR1010`, Spezialist = Demo-User.
- [ ] Worklist ist nach dem nächtlichen Lauf gefüllt: am Vortag in F0380 prüfen, dass der Kunde erscheint. Sonst in der Demo F2375 (Supervise) als Fallback nutzen.
- [ ] Zweiter User (oder zweiter Browser) für die Rolle Koordinator vs. Bearbeiter; sonst mit demselben User und klarer Ansage arbeiten.
- [ ] Optional: Kontoauszugsposition mit Unterzahlung vorbereitet (J78/BFB) und Dispute-Katalog der Cash-Specialist-Rolle zugeordnet. Wenn zu aufwendig: Weg 2 nur erklären, nicht klicken.
- [ ] Mahnhistorie des Demokunden älter als 14 Tage, sonst entsteht kein Mahnvorschlag.
- [ ] E-Mail-Versand: Output-Konfiguration prüfen oder E-Mail nur bis zur Vorschau zeigen.
- [ ] Ein Dispute Case schon im Status "In Process" vorhanden, damit die Reporting-Apps nicht leer sind.

### 3.2 Storyline

"Die Firma LOH hat ihren Kunden S10100251 seit Wochen nicht erreicht. Drei Rechnungen sind überfällig, eine davon ist groß. Wir zeigen, wie das System den Kunden morgens automatisch auf die Arbeitsliste des Spezialisten setzt, wie der Spezialist den Kontakt abarbeitet, wie aus dem Gespräch ein Zahlungsversprechen und eine Reklamation entstehen und wie die Reklamation bis zur Gutschrift oder zurück ins Inkasso läuft."

### 3.3 Demo Block 1: Strategie, Worklist, Kundenkontakt (ca. 45 min)

| # | Rolle | App | Klickfolge | Botschaft |
|---|---|---|---|---|
| 1 | AR Manager | Manage Collection Strategies (F2946) | Strategie `YT_ST1010` öffnen; Regeln mit Bedingungen und Punkten zeigen; Aging Periods; "Show Assignment" | "Die Strategie ist das Regelwerk, das jede Nacht entscheidet, wer oben steht. Regeln sind Standard, Gewichte sind Ihre Entscheidung." |
| 2 | AR Manager | Manage Collection Groups (UDM_GROUP) | Gruppe `YT_GR1010` → Strategie, Processor-Zuordnung, Vertreter-Feld | "Gruppe = Team mit einer Strategie. Vertretung bei Urlaub ist Standard." |
| 3 | AR Manager | Manage Collections Master Data (F5400) | Kunde `S10100251`: Profil, Segment, Gruppe, Spezialist | "Pro Kunde nur: Profil + Spezialist. Rest wird abgeleitet. Massenzuordnung per Job (F3918) zeigen oder erwähnen." |
| 4 | AR Manager | Supervise Collections Worklist (F2375) | Liste aller überfälligen Kunden, Spalte Spezialist; einem Kunden ohne Spezialist einen zuweisen | "Manager-Sicht: Wer hat was, wo fehlt jemand." |
| 5 | AR Accountant | Process Collections Worklist (F0380) | "My Open Items": Priorität, Beträge, Aging; Doppelklick auf `S10100251` → Dialog → "Process Receivables" | "Das ist der Arbeitsplatz des Spezialisten. Keine Excel-Liste mehr." |
| 6 | AR Accountant | Process Receivables (F0106A) | Reiter Invoices, Contact History; Collection Contacts → Create → Ansprechpartner mit Telefon/E-Mail | "Alles zum Kunden an einem Ort: Rechnungen, Versprechen, Reklamationen, Historie." |
| 7 | AR Accountant | Process Receivables → Create Promise to Pay (F4710) | Kleine überfällige Rechnung markieren → Betrag (Default voll), Datum heute + 7 → Save → Reiter Promises to Pay zeigen | "Das System prüft selbst, ob das Versprechen gehalten wird. Gebrochene Versprechen holen den Kunden per Regel zurück auf die Liste. Solange das Versprechen läuft, wird nicht gemahnt." |
| 8 | AR Accountant | Process Receivables → Create Resubmission (F4709) | Zweite Rechnung → Datum heute + 2, Grund "Contact Person Requests Callback" | "Wiedervorlage nimmt den Kunden bis dahin von der Worklist." |
| 9 | AR Accountant | Process Receivables → Create Dispute Case | Große Rechnung markieren → Titel "Preisdifferenz Rechnung 9xxxx", Grund Price Differences, Priorität High, Bearbeiter leer lassen (für Block 2), Notiz | "Reklamation entsteht aus dem Gespräch heraus. Die Rechnung wird ab jetzt aus dem Mahnlauf ausgeklammert." |
| 10 | AR Accountant | Process Receivables → Finish Customer Contact (F4707) | Kontaktergebnis wählen, vorbefüllte Notiz zeigen; Create Email → Template "Customer Contact Recap" → Vorschau (senden nur, wenn Output konfiguriert) | "Kontakt ist dokumentiert, Kunde bekommt die Zusammenfassung. Die Historie bleibt für Kollegen sichtbar." |
| 11 | AR Accountant | Process Collections Worklist (F0380) | Zurück: Kunde ist in "My Completed Items"; Massenkorrespondenz für zwei weitere Kunden anstoßen (bis Vorschau) | "Massenkorrespondenz für die lange Schwanzliste." |

Fit-to-Standard-Fragen, die ich in Block 1 stelle: Wer sind die Spezialisten, wie viele, wie gruppiert (Region, Kundengruppe, Buchungskreis)? Welche Kriterien entscheiden heute, wer angerufen wird? Gibt es Vertretungsregeln? Welche Korrespondenz geht heute raus und in welchen Sprachen?

### 3.4 Demo Block 2: Dispute-Lebenszyklus (ca. 40 min)

| # | Rolle | App | Klickfolge | Botschaft |
|---|---|---|---|---|
| 12 | AR Accountant (Koordinator) | Manage Dispute Cases – As Coordinator (F0702A) | Go ohne Filter → unzugewiesene Cases (Processor leer) → Case aus Schritt 9 → Edit → Processor = Bearbeiter-User, Notiz → Save | "Koordinator verteilt. Alles, was unzugewiesen ist, sieht man sofort." |
| 13 | AR Accountant (Bearbeiter) | Manage Dispute Cases (F0702A) | Filter Processor = eigener User → Case öffnen → Status "In Process", Notiz, Anhang (z. B. Lieferschein) → E-Mail an Kunden aus dem Case → Save | "Der Bearbeiter hat Rechnung, Notizen, Anhänge und Mailverkehr im Case. Kein Mailpostfach-Suchen." |
| 14 | AR Accountant | Manage Dispute Cases (F0702A) | **Weg A:** Case ist berechtigt → erklären: Gutschrift buchen, Ausgleich → Case schließt automatisch. Falls Gutschrift vorbereitet, in Manage Customer Line Items (F0711) den Ausgleich zeigen | "Kein manuelles Schließen. Buchhaltung und Dispute laufen synchron." |
| 15 | AR Accountant | Manage Dispute Cases (F0702A) | **Weg B:** Zweiten (vorbereiteten) Case öffnen → Status "Not justified" → Save | "Nicht berechtigt heißt: zurück ins Collections, Mahnsperre fällt, Forderung wird eingetrieben." |
| 16 | AR Accountant | Manage Dispute Cases (F0702A) | "Void Dispute Case" an einem Test-Case zeigen | "Fehlanlagen werden storniert, nicht gelöscht; Nachvollziehbarkeit bleibt." |
| 17 | Cash Specialist | Reprocess Bank Statement Items (F1520) | Nur wenn vorbereitet: Unterzahlung → Rechnung ausgleichen → Create Dispute im Clearing-Dialog → Post. Sonst Screenshot/Erklärung | "Reklamationen entstehen oft in der Zahlungsverarbeitung. Der Restposten wird direkt zum Case." |
| 18 | AR Accountant | Schedule Dispute Management Jobs (F3578) | Job "Automatic Creation of Dispute Cases" als **Testlauf** mit Buchungskreis 1010 planen → Log zeigen; Job "Automatic Write-Off of Dispute Cases" nur im Template zeigen | "Automatisierung: Restposten werden nachts zu Cases. Eskalierte Cases können automatisch ausgebucht werden." |
| 19 | AR Accountant | My Dunning Proposals (F2435) | Mahnvorschlag erzeugen → zeigen, dass die reklamierte Rechnung und die mit Zahlungsversprechen **fehlen** → PDF-Vorschau → Mahnsperre mit Grund demonstrieren | "Mahnwesen und Collections sind integriert: keine Mahnung für reklamierte oder versprochene Posten." |

Fit-to-Standard-Fragen in Block 2: Welche Reklamationsgründe gibt es heute? Wer koordiniert, wer bearbeitet (Buchhaltung, Vertrieb, Logistik)? Gibt es Freigabegrenzen für Gutschriften und Abschreibungen? Sollen Restposten aus Kontoauszügen automatisch zu Cases werden, ab welchem Betrag?

### 3.5 Reporting und Ausblick (ca. 25 min)

| # | Rolle | App | Zeigen |
|---|---|---|---|
| 20 | AR Manager | Collections Management Reporting (F4495) | Reiter Collection Progress nach Spezialist/Gruppe; Reiter Promise to Pay |
| 21 | AR Manager | Promise To Pay – Today (F1753) | Sicht "By Broken Promises (last 12 months)" |
| 22 | AR Manager | Dispute Management Reporting (F4370) | Reiter Open / Processing Days / New and Solved; Dimension Grund und Bearbeiter |
| 23 | AR Manager | Cash Collection Tracker (F3182) | Nach Strategie und Spezialist |
| 24 | AR Accountant | Display Dunning History (F2328) | Mahnhistorie des Demokunden |
| 25 | – | Folie/Erklärung | 7MA in 5 Minuten: Prioritization Rule (F8833), Teams (F2412), Manage Disputes (F7876) mit Classify/Evaluate/Decide/Finalize, Process Accounts (F8607) mit Task und Activity, BRF+-Automatisierung. Entscheidungsfrage stellen. |
| 26 | GL/AR Accountant | Doubtful Accounts Valuation (F3246) | 2PD in 5 Minuten: Wertberichtigungsschlüssel im Kundenstamm, Bewertungslauf F107 (nur erklären), Analyse F3246 zeigen, Ausbuchung F0773 erklären |

---

## Teil 4: Fit-to-Standard-Fragenkatalog und Entscheidungsbedarf

**Grundsatz**
1. BFC oder 7MA? Lizenzstatus klären. Falls 7MA: BRF+-Verantwortung im Fachbereich?
2. Soll Collections Management überhaupt für alle Kunden gelten oder nur für bestimmte Risikoklassen/Kundengruppen (Profilzuordnung per Job mit Selektion)?

**Organisation**
3. Segmente: nach Buchungskreis, Land, Vertriebsbereich, Kundengruppe?
4. Gruppen und Spezialisten: Anzahl, Zuständigkeiten, Vertretungen, Default-Gruppe je Segment.
5. Rollen: Wer bekommt AR Accountant, AR Manager, Cash Management Specialist? Braucht der Cash Specialist Dispute-Berechtigungen (F1520)?

**Strategie**
6. Welche Regeln mit welcher Gewichtung? Betragsgrenzen, Tage überfällig, Tage seit letztem Kontakt, gebrochene Versprechen, Risikoklasse aus Credit Management.
7. Aging-Perioden (Standard 30/60/90) passend?
8. Proaktiver Kontakt vor Fälligkeit (Zahlungsbedingungen berücksichtigen)?
9. Strategiewährung bei mehreren Buchungskreiswährungen.

**Mahnwesen (J59)**
10. Mahnverfahren: Stufen, Intervalle (Standard 1001: 14 Tage, 4 Stufen), Mahngebühren/Zinsen?
11. Formulare und Ausgabe: Druck vs. E-Mail, Sprachen, BRF+-Formularzuordnung.
12. Mahnsperrgründe und wer sie setzen darf.
13. Mahnlauf zentral (F150) oder je Sachbearbeiter (F2435)?

**Dispute**
14. Reklamationsgründe (Reason) und Ursachencodes (Root Cause) für das Reporting.
15. Prioritäten, Koordinator-/Bearbeiter-Modell, Beteiligung Vertrieb/Logistik.
16. Automatische Case-Anlage für Restposten: ja/nein, Betragsgrenze, Toleranzen für Kleindifferenzen.
17. Eskalation und automatische Abschreibung: Kriterien, Freigabe, Konten.
18. Korrespondenz aus dem Case: E-Mail-Templates, Absenderadressen.

**Kundenkontakt**
19. Kontaktergebnisse, Wiedervorlagegründe (Resubmission Reasons), Pflichtfelder.
20. E-Mail-Template "Customer Contact Recap" anpassen? Weitere Templates?

**Wertberichtigung (2PD)**
21. Wertberichtigungssätze je Aging-Bucket, Wertberichtigungsschlüssel je Kundengruppe.
22. Aufwandskonten für Wertberichtigung und Ausbuchung, Freigabeprozess für Ausbuchungen.
23. Ist Advanced Foreign Currency Valuation geplant? Dann funktioniert der 2PD-Bewertungslauf nicht.

**Integration**
24. Kontoauszugsverarbeitung (J78/BFB) im Scope? Nötig für Dispute aus Unterzahlung.
25. Credit Management im Scope? Risikoklasse als Strategiekriterium und zur Profilzuordnung.
26. Reporting-Anforderungen: DSO, Collection Progress, Promise-to-Pay-Quote, Bearbeitungsdauer Disputes.

---

## Teil 5: Stolperfallen für die Demo

- **Worklist wird nur nächtlich erzeugt.** Keine Live-Änderung der Strategie versprechen. Alles am Vortag einrichten und morgens prüfen.
- **Kein Mahnvorschlag**, wenn der letzte Mahnlauf jünger als 14 Tage ist oder der Sachbearbeiter nicht im Kundenstamm steht.
- **F1520 ohne Dispute-Katalog** zeigt keinen "Create Dispute"-Button. Rolle vorher anpassen oder den Weg nur erklären.
- **Dispute Case schließt erst beim Ausgleich** der Rechnung mit der Gutschrift. Wenn keine Gutschrift vorbereitet ist, das Verhalten erklären statt zeigen.
- **E-Mail-Versand** braucht Output-Konfiguration. Vorschau reicht für die Demo.
- **2PD-Bewertungslauf** ist ein klassischer Batch-Dialog (F107) und wirkt in der Demo sperrig. Nur F3246 live zeigen.
- **Demodaten in Starter-Systemen** werden von SAP gelegentlich aktualisiert. Am Vortag prüfen, ob `S10100251` noch die erwarteten Posten hat.

## Anhang: App-Spickzettel

| App | ID | Rolle | Zweck |
|---|---|---|---|
| Manage Collection Strategies | F2946 | AR Manager | Strategie, Regeln, Aging |
| Manage Collection Groups | UDM_GROUP | AR Manager | Gruppen, Strategie-Zuordnung, Spezialisten |
| Assign Collection Groups to Segments | UDM_GROUP2SGMT | AR Manager | Gruppe ↔ Segment |
| Manage Collections Master Data | F5400 | AR Manager | Profil, Gruppe, Spezialist je Kunde |
| Schedule Collections Management Jobs – Mass Changes | F3918 | AR Accountant | Profil-/Segment-/Spezialisten-Massenänderung |
| Define Accounting Clerks | S_ALR_87003335 | AR Manager | Sachbearbeiter |
| Manage Customer Master Data | F0850A | AR Accountant | Mahndaten, Sachbearbeiter, Wertberichtigungsschlüssel |
| Process Collections Worklist | F0380 | AR Accountant | Worklist Spezialist |
| Supervise Collections Worklist | F2375 | AR Manager | Worklist Manager |
| Process Receivables | F0106A | AR Accountant | Kundencockpit |
| Manage Promises to Pay / Resubmissions / Contact Persons / Customer Contacts | F4710 / F4709 / F4708 / F4707 | AR Accountant | Objekte aus dem Kundenkontakt |
| Manage Dispute Cases – As Coordinator | F0702A | AR Accountant | Dispute-Bearbeitung |
| Schedule Dispute Management Jobs | F3578 | AR Accountant | Auto-Anlage, Auto-Write-Off |
| Reprocess Bank Statement Items | F1520 | Cash Specialist | Dispute aus Unterzahlung |
| My Dunning Proposals / Create Dunning Notices / Display Dunning History | F2435 / F150 / F2328 | AR Accountant | Mahnwesen |
| Create Correspondence / Display Correspondence History | F0744A / F2934 | AR Accountant | Kontoauszug, OP-Liste usw. |
| Dispute Management Reporting / Open Disputes / Overdue in Dispute / Solved / New vs Solved / Processing Days | F4370 / F1752 / F2540 / F2521 / F2523 / F2522 | AR Manager | Dispute-Reporting |
| Collections Management Reporting / Collection Progress / Promise to Pay / Cash Collection Tracker | F4495 / F1738 / F1753 / F3182 | AR Manager | Collections-Reporting |
| Perform Further Valuations / Doubtful Accounts Valuation / Clear Incoming Payments – Manual Clearing | F107 / F3246 / F0773 | GL/AR Accountant | 2PD |
| 7MA: Manage Account Prioritization Rules / Manage Teams / Manage Master Data C&DA / Manage Disputes / Manage Receivable Items / Process Worklist / Process Accounts / Manage Activities | F8833 / F2412 / F8606 / F7876 / F7877 / F8832 / F8607 / F8610 | AR Manager / Accountant | Alternative 7MA |
| 7MA Jobs: Collections / Dispute Resolution / Integration / RPI | F8376 / F8713 / F8377 / F8418 | AR Accountant / BPC Expert | Worklist, Eskalation, Datenübernahme |
