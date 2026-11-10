# Moderations-/Demo-Skript — F2S Explore-Workshop #2.4: Period-End Closing & Tax

**Projekt:** SAP S/4HANA Cloud Public Edition — Flughafen Düsseldorf (DUS) | Deloitte
**Datum:** 16. Juli 2026 · **Dauer:** 3 Std. (davon ~90 Min. Live-Demo)
**Scope Items:** J58 (Accounting & Financial Close) · 2OO (Externe Steuerprüfung) · 1J2 (Compliance-Formate) · 5XU (Document & Reporting Compliance)
**Systembasis:** S/4HANA Cloud Public Edition, Release 2602 — Starter-/Demosystem (Buchungskreise 10DE–60DE, HGB als Leading Ledger 0L)
**Präsentation:** Moritz Göthel (Deloitte, Workstream Lead Accounting/FI)

> **Lesehilfe für den Präsentator:** Jede App ist nach demselben Schema aufgebaut:
> **① Die App** (Name + Fiori-ID/Tcode) — **② Businesskontext** (Warum? Fachlicher Bezug zum Abschluss-/Steuerprozess bei FDG) — **③ App-Funktionsweise** (Was die App tut & was ich konkret live zeige).
> *Sprechtext ist kursiv als „O-Ton" markiert. Zeitangaben sind Richtwerte laut Agenda.*

---

## 0. Einstieg (00:00 – 00:20 | 20 Min.)

### 0.1 Begrüßung, Ziele & Agenda (10 Min.)

**O-Ton:** *„Herzlich willkommen zum vierten Workshop unserer F2S-Explore-Serie. Heute geht es um zwei Themenblöcke: den periodischen Monats- und Jahresabschluss und alle relevanten Steuerthemen. Wichtig vorab drei Punkte:*
- *Das ist eine **Explore-Demo, kein Training** — wir zeigen, **was der Standard kann**, und gleichen ihn mit Ihren heutigen FDG-Prozessen ab (Fit-to-Standard).*
- *Wir zeigen **ausschließlich S/4HANA-Public-Cloud-Standardprozesse** — keine kundenspezifischen Erweiterungen, BTP-Entwicklungen oder Add-ons.*
- *Wir arbeiten im **Starter-/Demosystem**. Einzelne Apps sind ggf. noch nicht freigeschaltet — falls ja, halte ich das transparent fest und wir reproduzieren es in einem Folgetermin.*
- *Alles, was über den Standard hinausgeht, sammeln wir strukturiert im **Diskussionsblock als Gap** — nicht während der Demo."*

**Agenda kurz zeigen:** Recap → Demo Teil 1 (Closing, 50 Min.) → Pause → Demo Teil 2 (Tax, 40 Min.) → Diskussion/Fit-to-Standard (45 Min.) → Zusammenfassung & Action Items.

### 0.2 Recap: FDG-Anforderungen aus dem GL-Workshop (10 Min.)

**O-Ton:** *„Kurzer Rückgriff auf den Hauptbuch-Workshop vom 06.07.: Dort haben wir bereits mehrere Closing- und Steuerthemen aufgenommen — u. a. Rückstellungsspiegel mit Bewegungsarten, vorerfasste Belege auf Sachkonten inkl. Saldo, die Massen-/Upload-Buchungen und das Thema DRC vs. heutiger Elster-Prozess. Diese Punkte greifen wir heute an den passenden Stellen wieder auf."*

*(Offene Punkte an der Stelle nur benennen, nicht ausdiskutieren — Verweis auf Diskussionsblock Abschnitt 4.)*

---

## Teil 1 — Period-End Closing im Standard (00:20 – 01:10 | ~50 Min.)
### Scope Item J58 — Accounting & Financial Close

**Überleitung O-Ton:** *„Wir gehen den Abschluss in der Reihenfolge durch, in der er auch fachlich abläuft: erst die Periodensteuerung, dann periodische Buchungen und Abgrenzungen, dann Bewertung/Umgliederung, Spiegeldarstellungen und zum Schluss das Abschluss-Reporting."*

---

### 2.1 Steuerung der Buchungsperioden (~6 Min.)

#### ① Die App
- **Buchungsperioden verwalten** — *Manage Posting Periods* · **F2293**
- **Buchungsperiodenvarianten verwalten** — *Manage Posting Period Variants* · **F2581**
- *(Ergänzend im Standard: Buchungsperioden – Kostenrechnung · F4684)*

#### ② Businesskontext
Am Monats-/Jahresultimo muss gesteuert werden, **wer ab wann noch in welche Periode buchen darf**. Das ist die erste Kontrolle jedes Abschlusses: Vergangene Perioden werden für die operativen Buchungen geschlossen, für die Abschlussbuchhaltung aber gezielt offen gehalten. Für FDG relevant, weil pro Buchungskreis (10DE–60DE) eine saubere, getrennte Periodensteuerung sichergestellt sein muss.

#### ③ App-Funktionsweise — was ich zeige
- Öffnen/Schließen einer Periode **je Kontoart**: **S** (Sachkonto), **D** (Debitor), **K** (Kreditor), **A** (Anlage), **M** (Material) — und je **Kontenintervall**.
- Zwei Perioden-Intervalle (laufende Periode + Sonder-/Korrekturperioden) und das Prinzip der **jahresübergreifenden Buchung**.
- **Berechtigungsgruppen**: nur berechtigte Rollen dürfen in noch offene „Abschluss-Perioden" buchen.
- In **F2581** zeige ich, dass **jeder Buchungskreis seine eigene Periodenvariante** hat — zentrale Steuerung erfolgt über Berechtigungen.

**O-Ton:** *„Der Standard trennt sauber nach Kontoart und Kontenbereich — so können Sie z. B. für die Fachbereiche schließen, für das Rechnungswesen aber noch offen lassen. Genau dieses zweistufige Schließen ersetzt manuelle Absprachen."*

---

### 2.2 Periodische Buchungen: Dauerbuchungen & manuelle Abgrenzungen (~10 Min.)

#### ① Die App
- **Dauerbuchungsbelege anlegen/verwalten** — *Manage Recurring Journal Entries* · **F1598**
- Ergänzend: **Hauptbuchbeleg buchen** (mit *Buchen mit automatischer Stornierung* / Auto-Reverse), **Hauptbuchbelege hochladen** (Excel-Massen-Upload), **Buchungsbelege verwalten** (Kopieren/Umkehrbuchung).

#### ② Businesskontext
Wiederkehrende gleichartige Buchungen (Mieten, Leasing, Versicherungen, planmäßige Abgrenzungen) sollen nicht jeden Monat manuell erfasst werden. Und periodenfremder Aufwand/Ertrag muss **periodengerecht abgegrenzt** werden. Beides sind Kern-Tätigkeiten jedes Monatsabschlusses bei FDG.

#### ③ App-Funktionsweise — was ich zeige
- **Dauerbuchung (F1598):** Anlegen eines Dauerbuchungsbelegs mit **definiertem Rhythmus** (z. B. monatlich) und Laufzeit; der terminierte Lauf erzeugt automatisch die periodischen Belege.
- **Auto-Reverse:** manuelle Abgrenzung mit **automatischer Stornierung** zum Folgeperiodenbeginn — ein Beleg, der sich selbst zurückdreht.
- **Journal Entry Template:** Buchungsvorlagen für wiederkehrende manuelle Buchungen.
- **Massen-Upload:** Standard-App „Hauptbuchbelege hochladen" mit **Excel-Vorlage** — wichtig für den späteren Abgleich mit den heutigen CSV-Strukturen von FDG *(→ Gap-Diskussion 4)*.

**O-Ton:** *„Für die periodengerechte Abgrenzung gibt der Standard Ihnen zwei Wege: die manuelle Abgrenzung mit Auto-Reverse und die planbare Dauerbuchung. Beim Massen-Upload schauen wir uns in der Diskussion die Vorlage gemeinsam an — da wollen wir Ihre heutigen CSV-Strukturen abgleichen."*

---

### 2.3 Abgrenzungsmanagement — Accruals Management (~8 Min.)

#### ① Die App
- **Bestellabgrenzungen prüfen (für Kostenrechner)** — *Review Purchase Order Accruals - For Cost Accountant* · **F3552**
- **Bestellabgrenzungen anzeigen** — *Display Purchase Order Accruals* · **F3928**
- **Schedule Accruals Jobs** · **F3778** (Job-Template *„Purchase Order Accruals - Post Periodic Accruals"*)
- *(Analyse: Accrual Postings – Simulated/Posted · W0184; Analyze Accrual Postings · F3732)*

#### ② Businesskontext
Für **bestellbezogene** Sachverhalte (Wareneingang/Leistung erbracht, Rechnung fehlt noch) bietet der Standard eine **automatisierte, periodengerechte Abgrenzung über den Leistungszeitraum** — als systemgestützte Alternative zur manuellen Abgrenzung. Relevant für FDG überall dort, wo Leistungen über mehrere Perioden laufen.

#### ③ App-Funktionsweise — was ich zeige
- **F3552 (Review):** der Kostenrechner sieht **vorgeschlagene vs. gebuchte** Abgrenzungsbeträge über den Leistungszeitraum und gibt sie im **Standard-Review-Prozess** frei.
- **F3928 (Display):** analytische Sicht auf die PO-Abgrenzungen.
- **F3778 (Schedule Accruals Jobs):** der eigentliche „Vorschlagen/Buchen"-Schritt ist hier ein **Job-Template** — ich zeige, wie der automatisierte Abgrenzungslauf terminiert wird.

**O-Ton:** *„Der Unterschied zu 2.2: Hier leitet das System die Abgrenzung aus der Bestellung und dem Leistungsfortschritt selbst ab — der Cost Accountant prüft und gibt frei, statt jede Abgrenzung manuell zu rechnen."*

---

### 2.4 Bewertung & Umgliederung (~12 Min.)

#### ① Die App
- **Forderungen/Verbindlichkeiten umgliedern** — *Regroup Receivables / Payables* · **FAGLF101** (Fiori-App behält die klassische ID)
- Ergänzend als Standard-Bewertungsläufe (Kurzvorstellung): **Fremdwährungsbewertung** (Advanced Foreign Currency Valuation · F3753 / Post Currency Adjustments · F1606), **Wertberichtigung nach IFRS 9 / ECL** · **F107**.

#### ② Businesskontext
Zum Abschluss müssen Bilanzposten **richtig ausgewiesen** werden: Forderungen/Verbindlichkeiten **nach Restlaufzeit** umgegliedert (kurz-/langfristig), Fremdwährungsposten neu bewertet und ausfallrisikobehaftete Forderungen wertberichtigt. Das sind klassische HGB-/IFRS-Abschlussbewertungen, die FDG heute teils manuell aufbereitet.

#### ③ App-Funktionsweise — was ich zeige
- **FAGLF101:** **Bilanzumgliederung nach Fristigkeit** — das System klassifiziert Forderungen/Verbindlichkeiten nach Restlaufzeit und erzeugt die Umgliederungsbuchungen; Storno zum Folgemonat.
- Kurzvorstellung: **Abzinsung langfristiger Posten** und **kreditrisikobasierte Wertberichtigung (IFRS 9/ECL, F107)** als weitere Standard-Bewertungsläufe.

**O-Ton:** *„Die Fristigkeits-Umgliederung, die heute oft in Excel läuft, ist im Standard ein Bewertungslauf mit nachvollziehbaren Buchungen — inkl. automatischem Storno in der Folgeperiode."*

---

### 2.5 Statement of Changes / Spiegeldarstellungen im Standard (~6 Min.)

#### ① Die App
- **Statement of Changes in General Ledger** (Standard-Entwicklungsdarstellung je Konto mit Bewegungsarten).

#### ② Businesskontext
Für Anhang und interne Zwecke werden **Spiegel** benötigt (z. B. Rückstellungsspiegel: Anfangsbestand → Zuführung/Verbrauch/Auflösung → Endbestand). FDG hat hier im GL-Workshop bereits einen konkreten Bedarf angemeldet.

#### ③ App-Funktionsweise — was ich zeige
- Standardauswertung der **Kontenentwicklung je Konto mit Bewegungsarten**.
- **Voraussetzungen & Grenzen ehrlich benennen:** Der Spiegel im Standard setzt **OP-geführte Konten und gepflegte Bewegungsarten** voraus. **Altsalden, die nicht OP-geführt sind**, erscheinen nicht automatisch mit Bewegungsart — das ist ein **Migrations-/Gap-Thema** *(→ Diskussion 4)*.

**O-Ton:** *„Hier bin ich bewusst transparent: Der Standard-Spiegel funktioniert sauber für OP-geführte Konten mit Bewegungsarten. Für Ihre Altbestände nehmen wir das als Gap und Migrationsthema mit — das gehört in die Diskussion, nicht in die Demo."*

---

### 2.6 Abschluss-Reporting: Bilanz & GuV (~8 Min.)

#### ① Die App
- **Bilanz/GuV** — *Balance Sheet / Income Statement* · **F0708** *(Hinweis: F0708, nicht F0996)*
- **Bilanz/GuV mehrdimensional** — *…Multidimensional* · **W0161** (nach Profit-Center/Segment; „W" = Analyse-App)
- **Summen-/Saldenliste** — *Trial Balance* · **F0996** (Vergleichsvariante W0097)
- **Schedule General Ledger Jobs** · **F1927** (Job-Template *Carry Forward Balances* = Saldovortrag)

#### ② Businesskontext
Das Ergebnis des Abschlusses: **Bilanz und GuV** auf Knopfdruck, mehrdimensional auswertbar, plus **Saldovortrag** ins neue Geschäftsjahr. Für FDG die Standard-Alternative zu heutigen Report-Aufbereitungen — inkl. Sicht nach Profit-Center/Segment.

#### ③ App-Funktionsweise — was ich zeige
- **F0708:** Standard-**Bilanz & GuV** über die Bilanz/GuV-Struktur.
- **W0161:** dieselbe Auswertung **mehrdimensional** (Profit-Center/Segment) — Drill-down live.
- **F0996 (Trial Balance):** Summen-/Salden, Year-to-Date-Balances, Vortragsstatus.
- **F1927:** der **Saldovortrag** als Job-Template (*Carry Forward Balances*) — Jahreswechsel-Aktivität; Status über *Balance Carryforward Status* (F4683).

**O-Ton:** *„Wichtig für die Namensgebung: Bilanz/GuV ist F0708, die Summen-/Saldenliste F0996 — die verwechselt man leicht. Der Saldovortrag ist kein separates Programm mehr, sondern ein Job im ‚Schedule General Ledger Jobs'."*

**Überleitung zur Pause:** *„Damit ist der Abschlussblock im Standard durch. Nach der Pause gehen wir in die Steuerthemen."*

---

## Pause (01:10 – 01:20 | 10 Min.)

---

## Teil 2 — Tax / Steuern im Standard (01:20 – 02:00 | ~40 Min.)
### Scope Items: 2OO (Externe Steuerprüfung) · 1J2 (Compliance-Formate) · 5XU (Document & Reporting Compliance)

**Überleitung O-Ton:** *„Im Steuerblock gehen wir vom Fundament aus: erst Steuerkennzeichen und -konten, dann die USt-Voranmeldung mit Zahllast, die Meldungen (ZM/Außenwirtschaft), die zentrale Compliance-Plattform DRC, die Steuer-Abstimmung und zum Schluss der Prüferzugriff."*

---

### 3.1 Steuer-Grundlagen: Steuerkennzeichen & Steuerkonten (~5 Min.)

#### ① Die App
- **Steuerinformationen je Land/Region anzeigen** — *Display Tax Information per Country-Region* · **S_ALR_87012365**
- Ergänzend (Config/Display): Steuerkennzeichen (Vorsteuer/Ausgangssteuer), Zuordnung Steuerkonten, Sachkonten-Steuerkategorie.

#### ② Businesskontext
Jede steuerrelevante Buchung hängt an einem **Steuerkennzeichen**, das Steuersatz, -art und **Steuerkonto** steuert. Das ist das Fundament für alle folgenden Meldungen. Für FDG entscheidend: Sind Vorsteuer, Ausgangssteuer und Einfuhrumsatzsteuer sauber abgebildet?

#### ③ App-Funktionsweise — was ich zeige
- Überblick über **Vorsteuer- und Ausgangssteuer-Kennzeichen** und ihre Kontenzuordnung.
- **Standard-Prinzip:** je **ein** Vorsteuer- und **ein** Ausgangssteuerkonto mit mehreren Steuerkennzeichen; **Einfuhrumsatzsteuer separat**.
- **Steuerinformationen je Land/Region** als Nachschlage-/Prüfsicht.

**O-Ton:** *„Bitte halten Sie hier Ihre Liste der heute genutzten Steuerkennzeichen bereit — die verifizieren wir gegen den Standard (Vorsteuer, Ausgangssteuer, Einfuhr-USt)."*

---

### 3.2 Umsatzsteuer-Voranmeldung & Zahllast (~9 Min.)

#### ① Die App
- **Umsatzsteuervoranmeldung erstellen** — *Advance Return for Tax on Sales/Purchases* · **S_ALR_87012357** (Report RFUMSV00)
- **Steuerverbindlichkeiten buchen** — *Post Tax Payables* · **F1597**
- **Schedule Tax Jobs** · **F3690**
- *(Modernes Filing zusätzlich über „Run Statutory Reports" / DRC → 3.4)*

#### ② Businesskontext
Die **USt-Voranmeldung** ist die zentrale periodische Steuerpflicht: Ermittlung der Zahllast/des Erstattungsanspruchs und Übermittlung ans Finanzamt. FDG macht dies heute über einen (teils manuellen) Elster-Prozess — wir zeigen die Standard-Abdeckung.

#### ③ App-Funktionsweise — was ich zeige
- **S_ALR_87012357:** Erstellung der Voranmeldung (RFUMSV00); im Standard enthalten: **Dauerfristverlängerung**, **Sondervorauszahlung** und **Input Tax from Parked Documents** (Vorsteuer aus vorerfassten Belegen).
- **F1597 (Post Tax Payables):** Buchung der **Zahllast** auf das Steuer-/Verrechnungskonto.
- **F3690 (Schedule Tax Jobs):** Batch-/Stapelverarbeitung des Steuerlaufs im Standard.

**O-Ton:** *„Die drei Schritte — ermitteln, Zahllast buchen, terminieren — bildet der Standard vollständig ab. Ob Sie manuell per Elster melden oder über die DRC-Plattform, sehen wir gleich in 3.4."*

---

### 3.2a Praxisbeispiel: Zahllast ermitteln & buchen (DUS, Juni 2026)

> **Demo-/Schulungsbeispiel auf Basis des echten DUS-Datensatzes** (Flughafen Düsseldorf GmbH, Buchungskreis **10DU**, Ledger 0L, Voranmeldungszeitraum **01.06.–30.06.2026**, Report RFUMSV00 / CB9980000015). Kontenplan: **YCOA**.

#### Schritt 1 — Wie das System die Zahllast ermittelt

Die Zahllast **rechnest du nicht selbst** — sie ist das Ergebnis der USt-Voranmeldung (S_ALR_87012357 / RFUMSV00). Maßgeblich ist die Seite **„Salden aller Buchungskreise"**, Spalte **„Saldo in Meldewährung"**:

| Steuerart | Kz. | Bedeutung | Satz | Betrag |
|---|---|---|---|---|
| Ausgangssteuer (MWS) | A0 | nicht steuerbar | 0 % | 0,00 |
| **Ausgangssteuer (MWS)** | **A1** | Inland voller Satz | 19 % | **−5.395,96** (Haben) |
| Vorsteuer (VST) | V0 | nicht steuerbar | 0 % | 0,00 |
| **Vorsteuer (VST)** | **V1** | voller Satz | 19 % | **198,59** (Soll) |
| **Saldo in Meldewährung** | | | | **−5.197,37** |

Nur **A1** (Ausgangssteuer 19 %) und **V1** (Vorsteuer 19 %) tragen Steuerbeträge; A0/V0 sind 0 % (nicht steuerbar) und werden nicht umgebucht.

```
  Ausgangssteuer   5.395,96  (Haben-Saldo auf 22000000)
− Vorsteuer          198,59  (Soll-Saldo auf 12600000)
= Zahllast         5.197,37  EUR  → Verbindlichkeit ggü. Finanzamt
```
Das negative Vorzeichen des Saldos (−5.197,37) bedeutet **Zahllast** — man schuldet dem Finanzamt.

#### Schritt 2 — Das Posting (Post Tax Payables / F1597)

**Beleg — Zahllastbuchung, BuKr 10DU, Belegart SA, Buchung ohne Steuerkennzeichen:**

| Pos. | S/H | Konto | Bezeichnung | Betrag (EUR) |
|---|---|---|---|---|
| 1 | **Soll** | 22000000 | Ausgangssteuer (MWS) | 5.395,96 |
| 2 | **Haben** | 12600000 | Vorsteuer (VST) | 198,59 |
| 3 | **Haben** | 22090000 | Umsatzst. Zahllast | 5.197,37 |

**Prüfung:** Soll 5.395,96 = Haben (198,59 + 5.197,37 = 5.395,96) ✓ — Beleg ausgeglichen. Danach sind 22000000 und 12600000 saldiert (= 0), auf **22090000** steht die Zahllast von **5.197,37 EUR**.

#### Schritt 3 — Warum man so bucht und was die Buchung bedeutet

**Was liegt vor der Buchung auf den Konten — und warum?** Diese Salden entstehen **automatisch im laufenden Betrieb**, nicht durch eine bewusste Steuerbuchung:
- **Ausgangssteuer (22000000):** Jede **Ausgangsrechnung** an einen Kunden enthält 19 % USt. Diese USt gehört nicht dem Flughafen — sie wird **im Auftrag des Staates eingezogen** und steht als **Haben-Saldo** (Verbindlichkeit ggü. Finanzamt).
- **Vorsteuer (12600000):** Jede bezahlte **Eingangsrechnung** enthält Vorsteuer, die man sich vom Staat **zurückholen** darf → **Soll-Saldo** (Forderung ans Finanzamt).

**Was macht die Zahllastbuchung?** Das USt-System verlangt **Verrechnung**: nicht die volle Ausgangssteuer zahlen und separat die Vorsteuer zurückholen, sondern nur die **Differenz** ans Finanzamt abführen. Die Buchung räumt die einzelnen Steuerkonten leer und **bündelt die tatsächliche Schuld auf einem Verbindlichkeitskonto (22090000)**.

**Warum diese Soll-/Haben-Seiten?** Ein Konto stellt man glatt, indem man die *entgegengesetzte* Seite seines Saldos bebucht — die Seite ist also nicht willkürlich, sondern zwingend:

| Konto | Saldo vorher | Gegenbuchung | Fachliche Bedeutung |
|---|---|---|---|
| 22000000 Ausgangssteuer | **Haben** 5.395,96 | im **Soll** | Verbindlichkeit wird aufgelöst |
| 12600000 Vorsteuer | **Soll** 198,59 | im **Haben** | Forderung wird aufgelöst |
| 22090000 Zahllast | 0 | im **Haben** (Differenz) | neue, gebündelte Verbindlichkeit entsteht |

**Warum ein eigenes Zahllastkonto (22090000)?**
1. **Klarheit:** Die Arbeitskonten 22000000/12600000 sind danach wieder **auf null** — bereit für die nächste Periode, keine Vermischung von Zeiträumen.
2. **Ein Betrag = eine Zahlung:** Auf 22090000 steht **exakt der ans Finanzamt zu überweisende Betrag** (5.197,37 EUR); die spätere Bankzahlung bucht gegen dieses Konto.
3. **Nachvollziehbarkeit:** Der Saldo muss dem in der Voranmeldung gemeldeten Betrag entsprechen — genau das prüft *Tax Declaration Reconciliation (F2096)*.

**Der Kreislauf in einem Bild:**
```
 laufender Betrieb          Periodenende (F1597)         Zahlung
 ────────────────           ──────────────────           ────────
 Ausgangsrechnungen  ─┐
   → 22000000 (H)     ├──►  Verrechnung auf     ──►  22090000 ──► Bank
 Eingangsrechnungen  ─┘     22090000 = Zahllast       (Soll)      (Haben)
   → 12600000 (S)                                     Schuld beglichen
```

**In einem Satz:** Die Zahllastbuchung übersetzt die vielen einzelnen, automatisch entstandenen Steuerbeträge in **die eine Zahl, die man dem Finanzamt tatsächlich schuldet**, parkt sie auf einem klaren Verbindlichkeitskonto und macht die Arbeitskonten für die nächste Periode frei.

#### Schritt 4 — Zahlung ans Finanzamt buchen (Post Outgoing Payments / F1612)

> **DUS-Vorgehen:** Die Zahlung wird **direkt über *Post Outgoing Payments* (F1612)** gebucht — kein Umweg über einen Finanzamt-Kreditor oder den automatischen Zahllauf.

Die Zahllastbuchung (Schritt 2) hat auf **22090000** nur eine offene Verbindlichkeit erzeugt. Die eigentliche Zahlung lässt das Geld abfließen und gleicht diesen Posten aus. **F1612** kann das in **einem Schritt**, weil die App den offenen Posten **direkt auf dem Sachkonto** ausgleicht (nicht nur über Kreditor/Debitor):

- **App:** *Post Outgoing Payments* · **F1612**
- **Bankseite:** Auswahl des Hausbank-/Bankkontos, Betrag **5.197,37 EUR** → Haben.
- **Ausgleichsseite:** offenen Posten auf **22090000 (Umsatzst. Zahllast)** auswählen und gegenbuchen → Soll.

| Pos. | S/H | Konto | Bezeichnung | Betrag (EUR) |
|---|---|---|---|---|
| 1 | **Soll** | 22090000 | Umsatzst. Zahllast *(offener Posten ausgeglichen)* | 5.197,37 |
| 2 | **Haben** | 11xxxxxx | Bank (Kontokorrent) | 5.197,37 |

Nach dieser Buchung ist **22090000 = 0** und der gesamte USt-Kreislauf für den Zeitraum geschlossen (alle Steuerkonten glatt).

> **Voraussetzung:** Das Zahllastkonto **22090000 muss OP-geführt** (open-item managed) sein, damit F1612 Zahllast und Zahlung gegeneinander ausgleichen kann. → **im YCOA-Setup verifizieren.**

**O-Ton:** *„Die Zahlung buchen wir direkt über *Post Outgoing Payments*: Bank im Haben, das offene Zahllastkonto im Soll. Einen eigenen Finanzamt-Kreditor oder den Zahllauf brauchen wir dafür im Standard nicht."*

> **Hinweis Sonderfall Vorsteuerüberhang:** Übersteigt die Vorsteuer die Ausgangssteuer, dreht sich das Vorzeichen — 22090000 hat dann einen **Soll-Saldo** (Erstattungsanspruch), Positionen 1 und 3 tauschen die S/H-Seite. In der Praxis erzeugt der Update-Lauf von RFUMSV00 / F1597 diese Umbuchung **automatisch**; die Tabelle oben zeigt, was das System dabei bucht.

---

### 3.3 Zusammenfassende Meldung & Außenwirtschaftsmeldungen (~6 Min.)

#### ① Die App
- **Zusammenfassende Meldung** — *EC Sales List* · über **F1515** (*Run Statutory Reports*, Länder­variante DE, DME-Format)
- **Außenwirtschafts-Meldungen Z4 / Z5A** (AWV, Deutschland)

#### ② Businesskontext
Für innergemeinschaftliche Lieferungen/Leistungen ist die **Zusammenfassende Meldung (ZM)** Pflicht; für den Zahlungsverkehr mit dem Ausland die **AWV-Meldungen Z4/Z5A**. FDG erstellt die ZM heute in einem manuellen Format — Standard-Ziel ist die job-gesteuerte Erzeugung.

#### ③ App-Funktionsweise — was ich zeige
- **ZM** als Report-Definition **innerhalb von Run Statutory Reports (F1515)**, Ländervariante DE, **DME-Format**, job-gesteuert.
- **Z4/Z5A**: die deutschen Außenwirtschafts-Meldungen aus dem Standard.

**O-Ton:** *„Statt eines manuell gepflegten ZM-Formats erzeugt der Standard die Meldung job-gesteuert im DME-Format. Ihr heutiges ZM-Format bitte zum Abgleich bereithalten."*

---

### 3.4 Document & Reporting Compliance — DRC (5XU / 1J2) (~11 Min.)

#### ① Die App
- **Run Statutory Reports** — Reporting-Dashboard · **F1515** (*Define Statutory Reports* = F2131)
- **Manage Electronic Documents / eDocument Cockpit** · **EDOC_COCKPIT**

#### ② Businesskontext
**DRC** ist die zentrale Standard-Plattform für **gesetzliche Steuermeldungen und E-Belege**: sie bündelt USt-Voranmeldung, ZM und Audit-Reports, übernimmt die **elektronische Übermittlung an Behörden** (Elster-Anbindung) und deckt das Zusammenspiel mit der **E-Rechnung** ab. Für FDG die Ablösung des heutigen manuellen Elster-Prozesses — mit **Lizenzaspekt** (>24 Meldungen, siehe 5XU/1J2).

#### ③ App-Funktionsweise — was ich zeige
- **F1515 (Run Statutory Reports):** das DRC-Dashboard — Advanced VAT Return, EC Sales List, Audit; **Reporting-Phasen & Status-Monitoring** in einem zentralen Cockpit.
- **EDOC_COCKPIT (Manage Electronic Documents):** **elektronische Übermittlung** an die Behörde (Elster im Standard), **Analyse-, Vorschau- und manuelle Anpassungsfunktion**, **Standard-Genehmigungsworkflow** (Team, Freigabestufen) und Geschäftspartner-Korrespondenz per E-Mail.

**O-Ton:** *„Hier liegt der große Standard-Hebel: eine Plattform, ein Status-Dashboard, ein Freigabeworkflow für alle gesetzlichen Meldungen. Zum Lizenzthema — die Grenze von 24 Meldungen pro Jahr — nehmen wir uns in der Diskussion Zeit, das ist für Ihre Anzahl Buchungskreise relevant."*

*Hintergrund für Rückfragen:* **5XU** aktiviert/steuert die erweiterten DRC-Funktionen (E-Invoicing, E-Reporting) auf Länderebene; **1J2** liefert die länderspezifischen **Compliance-Formate** für die manuelle Einreichung (Anzeige/Ausgabe). Für Lizenzen vor Q4/2021: >24 Meldungen p. a. erfordern ggf. Zusatzlizenz.

---

### 3.5 Steuer-Abstimmung (~5 Min.)

#### ① Die App
- **Tax Reconciliation Account Balance** — Abstimmung Steuerkontensaldo · **F2095**
- **Tax Declaration Reconciliation** — Abstimmung Steuermeldung · **F2096**

#### ② Businesskontext
Vor der Abgabe muss die **Steuermeldung gegen die Buchhaltung abgestimmt** werden: Stimmen die gemeldeten Beträge mit den Salden der Steuerkonten überein? Und ist die ZM plausibel gegenüber der USt-Voranmeldung? Das ist die Qualitätssicherung des Steuerprozesses.

#### ③ App-Funktionsweise — was ich zeige
- **F2095:** Abstimmung des **Steuerkontensaldos** gegen die gebuchten Steuerbeträge.
- **F2096:** **Abstimmung der Steuermeldung** inkl. **Plausibilisierung ZM vs. USt-Voranmeldung**.

**O-Ton:** *„Diese beiden Apps geben Ihnen die Sicherheit, dass Gemeldetes und Gebuchtes zusammenpassen — bevor die Meldung rausgeht."*

---

### 3.6 Elektronische Steuerprüfung & externer Prüferzugriff — 2OO (~4 Min.)

#### ① Die App
- **Externer Prüfer — Direkt-/Lesezugriff** (*External Auditor Direct (Read) Access*)
- Standard-**Auditstruktur** (SAIS / Audit Information System), **Audit Journal**, **Generic Audit Filter (GAF)**; Prüfer erreichen Daten u. a. über **F2095 / F2096** (lesend).

#### ② Businesskontext
Externe Steuerprüfer sollen **steuerrelevante Daten direkt im System, aber schreibgeschützt** einsehen können — mit der Hard-/Software des Steuerpflichtigen auswählen, filtern, sortieren (Bezug euBP / GDPdU). Das reduziert Datenexporte und Medienbrüche gegenüber heute.

#### ③ App-Funktionsweise — was ich zeige
- **Auditor Direct Access:** Zugriff im **Read-only-Modus** über die **Standard-Auditstruktur**.
- **Audit Journal / Audit-Protokoll** und **Generic Audit Filter** mit **Zeit-/Datenrestriktionen**.
- Verweis: die Abstimm-Apps (F2095/F2096) sind für den Prüfer lesend erreichbar.

**O-Ton:** *„Der Prüfer arbeitet direkt im System, sieht nur was er sehen darf, kann nichts verändern — und Sie behalten über die Restriktionen die Kontrolle."*

---

## 4. Diskussion — Fit-to-Standard & Gaps (02:00 – 02:45 | ~45 Min.)

**O-Ton:** *„Jetzt gleichen wir das Gezeigte mit Ihren heutigen Prozessen ab. Alles, was über den Standard hinausgeht, halten wir als Gap für die spätere Bewertung in Design/Realize fest — das sind keine Demo-Punkte."*

**Bekannte Gaps / Diskussionsitems (aus Vorbereitung & GL-Workshop):**
1. **Rückstellungsspiegel mit Bewegungsarten** — im Standard nur eingeschränkt; **Altsalden (nicht OP-geführt)** = Migrationsthema *(vgl. 2.5)*.
2. **Automatisierter Self-Service-Meldeprozess** der Fachbereiche (Workflow) über das reine Accruals Management hinaus.
3. **Ertragsteuern** (GewSt/KSt, §60(2)-Überleitung, Hinzurechnungen/Kürzungen): **kein Steuerledger im Standard** — separate Bewertung.
4. **Massen-/Upload-Buchungen:** Abgleich Standard-Upload-Vorlage ↔ heutige CSV-Strukturen (gemeinsame vs. getrennte Dateien) *(vgl. 2.2)*.
5. **Vorerfasste Belege auf Sachkonten inkl. Saldo anzeigen** — Verfügbarkeit im Standard (offener Punkt aus GL-Workshop).
6. **USt-Voranmeldung & ZM über DRC** statt manuellem Elster-Prozess — Standard-Abdeckung, **Lizenzaspekt (>24 Meldungen)**, Zeitschiene *(vgl. 3.4)*.

**Moderationshinweis:** je Gap kurz festhalten — *Ist-Prozess FDG · Standard-Deckungsgrad · offene Frage · Verantwortliche(r) · nächster Schritt*.

---

### 4.1 Vertiefung Gap 3 — Ertragsteuern (Gesprächsleitfaden)

> **Zweck:** souverän erklären, **warum** Ertragsteuern ein Gap sind und **was** der Standard trotzdem hergibt. **Kein Demo-Prozess** — reine Diskussion.

#### Erste Klarstellung: Ertragsteuern ≠ die eben gebuchte Umsatzsteuer

Häufiges Missverständnis im Raum: „Haben wir das nicht gerade gebucht?" — **Nein.** Sauber abgrenzen:

| | **Umsatzsteuer** (Demo 3.2/3.2a) | **Ertragsteuern** (dieses Gap) |
|---|---|---|
| Art | Verkehrsteuer, **durchlaufender Posten** | **Ertragsteuer — belastet FDG selbst** |
| Bemessung | pro Umsatz/Rechnung, **monatlich** | auf den **Gewinn**, **jährlich** |
| Beispiele | Vor-/Ausgangssteuer, Zahllast | **GewSt, KSt**, §60(2)-Überleitung, Hinzurechnungen/Kürzungen |
| SAP-Standard | **voll abgedeckt** (RFUMSV00, F1597, F1612, DRC) | **kein Standardprozess** |

**O-Ton:** *„Was wir gerade gebucht haben — die USt-Zahllast — ist ein durchlaufender Posten, im Standard komplett abgedeckt. Ertragsteuern sind eine andere Kategorie: GewSt, KSt, die §60(2)-Überleitung Handels-/Steuerbilanz und die gewerbesteuerlichen Hinzurechnungen/Kürzungen. Dafür gibt es in der Public Cloud bewusst keinen Standardprozess — kein Steuerledger."*

#### Warum es ein Gap ist (der fachliche Kern)

- **Kein Steuer-Ledger im Public-Cloud-Standard:** Eine parallele **Steuerbilanz neben der HGB-Handelsbilanz** (Leading Ledger 0L) ist im Standard **nicht als eigenes Ledger** vorgesehen. Die **§60(2)-Überleitung** (Handels- → Steuerbilanz) läuft daher **nicht automatisiert** im System.
- **Keine GewSt-/KSt-Berechnungslogik:** Steuersatz-Anwendung, Zerlegung, Vorauszahlungen etc. sind **kein geführter Prozess**.
- **Keine geführten Hinzurechnungen/Kürzungen (§ 8 / § 9 GewStG):** müssen außerhalb des Systems ermittelt werden.

#### Was der Standard *ansatzweise* hergibt (Anknüpfungspunkt, keine Lösung)

1. **Konten existieren im YCOA** — Steueraufwand und Rückstellung können **manuell gebucht** werden. Der Kontenplan enthält bereits **spezifische** Ertragsteuer-Konten:

   *Aufwand (GuV):*
   | Konto | Bezeichnung | Verwendung |
   |---|---|---|
   | 75002000 | Aufw. Körperschaftsteuer | **KSt-Aufwand** |
   | 75002100 | Kapitalertragssteuer | KapESt |
   | 75002200 | Solizuschlag auf KSt | **SolZ auf KSt** |
   | 75008000 | Gewerbesteuer | **GewSt-Aufwand** |
   | 75003000 | Latente Steuern | latenter Steueraufwand/-ertrag |
   | 75004000 | So Ertragssteuern | übrige Ertragsteuern |

   *Rückstellungen / latente Steuern (Bilanz):*
   | Konto | Bezeichnung | Verwendung |
   |---|---|---|
   | 24032000 | Rückst. Gewerbest. | **GewSt-Rückstellung** |
   | 24033000 | Rückstg KSt | **KSt-Rückstellung** |
   | 24034000 | Rückstg KapErtSt | KapESt-Rückstellung |
   | 24037000 | Rückst. pass lat St | **passive latente Steuern** |
   | 21723000 | Man. Rückst. erw. ES | manuelle Rückst. erwartete Ertragsteuer |
   | 12606000 | Latente Steuerguthaben | aktive latente Steuern |
   | 21600000 | Abgr. latente Steuern | Abgrenzung latenter Steuern |

   > Der YCOA ist also für die **Ergebnisbuchung** (Aufwand + Rückstellung, getrennt nach GewSt/KSt/KapESt/latent) vollständig ausgestattet — was fehlt, ist nicht das Konto, sondern der **Herleitungs-/Berechnungsprozess**.

2. **Ledger-Konzept zeigen:** Leading Ledger **0L = HGB**; erklären, dass eine steuerliche Parallelrechnung im Standard **nicht als eigenes Ledger** existiert → die Überleitung erfolgt außerhalb.

**O-Ton:** *„Wir können den Steueraufwand und die -rückstellung im System manuell buchen — die Konten dafür sind da. Was das System nicht liefert, ist die Herleitung: die Überleitung zur Steuerbilanz und die Hinzurechnungen/Kürzungen. Die entstehen weiterhin außerhalb — heute vermutlich in Excel oder beim Steuerberater."*

#### Leitfragen an FDG (für die Gap-Bewertung)

- Wie wird die **Ertragsteuer heute ermittelt** — internes Excel, externes Tool, Steuerberater?
- Wird eine **§60(2)-Überleitung** erstellt, und wer verantwortet sie?
- Werden **latente Steuern** (HGB § 274) gebucht — und in welchem Detailgrad?
- Erwartung an das neue System: nur **Ergebnis buchen** (Aufwand/Rückstellung) oder **Herleitung** darin abbilden?

#### Mögliche Lösungsrichtungen (nur benennen — Design/Realize, nicht heute entscheiden)

- **(a) Standard + extern:** Herleitung extern (Excel/Steuerberater), nur **Ergebnisbuchung** im System. *(pragmatisch, geringster Aufwand)*
- **(b) Add-on/Partnerlösung** für Tax Reporting / latente Steuern über SAP BTP.
- **(c) Group-Reporting/Tax-Modul** prüfen (separater Track — Konsolidierung).
- **(d)–(f):** abgestufte Ziel-Architektur — siehe **4.1.2**.

**Festhalten:** *Ist-Prozess · gewünschter Ziel-Deckungsgrad · Lösungsrichtung · Verantwortliche(r) · nächster Schritt.* → verweist auf FDG-Zulieferung „Muster manuelle Ertragsteuerberechnung" (Abschnitt 5).

---

### 4.1.2 Lösungsarchitektur Ertragsteuern — abgestufte Optionen (Design-Diskussion)

> **Zweck:** die im Gespräch erarbeiteten Standard-nahen Wege festhalten. **Keine Entscheidung heute** — Weichenstellung für Design/Realize; einige Punkte sind **scoping-kritisch** (siehe Deadlines unten).

#### Die vier Bausteine der Steuerbilanz — wo sie im Zielbild entstehen

Die Ertragsteuer-Herleitung zerfällt in vier Teile, die **nicht** alle denselben Lösungsweg brauchen:

| Baustein | Empfohlener Weg im Zielbild | Standard? |
|---|---|---|
| **AfA-Differenzen** (HGB vs. steuerlich) — größter Differenztreiber | **Statistischer Bewertungsbereich** in der Anlagenbuchhaltung (z. B. Bereich 15) | ✅ **Standard** |
| **Latente Steuern** (temporäre Differenzen) | Basis aus dem stat. Bewertungsbereich + **manuelle Ergebnisbuchung** | ✅ überwiegend Standard |
| **Hinzurechnungen/Kürzungen (§ 8/§ 9 GewStG) + eigentliche GewSt-/KSt-Berechnung** | **BTP-App** als Ablösung der heutigen Excel | ⚠️ Eigenentwicklung |
| **Ablage / Steuerbilanz-Ausweis** (belegbasiert im System) | **Erweiterungsledger** (Delta über 0L) | ✅ Standard-Werkzeug |

#### (d) Erweiterungsledger — Chancen & Grenzen

- **Chance:** SAP nennt „Steuerzwecke" explizit als Anwendungsfall. Erbt 0L (HGB), speichert nur **Delta-Buchungen** → Reporting = HGB + Steuer-Deltas = **Steuerbilanz-Sicht**, belegbasiert (Art „Standardbuchungsbelege": nicht löschbar, nur stornierbar) → **prüfungssicherer als Excel**.
- **Grenze:** Es ist ein **Buchungs-/Reporting-Container, kein Bewertungswerkzeug** — es *rechnet nichts*. Laut SAP-Doku zudem: **nicht mit der Anlagenbuchhaltung integriert**, **keine Buchung auf OP-geführte Sachkonten / Kreditoren-/Debitorenabstimmkonten**, RLV/GJV/Währung werden geerbt (nicht änderbar).
- **Fazit:** löst die *Ablage/den Ausweis*, nicht die *Herleitung*.

#### (e) Steuerliche AfA über statistischen Bewertungsbereich (bevorzugt für den AfA-Teil)

- **Kernpunkt (Beleg: Ledger-Doku, Abschnitt Anlagenbuchhaltung):** *„Ein statistischer Bewertungsbereich (z. B. Bewertungsbereich 15) ist … zulässig."* → Die **Anlagenbuchhaltung rechnet die steuerliche AfA selbst** (eigene Nutzungsdauern, degressiv/linear, GWG) parallel zur HGB-AfA in Bereich 01.
- **Damit entfällt der teuerste BTP-Baustein:** die AfA-Logik muss **weder in Excel noch auf BTP** nachgebaut werden — der Standard liefert die book-↔-tax-Differenz.
- **Haken „statistisch":** rechnet & reported, **bucht keine eigenen G/L-Belege**. Für §60(2)-Überleitung, latente-Steuern-Basis und Steuerbilanz-Ausweis reichen die **Werte** i. d. R. aus. Sollen die AfA-Deltas auch *gebucht* erscheinen → Kombination mit dem **Erweiterungsledger (d)**.
- **Scoping-kritisch:** Der steuerliche Bewertungsbereich sollte **vor den ersten Anlagenbuchungen/der Migration** eingerichtet sein → gehört fachlich in den **Anlagen-Workshop (AA)**, hier nur als Gap-Verweis.

#### (f) BTP-App für Hinzurechnungen/Kürzungen + GewSt/KSt (Ablösung der heutigen Excel)

- **Ausgangslage:** Diese Berechnung liegt **heute schon als Excel bei DUS und wird von DUS gepflegt**. Eine BTP-Lösung ist daher **kein neuer Wartungsaufwand**, sondern **verlagert** die bestehende Pflege aus einer fragilen Excel in eine robuste, an S/4 angebundene Umgebung (belegbasiert, versioniert, mit Berechtigungen/Freigabe, Audit-Trail; AfA-Differenzen aus Bereich 15 fließen automatisch ein statt manueller Übertragung).
- **Architektur-Skizze:**
  ```
  S/4HANA (0L=HGB, stat. Bereich 15 = steuerl. AfA)
     │ ① Daten via CDS/OData-APIs (Salden, Anlagen, AfA-Deltas)
     ▼
  SAP BTP  ── ② Berechnungs-App (Hinzurechnungen/Kürzungen §8/§9,
     │           GewSt-/KSt-/SolZ-Rechnung, latente Steuern, Überleitungs-Doku)
     │ ③ Delta-/Ergebnisbuchung via Journal Entry API (Ziel-Ledger adressierbar)
     ▼
  Erweiterungsledger  → Steuerbilanz-Sicht, belegbasiert
  ```
- **Erfolgs­kriterium „user-friendly" (entscheidend!):** Alles, was sich durch **Gesetz oder Jahr** ändert, muss **vom Fachbereich selbst pflegbare Konfiguration** sein — **nicht** Code. Sonst tauscht man „fragiles Excel" gegen „IT-abhängige Blackbox".

  | Nutzer pflegt selbst (Config/Parameter) | Bleibt Code (Anwendungslogik) |
  |---|---|
  | GewSt-**Hebesatz** (Düsseldorf), Messzahl | Rechen-Framework / Ablauf |
  | Sätze/Schwellen **Hinzurechnungen § 8** | S/4-Anbindung (APIs) |
  | **Kürzungs**-Parameter § 9, Grundbesitz-Basis | Rückbuchung ins Erweiterungsledger |
  | Konten-Zuordnung Position ↔ Konto | Validierungen, Berechtigungen |
  | KSt-/SolZ-Sätze | |

- **Umsetzungsvarianten:** **SAP Build (Low-Code)** — näher am Excel-Gefühl, Fachbereich autonomer · **Pro-Code (CAP/Fiori)** — mächtiger, IT-abhängiger · **Hybrid (empfohlen)** — Framework als Code, **alle Steuerparameter in Pflegetabellen** + einfache Eingabemasken für manuelle Positionen.
- **Ehrliche Einordnung:** bewusstes **Eigenentwicklungs-Projekt** (kein Standard) mit klarem Nutzen (Excel-Ablösung). **Aufwand/Nutzen** prüfen: Build + Betrieb + BTP-Lizenz vs. jährlicher Prozess an einem Standort.

#### Zielbild in einem Satz

*„AfA-Differenzen im Standard über den statistischen Bewertungsbereich, latente Steuern als Ergebnisbuchung darauf, die Hinzurechnungen/Kürzungen und die GewSt-/KSt-Rechnung als BTP-App zur Ablösung der heutigen Excel (mit fachlich pflegbaren Parametern), und die Steuerbilanz-Sicht belegbasiert im Erweiterungsledger."*

#### Action Items aus dieser Diskussion

- ☐ **Heutige Steuer-Excel als Anforderungsbasis** liefern (Positionen, Formeln, Parameter) — *FDG Steuer* → Realize-Spec.
- ☐ **„User-friendly"-Definition:** Was muss der Fachbereich ohne IT ändern können? → entscheidet Low-Code vs. Pro-Code.
- ☐ **Scoping-Deadline Ledger:** Bedarf zusätzliches (nicht-führendes) Ledger? — **nach Scope-Abschluss nicht mehr hinzufügbar/entfernbar.** Erweiterungsledger dagegen später anlegbar.
- ☐ **Scoping-Deadline Bewertungsbereich:** steuerlicher Bewertungsbereich **vor Anlagen-Migration** einrichten → **Anlagen-Workshop (AA)** einsteuern.
- ☐ **Aufwand/Nutzen (TCO)** BTP-App vs. externe Berechnung bewerten.

---

### 4.1.1 Hintergrund: Ermittlungsprozess & Steuerledger (Backup-Wissen für Rückfragen)

> **Zweck:** Vertiefung für Rückfragen der FDG-Steuerabteilung — *warum* das System die Rechnung nicht abnimmt. Nicht Teil der Live-Demo.

#### (1) Wie Ertragsteuern ermittelt werden — der Prozess

Ertragsteuern bemessen sich am **Gewinn**, nicht am Umsatz. Der *steuerliche* Gewinn ≠ der *handelsrechtliche*. Der Weg dahin ist eine mehrstufige Nebenrechnung **außerhalb der laufenden Buchhaltung**:

```
   Handelsbilanzergebnis (HGB, Ledger 0L)               ← das liefert SAP
 ± Überleitung §60 Abs. 2 EStDV (Handels- → Steuerbilanz)
     z. B. andere AfA, Rückstellungsverbote, Drohverlust-
     rückstellung steuerlich nicht anerkannt …
 = Steuerbilanzgewinn
 ± außerbilanzielle Korrekturen (nicht abzugsf. BA, steuerfreie Erträge)
 = zu versteuerndes Einkommen (Basis KSt)
   KSt  = 15 %  × zvE
   SolZ = 5,5 % × KSt

 Gewerbesteuer separat:
   Steuerbilanzgewinn
 + Hinzurechnungen §8 GewStG (anteil. Zinsen; Miet-/Pacht-/Leasingaufwand)
 − Kürzungen §9 GewStG (1,2 % Einheitswert Grundbesitz, Gewinnanteile)
 = Gewerbeertrag
   × Messzahl 3,5 %  = Steuermessbetrag
   × Hebesatz (Düsseldorf ≈ 440 %) = Gewerbesteuer
```

**DUS-Relevanz:** Bei einem immobilien-/infrastrukturlastigen Betrieb sind v. a. die **GewSt-Hinzurechnungen** (§ 8 Nr. 1 GewStG — Miet-/Pacht-/Leasingaufwand, anteilige Zinsen) potenziell erheblich. Dazu **latente Steuern** (§ 274 HGB) auf jede temporäre HGB-/Steuerbilanz-Differenz.

→ Diese Rechnung ist eine **Nebenrechnung** (heute Excel/Steuerberater). Nur das *Ergebnis* wird gebucht.

#### (2) Wie die manuellen Buchungen aussehen (YCOA)

Alle über *Post General Journal Entries* (F0718) / Sachkontenbuchung:

**(a) Unterjährige Vorauszahlungen ans Finanzamt**
```
Soll  75008000  Gewerbesteuer                 X
Soll  75002000  Aufw. Körperschaftsteuer      Y
Soll  75002200  Solizuschlag auf KSt          Z
   Haben  11xxxxxx  Bank
```

**(b) Jahresabschluss — Rückstellung für erwartete Steuer** (Ergebnis der Nebenrechnung ./. geleistete Vorauszahlungen)
```
Soll  75008000  Gewerbesteuer
   Haben  24032000  Rückst. Gewerbesteuer
Soll  75002000  Aufw. Körperschaftsteuer
   Haben  24033000  Rückstg KSt
```

**(c) Latente Steuern** (aus temporären Differenzen)
```
Soll  75003000  Latente Steuern (Aufwand)
   Haben  24037000  Rückst. passive latente Steuern
— oder aktivisch —
Soll  12606000  Latente Steuerguthaben
   Haben  75003000  Latente Steuern (Ertrag)
```

**Kern:** reine **Ergebnis-Erfassungen**. Das System kennt weder Hebesatz noch Hinzurechnung noch Überleitungsposition — es bucht eine **fertige Zahl aus Excel**. Buchhalterisch trivial; die Intelligenz steckt in der vorgelagerten Rechnung.

#### (3) Was ein Steuerledger tun würde

Ein **Steuerledger** (steuerliches Parallelledger) ist ein *zweites vollständiges Hauptbuch neben Ledger 0L* mit **steuerlichem Wertansatz** je Buchung:
- **Automatische Parallelbewertung** (z. B. Anlage: 0L nach HGB-AfA, Steuerledger nach steuerlicher AfA — gleichzeitig gebucht).
- **Steuerbilanz aus dem System** statt aus Nebenrechnung.
- **§60(2)-Überleitung = Differenz 0L ↔ Steuerledger**, belegbasiert, per Knopfdruck, prüfungssicher.

Im **On-Premise / Private Cloud** ist ein solches Ledger (bzw. Special Ledger) einrichtbar → Überleitung & latente Steuern weitgehend systemgestützt.

#### (4) Worin das Problem liegt

- **Problem A — Public Cloud lässt kein Steuerledger zu.** Mehrere Ledger für **Rechnungslegung** (0L = HGB, ggf. IFRS) sind möglich, aber **kein frei konfigurierbares steuerliches Ledger** mit eigener Bewertungslogik (AfA, Hinzurechnungen, Hebesatz). → Automatisierung aus (3) steht **nicht** zur Verfügung.
- **Problem B — der intelligente Teil bleibt manuell.** Überleitung §60(2), Hinzurechnungen/Kürzungen, latente Steuern bleiben **externe Nebenrechnung**; das System nimmt nur das **fertige Ergebnis** auf.

**Konsequenzen (= Gap-Argumentation):**
1. Kein Automatismus — die Berechnung wird nicht einfacher als heute.
2. Medienbruch bleibt (Excel/Tool → manuelle Buchung), nicht belegbasiert prüfungssicher.
3. §60(2)-Überleitung weiterhin außerhalb.
4. Latente Steuern manuell ermittelt und als eine Zahl gebucht.

**Was NICHT das Problem ist:** die **Buchung** selbst. Der YCOA hat alle Konten (75002000/75002200/75008000, 24032000/24033000/24037000 …). **Der Gap ist die *Herleitung*, nicht die *Erfassung*.**

**O-Ton (Kernsatz):** *„Die Umsatzsteuer rechnet und meldet SAP für uns — die Ertragsteuern nicht. Für GewSt/KSt gibt es in der Public Cloud kein Steuerledger, das die Steuerbilanz automatisch ableiten würde; die Berechnung inkl. §60(2)-Überleitung und Hinzurechnungen bleibt eine externe Nebenrechnung. Das System kann das Ergebnis buchen — die Konten sind da — aber es nimmt uns die Rechnung nicht ab."*

---

## 5. Zusammenfassung, Action Items & nächste Schritte (02:45 – 03:00 | 15 Min.)

- **Kurz-Recap:** Closing (2.1–2.6) und Tax (3.1–3.6) im Standard demonstriert; identifizierte Gaps dokumentiert.
- **Action Items festhalten** (Verantwortliche + Termin), u. a.:

### Vorzubereiten / bereitzustellen durch FDG
- Aktuelles **ZM-Format** + Beispiel **USt-Voranmeldung/Elster-Prozess** → Standard-Abgleich.
- Übersicht der heute genutzten **CSV-Buchungsstrukturen** (Abgrenzung, Dauerbuchung) → Abgleich Standard-Upload-Vorlage.
- Liste der relevanten **Steuerkennzeichen** (Vorsteuer, Ausgangssteuer, Einfuhr-USt) → Verifizierung im Standard.
- Muster der **manuellen Ertragsteuerberechnung** (nur Gap-Input für Diskussion, nicht Demo).

- **Nächste Schritte:** offene/nicht freigeschaltete Apps in Folgetermin reproduzieren; Gaps in Design/Realize-Phase bewerten.

---

## Anhang A — App-Schnellreferenz (für den Präsentator)

| # | App (DE / EN) | Fiori-ID / Tcode |
|---|---|---|
| 2.1 | Buchungsperioden verwalten / *Manage Posting Periods* | F2293 |
| 2.1 | Buchungsperiodenvarianten verwalten / *Manage Posting Period Variants* | F2581 |
| 2.2 | Dauerbuchungsbelege verwalten / *Manage Recurring Journal Entries* | F1598 |
| 2.3 | Bestellabgrenzungen prüfen (Kostenrechner) / *Review PO Accruals* | F3552 |
| 2.3 | Bestellabgrenzungen anzeigen / *Display PO Accruals* | F3928 |
| 2.3 | Schedule Accruals Jobs | F3778 |
| 2.4 | Forderungen/Verbindlichkeiten umgliedern / *Regroup Receivables/Payables* | FAGLF101 |
| 2.4 | Wertberichtigung IFRS 9 / ECL | F107 |
| 2.6 | Bilanz/GuV / *Balance Sheet / Income Statement* | F0708 |
| 2.6 | Bilanz/GuV mehrdimensional / *…Multidimensional* | W0161 |
| 2.6 | Summen-/Saldenliste / *Trial Balance* | F0996 |
| 2.6 | Schedule General Ledger Jobs (Saldovortrag) | F1927 |
| 3.1 | Steuerinformationen je Land/Region / *Display Tax Information per Country-Region* | S_ALR_87012365 |
| 3.2 | USt-Voranmeldung erstellen / *Advance Return for Tax on Sales/Purchases* | S_ALR_87012357 |
| 3.2 | Steuerverbindlichkeiten buchen / *Post Tax Payables* | F1597 |
| 3.2 | Schedule Tax Jobs | F3690 |
| 3.3/3.4 | Run Statutory Reports (ZM, VAT, Audit) | F1515 |
| 3.4 | Manage Electronic Documents / eDocument Cockpit | EDOC_COCKPIT |
| 3.5 | Tax Reconciliation Account Balance | F2095 |
| 3.5 | Tax Declaration Reconciliation | F2096 |

> **Hinweis zur ID-Verifizierung:** Fiori-IDs geprüft gegen SAP Help Portal (help.sap.com), S/4HANA Cloud Public Edition Release 2602, korroboriert über die Fiori Apps Reference Library. Zeilen mit „(confirm ID)" in der Test-Overview (Z4/Z5A, Auditor Direct Access) vor formalem Test in der Fiori Apps Reference Library final bestätigen.

