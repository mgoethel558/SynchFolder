# Strategiepapier: Agentic Finance & Treasury
## Viessmann Generations Group (VGG) auf SAP S/4HANA Cloud Public Edition

| | |
|---|---|
| **Adressat** | CFO / Head of Finance VGG; Deloitte Delivery-Team |
| **Autor** | Deloitte – Senior Solution Architect S/4HANA Cloud Public Edition (Finance/Treasury) |
| **Stand** | 26.08.2026 (v3 – Kundenantworten, priorisierte Use Cases, Painpoint Authorisierung, Ausblick) |
| **Status** | Arbeitsentwurf zur Abstimmung |
| **Zweck** | Strategie für den agentischen Betrieb und die agentische Konfiguration von Finance & Treasury bei VGG |

> **Änderungsstand v2 (26.08.2026):** Eingearbeitet: Kundenantworten auf die offenen Fragen, vier neue Primärquellen – Config-Export inkl. Buchungskreisliste (`current_config/`), definitive SAP-AI-Feature-/-Agenten-Liste des Kunden (`sap_ai/AI Features Data.csv`), IST-Onboarding-Runbook (`entity_onboaring_prozess/`) – sowie die **vom Kunden selbst priorisierten Use Cases** (neuer Abschnitt 5.5, D-1…D-6). Zentrale Korrekturen ggü. v1: **101 produktive Buchungskreise** (statt „zweistellig, geschätzt"), **Team ~7 intern + externer Steuerberater** (statt 13–16), **DEV-Scope = Produktiv-Scope** (OF-1 geklärt), **Treasury-Gaps entfallen** (Drittlösung + E05 im Einsatz, OF-2/OF-7 geklärt), **SAP-Agenten-Landkarte auf die kundenseitig belegte Liste umgestellt**. Die zwei GA-fähigen Kundenprioritäten (D-2 Bilanzanalyse, D-5 Self-Service-Copilot) sind die neuen Top-Quick-Wins. **v3 ergänzt:** den Painpoint **Authorisierung** (Rollen-Erweiterung bei neuen BuKr → mit Priorität ins Entity Onboarding, Agent B-8) sowie ein **Ausblick-Kapitel (Kap. 10)** mit Umsetzungsweg, Horizonten und der Rolle der SAP Business AI Platform.

---

### Lesehinweis zur Quellenkennzeichnung

Dieses Papier trennt strikt zwischen **Fakt**, **Annahme** und **Empfehlung**:

- **[FAKT]** – belegt durch eine benannte Quelle (PDF-Pfad + Seite, Dateiname im Kundenordner, oder URL).
- **[ANNAHME]** – plausible Arbeitshypothese, im Kundenworkshop zu bestätigen (siehe `offene-fragen.md`).
- **[EMPFEHLUNG]** – Handlungsvorschlag des Autors.
- **[ZU PRÜFEN]** – Aussage, die nicht aus einer belastbaren Live-Quelle verifiziert werden konnte.

Quellenkürzel: **[Scope S.n]** = Scope-Item-PDF `Agents_AutonomusEnterprise/current_scope/ERP VGG IMP DEV - CUST scope (1).pdf`, Seite n. **[Datei: …]** = Datei im Kundenordner `…/Projekt/Viessmann/`. **[Zielbild]** = `…/Projekt/CAMP4/Zielbild_Autonomous_Enterprise.md` (Deloitte-internes Zielbild „Autonomous Enterprise Plus", Stand 21.07.2026). **[Web: …]** = recherchierte URL (Stand 25.08.2026). Vollständige Quellenliste im Anhang.

---

## 0. Management Summary

**Ausgangslage.** VGG betreibt SAP S/4HANA Cloud Public Edition als familiengeführte Investment- und Beteiligungsholding [FAKT, Web: viessmann.group]. Das produktive System umfasst **101 Buchungskreise** – 88 in Deutschland, 13 im Ausland (4 CA, 3 US, 2 NL, 2 LU, 1 GB, 1 FI) [FAKT, [Datei: current_config/V_001_CLD.xlsx]]. Accounting und Treasury werden von einem **sehr kleinen Team** betrieben: 3 Accounting, 2 Controlling, 2 Treasury (7 intern), ergänzt durch einen externen Steuerberater, der ebenfalls im System bucht und bilanziert – zusammen 4–8 Personen [FAKT, Kundenauskunft OF-3]. **Das Verhältnis ist der Kern der Geschichte: ~7 Personen betreiben Finance/Treasury für 101 Legal Entities.** Kernmerkmal des Geschäfts: regelmäßige Zukäufe von Vorratsgesellschaften und Assets, die schnell zu buchungsfähigen Buchungskreisen werden müssen (die vielen „Vis n Investment"-, „GForce"- und „USA Residential"-Gesellschaften belegen das [FAKT, [Datei: current_config/V_001_CLD.xlsx]]). Genau hier – Skalierung der Legal-Entity-Zahl ohne Headcount-Wachstum – liegt der größte Hebel.

**Drei Kernbotschaften.**

1. **Der Engpass ist nicht die Buchung, sondern die Wiederholung.** Das kleine Team bewältigt viele Entitäten mit weitgehend identischen, regelbasierten Tätigkeiten (Kontoauszug, Zahllauf, Intercompany-Abstimmung, Abschluss-Tasks, Stammdaten). Das ist das ideale Feld für agentische Automatisierung mit menschlicher Freigabe.

2. **Die „Buchungskreis-Fabrik" ist der strategische Differenzierer.** Kein SAP-Standard-Agent legt heute selbstständig einen Buchungskreis an. Genau diese agentische Konfiguration (Scoping → Org-Struktur → SSCUI) ist der Kern von Deloittes „Autonomous Enterprise Plus" / CAMP4 [FAKT, Zielbild]. Für einen Serien-Entity-Käufer wie VGG ist das kein Nice-to-have, sondern der Hebel mit der höchsten Skalenwirkung.

3. **SAP liefert den agentischen Betrieb – aber der Finance-Kern ist noch dünn.** Die kundenseitig belegte Liste der SAP-AI-Features für Public Edition [FAKT, [Datei: sap_ai/AI Features Data.csv]] zeigt: viele **GA-Joule-Assistenzfunktionen** (Enterprise Search, Easy Fill, Fixed-Asset-Stammdaten, Allocation-Ergebnisse, Payment-Advice-Verarbeitung via Document AI), aber **echte „AI Agents" bislang v. a. im Billing-Umfeld (Early Adopter Care)** und einzelne **Beta-Features** wie *Payment Exception Analysis* und *Task Automation*. Für das VGG-Kernproblem (Kontoauszug/Cash Application, IC, Close über 101 Entitäten) gibt es **noch keinen fertigen SAP-Standard-Agenten** – der Eigenbau (Kategorie B) und die Deloitte-Konfigurations-Capability sind daher der Hauptpfad. Das AI-Units-/Lizenzmodell wird kundenseitig aktuell mit SAP verhandelt [FAKT, Kundenauskunft OF-6].

**Vom Kunden selbst priorisiert (höchste Umsetzungswahrscheinlichkeit).** VGG hat sechs konkrete Use Cases benannt (Kap. 5.5). Zwei davon sind **sofort mit GA-Features** umsetzbar: **Bilanz-/Abweichungsanalyse** (Analytical Business Insights J88) und **Self-Service-Auswertung per natürlicher Frage** (Joule J74 + Enterprise Search J225). Weitere: Central Invoice Management mit automatischer BuKr-Zuordnung, Report ausstehende Eingangsrechnungen, sachliche Kontierungsprüfung, Anlagevermögen/CO-Verrechnung (mit bereits unterschriebenem SAP-Co-Innovation-Agreement). Weil Bedarf und Sponsorship hier belegt sind, bilden diese Use Cases den Kern der 0–6-Monats-Roadmap.

**Top-Empfehlungen (Kurzform, Details in Kap. 5–7).**

- **Quick Wins (0–3 Monate):** die zwei GA-fähigen Kunden-Use-Cases D-2 (Bilanzanalyse) und D-5 (Self-Service-Copilot) sofort starten; parallel Advanced Bank Statement Automation (4X8) und Advanced Cash Operations (J78) ausreizen; Situation Handling (31N) und Responsibility Management (1NJ) als Grundlage für Exception-basierte Agentenlogik konfigurieren – alle im Scope [FAKT, Scope S.1–2].
- **Painpoint Authorisierung mit Priorität:** Die vom Kunden benannte Rollen-Erweiterung bei neuen Buchungskreisen wird als **Pflichtschritt in das Entity Onboarding** gezogen (Agent B-8), gekoppelt an das laufende Berechtigungs-Vereinfachungsprojekt.
- **Strategisch (3–24 Monate):** Buchungskreis-Onboarding-Agent auf Basis CAMP4/ConfigPilot als VGG-spezifisches Asset (inkl. Rollen); Treasury-Integrations-Copilot über alle Entitäten (SAP + Drittlösung + E05). Grundlage für alles Agentische ist die **SAP Business AI Platform** (kundenseitig in Vorbereitung) – siehe Ausblick Kap. 10.
- **Voraussetzung überall:** Datenqualität (der BP-Löschjob-Vorfall und der FX-Valuation-Bug zeigen die Fragilität [FAKT, [Datei: VGG_DataInconsistency_BPDeletionJob.docx], [Datei: FX_Valuation_Issue_2026.docx]]) und Governance (4-Augen-Prinzip, Clean Core).

**Nutzen (Bandbreite, [ANNAHME] bis Volumina validiert).** Entlastung des ~7-köpfigen Teams um geschätzt 20–40 % der repetitiven Kapazität – bei 101 Entitäten wirkt jeder automatisierte Prozess als 101-facher Multiplikator; Verkürzung der Durchlaufzeit „Deal-Close → buchungsfähiger Buchungskreis" gegenüber dem heutigen manuellen Runbook (dokumentiert mit ~40 Einzelschritten über CBC und SSCUIs [FAKT, [Datei: entity_onboaring_prozess/…Set up new Company Code.md]]) auf wenige Tage; deutliche Reduktion manueller Fehlerquellen bei Kontoauszug, Zahllauf und Intercompany.

> **Diese Management Summary trägt allein.** Die folgenden Kapitel belegen und differenzieren die Aussagen.

---

## 1. Unternehmen und Geschäftsmodell → Implikationen für SAP

### 1.1 Geschäftsmodell (Faktenlage)

[FAKT, Web: viessmann.group, Abruf 25.08.2026] VGG ist eine familienkontrollierte Investment- und Beteiligungsholding mit Sitz in Battenberg (Eder). Das Modell ist über sechs Investment-Strategien und thematische Investitionsfelder organisiert:

- **Majority Investments** – Plattformen: GRITEC (Grid Infrastructure), isoplus (District Heating/Cooling – Pipes), aqotec/ETX/Pewo (Stations & Controls), KPS Global (Clean & Cold US), Viessmann Clean & Cold Solutions/Vitec (Clean & Cold EU).
- **Minority Investments** – Carrier, Encavis, AMCS, Schülke, Landefeld, Genaq, PharOS.
- **Generational Investments** – Real Estate, Forestry, Agriculture, FGTC Investment.
- **Early-Stage / Ecosystem** – Vito Ventures, Vision Mittelstand Partners, Urban Partners, Maschinenraum.
- **Philanthropie** – Viessmann Foundation gGmbH u. a.

Max Viessmann sitzt im Board of Directors von Carrier [FAKT, Web: viessmann.group].

**Abweichung zur Ausgangs-Zusammenfassung [ZU PRÜFEN]:** Die Live-Seite positioniert VGG primär über die Investment-Strategien und -Felder, nicht ausdrücklich als „Investment-Holding"; das Datum der Carrier-Zusammenführung (2023/24) ist auf der Seite nicht mehr prominent datiert. Carrier wird heute als *Minority Investment* geführt. Für das Strategiepapier ist der Kern unverändert gültig: **wenige Personen, viele Rechtsträger, kapitalmarkt-/beteiligungsgetriebenes Geschäft.**

### 1.2 Operating Model → was das ERP tatsächlich leisten muss

[ANNAHME, gestützt durch Geschäftsmodell + Dateninventar] Das operative Geschäft (Produktion, Vertrieb, Service) liegt in den Portfoliounternehmen mit eigenen Systemen. Auf VGG-Holding-Ebene dominieren:

| Funktionsbereich | Warum zentral für VGG | Beleg / Indikator |
|---|---|---|
| **Beteiligungsverwaltung & -buchung** | Kern des Geschäfts; jede Beteiligung ist ein Bilanzobjekt; 101 Legal Entities [FAKT, current_config/V_001_CLD.xlsx] | Portfolio-Struktur [Web]; Group Reporting im Scope (1SG, 3AF) [Scope S.2] |
| **Cash- & Liquiditätssteuerung, Treasury** | Kapitalallokation über viele Entitäten, Cash Pooling, FX | Treasury-Workshops, Cash-Pool-Testfälle [Datei: Treasury - 2nd_workshop.pptx], [Datei: E05_TestPlan.xlsx] |
| **Intercompany (Finanzierung & Abstimmung)** | Konzerninterne Darlehen, Verrechnung, Reconciliation | 1GP, 40Y im Scope [Scope S.2]; [Datei: ICMR.xlsx] |
| **Abschluss & Group Reporting (IFRS)** | Konsolidierung über alle Legal Entities | Group Ledger IFRS (1GA) [Scope S.1], 1SG/3AF [Scope S.2] |
| **Anlage neuer Rechtsträger** | Serien-Zukauf von Vorratsgesellschaften/SPVs | VESTA-Implementierungsordner, Copy-CoA-Doku [Datei: Documentation/CopyCoA2newCompanyCode.docx] |
| **Steuern & Compliance** | Mehrländer-Umfeld (7 Länder) | VAT (77N), Document & Reporting Compliance (5XU), External Tax Audit (2OO) [Scope S.2–3] |

**Zentrale Implikation:** Das VGG-ERP ist kein produktionsnahes ERP, sondern eine **Finanz- und Beteiligungssteuerungs-Plattform mit hoher Legal-Entity-Kardinalität** (101 Buchungskreise auf ~7 Personen). Der Skalierungsdruck entsteht nicht durch Transaktionsvolumen pro Entität, sondern durch die **Zahl der Entitäten** und die **Wiederholung gleichartiger Finanzprozesse** über diese Entitäten. Die Namensmuster in der Buchungskreisliste (u. a. „Vis 1–13 Investment GmbH & Co KG", je mit zugehöriger „Invst Vwltng GmbH" als Komplementär, sowie „GForce"- und „USA Residential Invest I–V"-Serien) sind der direkte Fingerabdruck des Serien-Entity-Modells [FAKT, current_config/V_001_CLD.xlsx].

### 1.3 Wo Skalierung ohne Headcount gelingen muss

[EMPFEHLUNG] Drei Skalierungsachsen, die das Papier weiter verfolgt:

1. **Entity-Onboarding** – von Deal-Close zu buchungsfähigem Buchungskreis (Kap. 4).
2. **Wiederkehrende Finanzprozesse** – Kontoauszug, Zahllauf, IC-Abstimmung, Abschluss (Kap. 3, 5).
3. **Konzernsicht** – Liquidität, FX und Reporting über alle Entitäten hinweg (Kap. 5, Kategorie C).

Die Ländervielfalt (Canada, Finland, Germany, Luxembourg, Netherlands, United Kingdom, USA) [FAKT, Scope S.1] erhöht die Komplexität jeder dieser Achsen (Ländervarianten, Steuer, Bankanbindung) und macht Standardisierung über Templates umso wertvoller.

---

## 2. IST-Bild: Scope-Item-Analyse und Daten-Inventar

### 2.1 Grundlage und Vorbehalt

[FAKT, Scope S.1] Die Scope-Liste stammt aus dem Workspace **„ERP VGG IMP DEV - CUST"** (Viessmann Development System, Tenant: Customizing, Type: Implementation, SAP Basis contact: Julien Cisse/Deloitte), Stand 25.08.2026. **Vorbehalt geklärt [FAKT, Kundenauskunft OF-1]:** Der DEV-/Customizing-Scope **entspricht dem produktiven Scope** – die folgende Analyse gilt damit unmittelbar für die Produktion.

### 2.2 Scope-Cluster nach Line of Business

[FAKT, Scope S.1–4] Die aktivierten Scope-Items, geclustert. Vollständige ID-Liste im Anhang A.

**Finance – sehr breit ausgeprägt (Reifegrad hoch).** 40+ Finance-Scope-Items, u. a.:

- **Hauptbuch / Abschluss:** Accounting and Financial Close (J58), Group Ledger IFRS (1GA), Advanced Financial Closing Integration (4HG), General Ledger Allocation Cycle (1GI), Universal Allocation (2QL), Organizational Flexibility in Financial Accounting (4PG).
- **Kreditoren / Debitoren:** Accounts Payable (J60), Accounts Receivable (J59), Basic Credit Management (BD6), Direct Debit (19M), Automated Invoice Settlement (2LH).
- **Bank / Cash / Payments:** **Advanced Bank Statement Automation (4X8)**, **Advanced Cash Operations (J78)**, Basic Cash Operations (BFB), Basic Bank Account Management (BFA), Basic Payment Management (7MJ), Bank Integration with File Interface (1EG), Cash Journal (1GO).
- **Treasury-nah:** Automatic Market Rates Management (1S4).
- **Anlagen:** Asset Accounting (J62), Asset Accounting – Group Ledger IFRS (1GB), Asset Under Construction (BFH/1GF).
- **Intercompany:** Intercompany Financial Posting (1GP), Intercompany Reconciliation Process (40Y).
- **Group Reporting / Konsolidierung:** Group Reporting – Financial Consolidation (1SG), Group Account Preparation for Financial Consolidation (3AF).
- **Steuern / Compliance:** VAT Tax Calculation and Reporting (77N), Document and Reporting Compliance (5XU), External Tax Audit (2OO), Compliance Formats – Support Preparation (1J2).
- **Planung / Analytik:** Financial Planning and Analysis (2FM), Financial Plan Data Upload (1HB), diverse Fiori Analytical Apps (2JB, BGC, 2QY).

**Procurement – mittel ausgeprägt (Reifegrad mittel).** Requisitioning (18J), Purchase Contract (BMD), Procurement of Direct Materials (J45), Procurement of Services (22Z), Consumable Purchasing (BNX), Automated Invoice Settlement (2LH), Invoice Processing with SAP Ariba Central Invoice Management (4N6), Real-Time Reporting for Procurement (1JI).

**Sales – breiter als die Ausgangshypothese erwarten ließ (Reifegrad mittel).** 17 Sales-Scope-Items [Scope S.3–4]: Sell from Stock (BD9), Sales Quotation (BDG), Credit/Debit Memo (1EZ/1F1), diverse Returns- und Korrekturprozesse, Sale of Services (2EQ), Omnichannel Convergent Billing (1MC), Fiori Analytical Apps for Sales (1BS).

**Supply Chain / Asset Mgmt / weitere.** Core Inventory Management (BMC), Physical Inventory (BML), Available-to-Promise (2LN); Proactive/Reactive Maintenance (4HI/4HH); Output Management (1LQ); Data Migration from Staging (2Q2); Data Protection & Privacy (5LE).

**Übergreifend / für Agenten fundamental:** **Responsibility Management (1NJ)**, **Situation Handling (31N)** [Scope S.1] – beide sind die native SAP-Grundlage für ausnahme- und rollenbasierte (agentische) Prozesssteuerung.

### 2.3 Reifegradbild je LoB

| LoB | Scope-Breite | Reifegrad [ANNAHME] | Bemerkung |
|---|---|---|---|
| Finance – GL/Close | sehr breit | hoch | inkl. IFRS-Parallelledger, Advanced Closing |
| Finance – Bank/Cash/Payments | breit | hoch, aber fragil | 4X8/J78 aktiv; operativer Schmerz bei Bankauszug [Datei: Ticket_UploadBankstatement.docx] |
| Finance – Treasury | schmal | mittel | nur 1S4 (Market Rates); kein Advanced Payment Mgmt / dediziertes TRM im Scope sichtbar → Lücke (2.4) |
| Finance – Intercompany | vorhanden | mittel | 1GP + 40Y; Non-SAP-Gesellschaften via Excel-Upload [Datei: ICMR.xlsx] |
| Finance – Group Reporting | vorhanden | mittel–hoch | 1SG + 3AF; Konsolidierungstool IDL erwähnt [ANNAHME] |
| Procurement | mittel | mittel | Ariba CIM (4N6) integriert |
| Sales | mittel-breit | mittel | breiter als erwartet – Hypothese teilweise widerlegt (2.5) |
| Asset/Supply Chain | schmal | niedrig–mittel | primär für einzelne operative/Real-Estate-Entitäten [ANNAHME] |

### 2.4 Lücken: bewusst geschlossen durch Kundenentscheidung

**Aktualisiert [FAKT, Kundenauskunft OF-4/OF-7]:** Die in v1 vermuteten Treasury-/Payment-Lücken sind **bewusst keine Lücken**. VGG setzt für diesen Funktionsbereich **Drittsoftware** ein; **Treasury and Risk Management (TRM), In-House Cash, Advanced Payment Management und Multibank Connectivity werden im SAP-System ausdrücklich nicht benötigt.**

Zusätzlich existiert eine **eigenentwickelte Lösung „E05" für Cash Pooling**, die die **Verzinsung und Abrechnung von Intercompany-Darlehen** ermöglicht [FAKT, Kundenauskunft OF-7; konsistent mit [Datei: E05_TestPlan.xlsx], [Datei: Treasury - 2nd_workshop.pptx]]. Diese Lösung deckt die Treasury-Intercompany-Prozesse ab, die sonst über SAP-TRM liefen.

**Konsequenz für die Agenten-Strategie:**
- Treasury-Agenten müssen die **Drittlösung** bzw. **E05** als Datenquelle/Schnittstelle berücksichtigen, nicht native SAP-TRM-Objekte.
- Der Treasury-/Liquiditäts-Copilot (C-2) wird damit zu einem **Integrations-Copilot** über SAP + Drittlösung + E05, kein reiner SAP-On-Board-Agent (siehe Kap. 5, aktualisierter Steckbrief C-2).
- Ein Advanced-Payment-Management-Agent ist damit **nicht** Teil der Roadmap.

### 2.5 Prüfung der Ausgangshypothese „Finance überall, Procurement teilweise, Sales kaum"

[FAKT, Scope S.1–4] **Teilweise bestätigt, teilweise widerlegt** auf Scope-Ebene:

- „Finance überall": **plausibel** – Finance ist mit Abstand die breiteste LoB.
- „Procurement teilweise": **bestätigt** – solider, aber selektiver Procurement-Scope.
- „Sales kaum": **auf Scope-Ebene widerlegt** – 17 Sales-Scope-Items sind aktiviert.

**Wichtige Differenzierung [ANNAHME]:** Der breite Sales-/SCM-/Asset-Scope im *Customizing*-System spiegelt vermutlich einzelne operative bzw. Real-Estate-Entitäten oder Template-Vollausbau wider, nicht den flächendeckenden Produktiv-Einsatz. Die Hypothese ist auf **Buchungskreis-Ebene** (welcher CC nutzt welche LoB produktiv) neu zu prüfen – das ist genau die Template-Frage aus Kap. 4 (offene Frage OF-3).

### 2.6 Daten-Inventar (Auszug; vollständig in Anhang B)

[FAKT] Grundlage: Sichtung des Kundenordners `…/Projekt/Viessmann/`. Die folgenden Kernbefunde sind für die Agenten-Strategie relevant. **Datenqualitäts-Hinweis:** Zahlen zu Buchungskreisen und Headcount stammen aus Migrations-/Mapping-/Rollendateien und sind **Indikatoren, keine Stammdatenwahrheit** – im Workshop zu bestätigen.

| Thema | Befund | Quelle | Kennzeichnung |
|---|---|---|---|
| **Buchungskreise** | **101 produktive Company Codes**: 88 DE, 4 CA, 3 US, 2 NL, 2 LU, 1 GB, 1 FI. Serien-Muster „Vis n Investment"/„Invst Vwltng", „GForce", „USA Residential Invest I–V" | [Datei: current_config/V_001_CLD.xlsx] | **[FAKT]** – exakte Zahl bestätigt |
| **Kontenplan** | Umfang Größenordnung mehrere Tausend Konten; mehrere CoA-Varianten (Group-/Legacy-/Standard) in Mappings sichtbar | [Datei: GL_Accounts/G_L_AccountMapping.xlsx] | [ANNAHME]: hohe Kontenzahl → Harmonisierung relevant; genaue Zahl offen |
| **Bankkonten** | Strukturierte Bankverbindungen bei mehreren Instituten (u. a. Goldman Sachs DE/CH, J.P. Morgan, St. Galler KB), mehrere Währungen | [Datei: GL_Accounts/Treasury*.xlsx], [Datei: BP_Masterdata/BankMapping_V1.xlsx] | [ANNAHME] |
| **Intercompany** | ICMR implementiert; Non-SAP-Gesellschaften liefern per Excel-Upload zum 2. Arbeitstag | [Datei: ICMR.xlsx] | [FAKT für Dateiexistenz; Prozess ANNAHME] |
| **Treasury / Cash Pool** | Cash-Pool-Prozesse mit Interest Accrual, Monthly Accrual/Reversal, Annual Settlement; 7 Testfälle | [Datei: Treasury - 2nd_workshop.pptx], [Datei: E05_TestPlan.xlsx] | [FAKT für Dokumentexistenz] |
| **Headcount Finance/Treasury** | **3 Accounting + 2 Controlling + 2 Treasury = 7 intern**, plus externer Steuerberater (bucht/bilanziert im System); zusammen 4–8 Personen | Kundenauskunft OF-3 | **[FAKT]** – korrigiert v1-Schätzung (13–16) deutlich nach unten |
| **Buchungskreis-Anlage (IST)** | **Vollständiges Runbook** „Set up new Company Code" (v.01/16.04.24) mit ~40 Einzelschritten über CBC + benannte SSCUIs; deckt CBC-Org, GL/Accounts, Controlling, Procurement, Sales, Forms, Transport ab | [Datei: entity_onboaring_prozess/VGG_SAP_XX_Set up new Company Code.md] | **[FAKT]** – detaillierte Basis für Kap. 4 |

### 2.7 Bekannte Schmerzpunkte (Tickets/Issues) – als Datenqualitäts- und Agenten-Signal

[FAKT für Dokumentexistenz; Inhalt teils ANNAHME] Diese Vorfälle prägen die Governance-Anforderungen an jede Automatisierung:

| Vorfall | Kern | Quelle | Relevanz für Agenten |
|---|---|---|---|
| **BP-Löschjob / Dateninkonsistenz** | BP-Deletion-Job löschte offenbar mehr als vorgesehen; Folge: Inkonsistenzen bei Journal-Entry-Positionen; SAP-Case hoher Priorität | [Datei: VGG_DataInconsistency_BPDeletionJob.docx] | Zeigt: automatisierte Massenaktionen brauchen strikte Guardrails & Dry-Run |
| **FX-Valuation-Issue 2026** | Advanced FX Valuation offenbar unerwartet aktiviert, blockiert Standard-Valuierung | [Datei: FX_Valuation_Issue_2026.docx] | Zeigt: Config-Änderungen mit Seiteneffekten → CAMP4/Change-Governance |
| **Bankauszug-Upload** | Lange Laufzeit / blockierende Fehler beim Bank-Statement-Upload; Monatsend-Engpass | [Datei: Ticket_UploadBankstatement.docx] | Direkter Kandidat für Bank-Statement-/Cash-Application-Agent |
| **AA Account Determination** | Anlagenkonten mit abweichender Methode | [Datei: AA Acc Det Issue Ticket.docx] | Zeigt: Stammdaten-/Config-Konsistenz kritisch |
| **Overconsumption** | Memory-/Verbrauchsspitzen nach Release-Upgrades | [Datei: Issue_Overconsumption.docx] | Betriebs-/Kostenüberwachung, relevant für AI-Units-Kalkulation |
| **Authorisierung / Rollen-Erweiterung bei neuen BuKr** | Berechtigungskonzept wird aktuell überarbeitet und vereinfacht; **Kernproblem: die Rollen-Erweiterung bei neuen Buchungskreisen** – bei 101 CC und laufenden Zukäufen ein wiederkehrender manueller Engpass | [FAKT, Kundenauskunft 26.08.2026] | **Direkter Treiber für B-8 (Rollen-Provisionierung) und Pflichtbestandteil des Entity Onboarding (Kap. 4)** |

**Ableitung:** Die Schmerzpunkte bestätigen drei Dinge – (a) es gibt konkrete, wiederkehrende Automatisierungskandidaten (Bankauszug), (b) Datenqualität und Change-Governance sind die kritische Voraussetzung, nicht die Agenten-Technologie selbst, und (c) **die Authorisierung ist nicht nur ein Betriebs-, sondern ein Onboarding-Problem**: Solange jede neue Gesellschaft eine manuelle Rollen-Erweiterung erfordert, ist die Buchungskreis-Fabrik unvollständig. Deshalb wird die Rollen-Provisionierung (B-8) mit Priorität als **fester Bestandteil des Entity Onboarding** geführt (Kap. 4). Das laufende Projekt zur Vereinfachung des Berechtigungskonzepts ist dafür ein günstiges Zeitfenster – ein vereinfachtes Rollenmodell ist deutlich leichter zu templatisieren und zu automatisieren.

---

## 3. Hebel Accounting & Treasury

### 3.1 Tätigkeitslandkarte des kleinen Teams

[FAKT, Kundenauskunft OF-3] Ein Team von **7 internen Personen (3 Accounting, 2 Controlling, 2 Treasury) plus einem externen Steuerberater** betreibt Accounting und Treasury über alle **101 Buchungskreise**. Das bedeutet grob: **ein Accountant je ~30 Entitäten** – ein Verhältnis, das nur über hohe Standardisierung und Automatisierung tragbar ist. Die typischen Tätigkeiten, getrennt nach Automatisierungseignung:

| Tätigkeit | Frequenz | Charakter | Eignung |
|---|---|---|---|
| Kontoauszugsverarbeitung / Cash Application | täglich | repetitiv, regelbasiert | **Automatisierung** |
| Zahlläufe (F110) inkl. Freigabe | mehrmals/Woche | regelbasiert + Kontrolle | **Automatisierung mit 4-Augen-Freigabe** |
| Intercompany-Abstimmung | monatlich + laufend | regelbasiert, hohes Volumen bei vielen CC | **Automatisierung** |
| Intercompany-Finanzierung (Darlehen, Zins) | ereignis-/periodisch | teils urteilsintensiv | **Vorbereitung durch Agent** |
| Liquiditätsplanung / Cash-Position | täglich/wöchentlich | analytisch | **Copilot** |
| FX-Bewertung | periodisch (Monats-/Jahresende) | regelbasiert, aber fehleranfällig | **Automatisierung mit Kontrolle** (vgl. FX-Issue) |
| Anlagenbuchhaltung | laufend/periodisch | regelbasiert | **Automatisierung** |
| Beteiligungsbuchung | ereignisgetrieben (Deals) | urteilsintensiv | **Copilot / Vorbereitung** |
| Abschluss-Tasks (Close) | periodisch | Mix; koordinationsintensiv über viele CC | **Automatisierung der Task-Orchestrierung** |
| Steuermeldungen (UStVA/ZM/VAT) | periodisch | regelbasiert | **Vorbereitung durch Agent** |
| Prüfer-/Auditanfragen | ad hoc | recherche-/nachweisintensiv | **Copilot (Retrieval)** |
| Stammdatenpflege (BP, Bank, Sachkonto) | laufend | regelbasiert, fehleranfällig | **Automatisierung mit Kontrolle** |

### 3.2 Repetitiv vs. urteilsintensiv – die Trennlinie

[EMPFEHLUNG] Die Kernbotschaft für den CFO: Der Hebel liegt darin, das kleine Team **von der Wiederholung zu befreien**, nicht die Urteilsentscheidungen zu ersetzen.

- **Automatisierungskandidaten (Agent führt aus, Mensch gibt frei/prüft):** Kontoauszug/Cash Application, Zahllauf, IC-Abstimmung, FX-Bewertung, Anlagenbuchung, Abschluss-Task-Orchestrierung, Stammdaten-Anlage, Steuermelde-Vorbereitung.
- **Copilot-Kandidaten (Agent unterstützt Urteil):** Liquiditätsplanung, Beteiligungsbuchung bei Deals, Prüfernachweise, IC-Darlehenskonditionen.

### 3.3 Der Multiplikator-Effekt bei VGG

[EMPFEHLUNG] Bei einem klassischen Einzelunternehmen entlastet ein Cash-Application-Agent *eine* Buchhaltung. Bei VGG multipliziert sich jeder automatisierte Prozess über **101 Entitäten**: Ein Agent, der Kontoauszüge oder IC-Abstimmungen entitätsübergreifend übernimmt, skaliert linear mit dem Portfolio – ohne zusätzlichen Headcount. Genau dieser Multiplikator, nicht die Einzelersparnis, ist das ökonomische Argument – und er ist bei einem Verhältnis von ~7 Personen zu 101 Entitäten besonders scharf. Das externe Steuerberater-Setup (Fremdkosten je Buchung/Abschluss) macht Automatisierung zusätzlich unmittelbar kostenwirksam. [ANNAHME] Grobe Bandbreite: 20–40 % der repetitiven Kapazität; belastbare Quantifizierung erfordert Volumendaten (OF-4 offen: Zahl der Kontoauszüge/Zahlläufe/IC-Beziehungen pro Monat).

---

## 4. Die Buchungskreis-Fabrik

> Das strategische Kernstück für einen Serien-Entity-Käufer wie VGG.

### 4.1 IST-Prozess der Buchungskreis-Anlage

**Aktualisiert [FAKT, [Datei: entity_onboaring_prozess/VGG_SAP_XX_Set up new Company Code.md] (v.01/16.04.24)]:** Es existiert ein **vollständiges, manuelles Runbook**. Der IST-Prozess ist damit präzise dokumentiert – und er ist umfangreich und personengebunden. Struktur (mit expliziten SSCUI-IDs aus dem Dokument):

| Phase | Schritte (Auszug) | Werkzeug |
|---|---|---|
| **3.1–3.3 Org-Struktur** | Company Code anlegen; Company (SSCUI 106040); Company↔Company Code zuordnen (SSCUI 101631) | CBC + SSCUI |
| **3.4–3.5 Logistik-Org** | Plant anlegen; Purchase Organization anlegen/zuordnen | CBC |
| **3.6 Finanz-Detailconfig** | Buchungsperioden-Varianten (SSCUI 101018) + FYV-Zuordnung (105409); GL-View (106039); Adressen (105651); Steuerinfo (105675); Paying Company Codes (101001); Payment Methods je CC (101044); alle CC für Zahlungsverkehr (101293); Nummernkreis 38 (101702); Accounting Clerk; Tax-Gruppen-Zuordnung (102521) | ~11 SSCUIs |
| **3.7 GL & Kontenfindung** | Operating CoA kopieren; zusätzliche GL-Konten (Manage G/L Account Master Data); Automatic Account Determination (SSCUI 100297) | Fiori-Apps + SSCUI |
| **3.8 Controlling** | Profit-/Cost-Center-Gruppen und -Stammsätze; Default Profit Center (102529); Default Account Assignments (102639) | Fiori-Apps + SSCUI |
| **3.9 Procurement** | Workflows für Bestellanforderung & Lieferantenrechnung; unterstützende Tabellen; CIM Master-Data-Import | Fiori + Tabellen |
| **3.10 Sales** | Automatic Account Determination (SSCUI 100297) | SSCUI |
| **3.11 Forms** | Footer/Sender-Details; Master-Form-Template-Regeln (SSCUI 101184) | SSCUI |
| **4 Transport** | Transport von Org-Struktur, CoA YCOA, Settings/Kontenfindung, Form-Details zwischen den Systemen | Transportmechanik |

**Kernbefund:** Rund **40 manuelle Einzelschritte** über CBC, ein Dutzend SSCUIs, mehrere Fiori-Apps und ein Transport zwischen DEV/TEST/PROD – **pro neuer Gesellschaft**. Der Prozess ist standardisiert (Runbook existiert), aber vollständig **manuell und personengebunden**. Genau diese deterministische, dokumentierte Schrittfolge ist der ideale Kandidat für die agentische Konfiguration (CAMP4): ein dokumentiertes Runbook mit definierten SSCUI-Zielwerten ist praktisch eine Vorstufe der „Zielkonfiguration als Artefakt".

**Weiterhin offen [ZU PRÜFEN]:** heutige Durchlaufzeit Deal-Close → Buchungsfähigkeit und wer die einzelnen Phasen verantwortet (OF-5).

### 4.2 Zielbild: Entity-Templates

[EMPFEHLUNG] Kern der Fabrik ist ein Satz standardisierter **Entity-Templates**, aus denen die konkrete Konfiguration abgeleitet wird:

| Template | Zweck | LoB-Umfang | Länder-Aspekt |
|---|---|---|---|
| **T1 – SPV / Vorratsgesellschaft (nur Finance)** | Halten von Beteiligungen/Assets, minimaler Betrieb | GL, AP, Bank/Cash, Tax, IC, Group Reporting | DE-Basis, Ländervariante bei Bedarf |
| **T2 – Asset-Entität (Real Estate / Forestry / Agriculture)** | Sachwert-Halter mit Anlagenbuchhaltung | T1 + Asset Accounting, ggf. einfache AR/AP | länderabhängig |
| **T3 – Operative Plattform-Entität** | Portfoliogesellschaft mit Geschäftsbetrieb | T1 + Procurement + Sales + Inventory | volle Ländervariante |
| **T4 – Ausländische Entität** | Entität in CA/FI/LU/NL/UK/US | T1/T2/T3 + Ländervariante (Tax, Bank, Reporting) | Kern des Länder-Handlings |

[ANNAHME] Für VGG dürfte **T1 der häufigste Fall** sein (Serien-SPVs), was die Standardisierung besonders lohnend macht. Die tatsächliche Verteilung ist zu erheben (OF-3).

**Jedes Template trägt ein Rollen-Set [EMPFEHLUNG].** Zum Template gehört nicht nur die Konfiguration, sondern auch das zugehörige **Berechtigungspaket** (welche Business Roles für welche Personen auf dieser Entität): T1 z. B. nur Finance-Rollen für Accounting + externen Steuerberater; T3 zusätzlich Procurement-/Sales-Rollen. So wird die vom Kunden als Painpoint benannte Rollen-Erweiterung Teil des Templates statt manueller Nacharbeit.

### 4.3 Rolle von CAMP4 / Autonomous Enterprise Plus in der Kette

[FAKT, Zielbild] Deloittes „Autonomous Enterprise Plus" unterscheidet zwei Stufen: **Stufe 1 = agentische Konfiguration des Systems** (CAMP4), **Stufe 2 = agentischer Betrieb** (SAP-/Partner-/Eigen-Agenten). Die agentische Konfiguration folgt der festen Kette und dem Prinzip **„Beschreibung vor Herstellung"**: zuerst wird eine **Zielkonfiguration** als versioniertes, prüfbares Artefakt beschrieben, dann in fester Reihenfolge hergestellt:

```
Deal-Close
   │
   ▼
[Zielkonfiguration ableiten]  ← Entity-Template T1–T4 + Länderparameter
   │  (Beschreibung: prüfbar, versioniert, freigabefähig)
   ▼
1) CBC-Scoping        → welche Scope-Items für diese Entität
   ▼
2) Organisationsstruktur → Company Code + zugehörige Org-Einheiten
   ▼
3) SSCUI-Ausprägung   → Detailkonfiguration je Scope-Item
   ▼
4) Stammdaten         → BP, Bankkonten, Sachkonten (Kontenplan-Übernahme)
   ▼
5) Bank-/Steueranbindung → Payment Methods, Tax-Registrierung, Bankkonnektivität
   ▼
6) Rollen & Berechtigungen → Business Roles je Entity-Template zuweisen, SoD prüfen
   ▼
Buchungsfähiger UND bedienbarer Buchungskreis
```

**Schritt 6 ist kein Anhängsel [EMPFEHLUNG, Kundenauskunft OF-Auth].** VGG hat die **Rollen-Erweiterung bei neuen Buchungskreisen** ausdrücklich als Painpoint benannt: Ein Buchungskreis ist erst dann wirklich betriebsbereit, wenn die zuständigen Personen (das ~7-köpfige Team + externer Steuerberater) auch die Berechtigungen darauf haben. Ohne diesen Schritt ist die Entität buchungs-, aber nicht bedienbar. Die Rollen-Provisionierung (B-8) wird deshalb als **Pflichtbestandteil mit Priorität** in die Fabrik gezogen – nicht als optionaler Nachgang. Das aktuell laufende **Vereinfachungsprojekt des Berechtigungskonzepts** ist die ideale Vorarbeit: Ein schlankes, templatisierbares Rollenmodell macht Schritt 6 überhaupt erst sauber automatisierbar.

[FAKT, Zielbild] Jeder Schritt setzt den vorangehenden voraus: Erst Scoping bestimmt die vorhandenen Konfigurationsumfänge, erst die Org-Struktur gibt den SSCUIs ihren Bezugsrahmen. Die Trennung von Beschreibung und Herstellung macht die Anlage **reproduzierbar, prüfbar und versionierbar** (Prinzip 1) – der entscheidende Unterschied zum heutigen teil-manuellen Kopieren.

**Wichtige Einordnung [FAKT, Zielbild]:** CAMP4 ist ein Deloitte-internes Asset/Capability (Talent Group), nicht ein am Markt verfügbares SAP-Produkt. SAP selbst hat „Agent-led Transformation Tooling" (GA ab Q3 2026) angekündigt, jedoch im **RISE-/Brownfield-Kontext**; eine CBC-fähige Public-Edition-Konfiguration durch SAP ist nicht belegt [FAKT, Zielbild Kap. 3.2/Anhang A]. Für VGG bedeutet das: Die Buchungskreis-Fabrik ist heute nur über die Deloitte-Capability realisierbar, nicht als eingekaufter SAP-Standard.

### 4.4 Trennlinie: manuell/rechtlich vs. Agent-vorbereitet vs. Agent-ausgeführt

[EMPFEHLUNG]

| Schritt | Verantwortung | Begründung |
|---|---|---|
| Gesellschaftsgründung, Notar, Handelsregister | **manuell/extern (rechtlich)** | rechtlicher Akt, außerhalb ERP |
| Bankkonto-Eröffnung (Institut) | **manuell/extern** | Bank-KYC, außerhalb ERP |
| Steuerliche Registrierung (Land) | **manuell/extern**, Agent bereitet Unterlagen vor | behördlicher Akt |
| Ableitung der Zielkonfiguration (Template-Auswahl, Parameter) | **Agent bereitet vor**, Mensch gibt frei | Vorschlag prüfbar, Freigabe zwingend (CBC-Scoping ist irreversibel) |
| CBC-Scoping-Herstellung | **Agent führt aus mit Freigabe** | irreversibel → menschliche Freigabe zwingend [FAKT, Zielbild Prinzip 2] |
| Org-Struktur + SSCUI-Ausprägung | **Agent führt aus mit Freigabe** | deterministisch aus Zielkonfiguration |
| Stammdaten (BP, Bank, Sachkonto) im System | **Agent führt aus mit Freigabe** | regelbasiert; Guardrails wg. BP-Löschjob-Erfahrung |
| Bankkonnektivität/Payment-Method-Config | **Agent bereitet vor**, Mensch gibt frei | Zahlungsverkehrssicherheit |
| **Rollen-/Berechtigungszuweisung (Business Roles je Template)** | **Agent führt aus mit Freigabe** (B-8) | Painpoint des Kunden; SoD-Prüfung zwingend, deshalb Freigabe |

### 4.5 Ziel-Durchlaufzeit

[EMPFEHLUNG] **Zielmarke:** Von Deal-Close (Gesellschaft rechtlich existent, Grunddaten bekannt) bis buchungsfähiger Buchungskreis in **wenigen Arbeitstagen** für Standard-Template T1 – gegenüber heute vermutlich mehreren Wochen [ANNAHME, IST-Durchlaufzeit offen, OF-5]. Die verbleibende Wartezeit wird dann von den externen/rechtlichen Schritten (Bankkonto, Steuer-ID) dominiert, nicht mehr von der Systemkonfiguration. Das ist die eigentliche Botschaft: **Die Fabrik verschiebt den Engpass von der IT-Konfiguration auf die unvermeidbaren externen Akte.**

---

## 5. Agenten-Landkarte A / B / C

### 5.0 Kategorien und Autonomiestufen

- **Kategorie A – Gibt es schon:** SAP-Standard-Agenten / Business-AI-Funktionen bzw. Deloitte-Assets, mit belegtem Verfügbarkeitsstatus.
- **Kategorie B – Können wir bauen:** eigene Agenten via Joule Studio / SAP Build / BTP im Rahmen der Public-Cloud-Extensibility.
- **Kategorie C – Andenken:** größere Zielbilder für die 12–24-Monats-Perspektive.

**Autonomiestufen:** *vorschlagen* → *vorbereiten* → *ausführen mit Freigabe* → *autonom*. Für Finance/Treasury bei VGG gilt durchgängig: **kein autonomer Zahlungsverkehr ohne 4-Augen-Freigabe** (vgl. Kap. 7).

**Statushinweis [FAKT, [Datei: sap_ai/AI Features Data.csv]]:** Diese Analyse stützt sich jetzt auf die **kundenseitig gepflegte Liste der SAP-AI-Features für Public Edition** (Quelle: SAP Discovery Center, Kundenexport). Das ist belastbarer als die allgemeine Web-Recherche aus v1 und ersetzt sie für den Verfügbarkeitsstatus. Wichtige Korrektur: Die in v1 aus News-Artikeln zitierten Agenten (Dispute Resolution, Cash Management, AR Agent) tauchen in der **Kundenliste nicht** auf; belegt sind stattdessen die unten genannten Features/Agenten.

### 5.1 Kategorie A – verfügbar / belegt (Kundenliste)

**A) Relevante GA-Features (Joule / Document AI) für Finance:**

| Feature (ID) | Funktion | Status |
|---|---|---|
| Joule for S/4HANA Cloud Public Edition (J74) | konversationale Assistenz (info/navig./transaktional) | **GA** |
| Enterprise Search (J225) | natürlichsprachige Suche über Geschäftsdaten | **GA** |
| Processing of Payment Advices with SAP Document AI (J1104) | automatisierte Zahlungsavis-Verarbeitung | **GA** |
| Creation of Fixed Asset Master Data (J298) | Anlagenstammdaten-Anlage per Joule | **GA** |
| Allocation Run Results (J1003) | Umlage-Ergebnisse einsehen/navigieren | **GA** |
| Aging WIP Analytics & Management (J918) | WIP-Aging-Tracking für Controller | **GA** |
| Error Explanation / Error Resolution for Cost Accounting (J227/J336) | Fehlererklärung + Smart Actions | **GA** |
| Compliance Management (J344) | automatisierte Pflichten-/Datenerfassung aus Dokumenten | **GA** |
| Easy Fill / Easy Filter / Smart Summarization (J281/J91/J90) | Eingabe-/Filter-/Text-Assistenz | **GA** |
| Configuration for US Tax Jurisdictions (J89) | vereinfachte US-Steuerpflege | **GA** |
| SAP Joule for Developers (ABAP AI) (J792) | KI-gestützte ABAP-Entwicklung | **GA** |

**B) Echte „AI Agents" / Beta-Features (noch nicht breit GA):**

| Agent/Feature (ID) | Funktion | Status |
|---|---|---|
| Payment Exception Analysis (J375) | Zahlungsausnahmen analysieren, Lösungen empfehlen | **Beta** |
| Task Automation (J1164) | automatisierte Prozesse aus natürlicher Sprache erstellen/ausführen | **Beta** |
| Smart Solution for Situations in My Home (J181) | Lösungsvorschläge auf der Startseite | **Beta** |
| Billing Posting Agent (J1294) | automatische Auflösung von Buchungsfehlern im Billing | **Early Adopter Care** |
| Billing Adjustment / Anomaly / Creation Agent (J1293/J1550/J1291) | Billing-Automatisierung (Anpassung, Anomalie, Erstellung) | **Early Adopter Care** |
| Project Billing Price Verification Agent (J1325) | Preisabweichungen in Projektfakturierung | **Beta** |

**C) Deloitte-Asset:**

| Asset | Funktion | Status |
|---|---|---|
| **CAMP4 / ConfigPilot** | agentische Konfiguration: Zielkonfiguration → CBC-Scoping → Org → SSCUI | Deloitte-internes Asset, E2E-Test bestanden; kein SAP-Marktprodukt [Zielbild] |

**Präzisierungen [FAKT, sap_ai/AI Features Data.csv]:**
- Für das **VGG-Kernproblem** (Cash Application / Bankauszug, IC-Abstimmung, Close über 101 Entitäten) gibt es in der Kundenliste **keinen fertigen SAP-Standard-Agenten**. Die vorhandenen Agenten liegen im **Billing-Umfeld** (für eine Holding mit wenig eigenem Vertrieb nur begrenzt relevant).
- Das nützlichste GA-Feature für VGG ist **Payment Advices via Document AI (J1104)** und **Payment Exception Analysis (Beta, J375)** – beide unterstützen den Zahlungs-/Cash-Prozess, ersetzen aber keine vollständige Cash-Application.
- **Task Automation (Beta, J1164)** ist strategisch interessant: „automatisierte Prozesse aus natürlicher Sprache" ist die native SAP-Grundlage, auf der sich VGG-spezifische Abläufe agentisch abbilden lassen.
- **AI-Units-/Lizenzmodell:** wird kundenseitig aktuell mit SAP verhandelt [FAKT, OF-6] – Voraussetzung für die Aktivierung der Premium-/Agent-Features.

**Konsequenz für VGG:** Kategorie A liefert heute vor allem **Assistenz-Features (GA)**, aber keinen einsatzfertigen Finance-Betriebs-Agenten für das Kernproblem. Damit sind **Eigenbau (Kategorie B, u. a. auf Basis von Task Automation) und die Deloitte-Konfigurations-Capability (CAMP4) der Hauptpfad** – nicht Ergänzung.

### 5.2 Kategorie B – baubar (Eigenentwicklung)

[FAKT, Web] Kunden/Partner können eigene Agenten bauen; der Reifegrad ist gestaffelt: **Joule Studio Skill Builder GA** (Q2 2025), **Custom-Agent-Building in Beta ab Dez. 2025**, **Joule Studio „Enterprise Scale" noch nicht GA** (Sapphire 2026), **Joule Studio Code Editor (VS-Code) + CLI GA** (Q1 2026) [Web: news.sap.com 2025/07, 2025/10, 2026/05, 2026/04]. Third-Party-Coding-Assistenten (u. a. Claude Code) sind über das Joule-Studio-CLI anbindbar [FAKT, Zielbild].

**Clean-Core-Grenze [ZU PRÜFEN, EMPFEHLUNG]:** Eigenbau muss innerhalb der Public-Cloud-Extensibility bleiben (Side-by-Side auf BTP, freigegebene APIs, keine Kernmodifikation). Konkrete Clean-Core-Extensibility-Restriktionen waren nicht aus einer Live-Quelle verifizierbar und sind über die SAP-Clean-Core-Dokumentation zu belegen (OF-7).

### 5.3 Kategorie C – andenken (strategische Zielbilder)

Größere Zielbilder, aus Kategorie-A/B-Bausteinen zusammengesetzt:

- **Sich selbst onboardende Buchungskreise nach Deal-Close** (Buchungskreis-Fabrik als durchgängiger Agent, Kap. 4).
- **Autonomer Abschluss für Holding-Entitäten** (orchestrierte Close-Tasks über alle CC).
- **Treasury-/Liquiditäts-Copilot über alle Entitäten** (konsolidierte Cash-Position, Vorschläge).
- **Akquisitions-Onboarding-Agent** (von Datenraum/Deal-Close bis ERP-Grundausstattung).

### 5.4 Steckbriefe

Autonomiestufe jeweils als Zielstufe; Start konservativer. Nutzen quantifiziert wo möglich, sonst Bandbreite [ANNAHME]. Aufwand als T-Shirt-Größe. Der maschinenlesbare Katalog liegt in `agenten-katalog.csv`.

---

#### A-1 · Bank-Statement-/Cash-Application-Agent · Kategorie A/B (Hybrid)

- **Problem / Rolle:** Manuelle, fehleranfällige Kontoauszugsverarbeitung; Monatsend-Engpass und blockierende Upload-Fehler [Datei: Ticket_UploadBankstatement.docx]. Betroffen: Accounting Team.
- **Trigger / Frequenz:** täglich, je Bankkonto/Entität (elektronischer Kontoauszug MT940/CAMT).
- **Inputs:** Kontoauszüge, offene Posten (AR/AP), BP-/Bankstammdaten; Scope 4X8 (Advanced Bank Statement Automation), J78 (Advanced Cash Operations), 1EG (Bank Integration File Interface).
- **Aktionen / Autonomiestufe:** Auto-Matching Zahlungseingang↔offener Posten; Ausnahmen zur Klärung vorlegen → *ausführen mit Freigabe* (Ausnahmen: *vorschlagen*).
- **Output:** ausgeglichene offene Posten, Klärungsliste, Buchungsvorschläge.
- **Technologie:** primär SAP-Standard (4X8/J78) ausreizen; Cash Management Agent sobald GA; Lücken via Joule-Skill/Situation Handling (31N).
- **Voraussetzungen:** 4X8/J78 aktiv [Scope S.2], saubere BP-/Bankstammdaten, stabile Bankanbindung.
- **Nutzen:** hoch – direkter Multiplikator über alle Entitäten; behebt akuten Schmerzpunkt.
- **Aufwand:** M (Standard-Ausschöpfung) bis L (Custom-Ergänzung).
- **Risiken/Compliance:** Fehlzuordnung; Guardrails + Nachvollziehbarkeit.
- **Verfügbarkeit/Reifegrad:** Standard 4X8/J78 verfügbar (im Scope); Cash Management Agent **angekündigt** [Web: SAP Connect 10/2025].

---

#### A-2 · Payment-Exception-/Payment-Advice-Agent · Kategorie A (Kundenliste)

- **Problem / Rolle:** Zahlungsausnahmen und Zahlungsavise binden Kapazität im Cash-/AP-Prozess. Betroffen: Accounting/Treasury.
- **Trigger / Frequenz:** ereignisgetrieben (Ausnahme / eingehendes Avis) + laufend.
- **Inputs:** Zahlungsausnahmen, eingehende Payment Advices, offene Posten; Scope J59/J60, 4X8/J78.
- **Aktionen / Autonomiestufe:** Ausnahmen analysieren + Lösungen empfehlen (J375); Avise automatisiert verarbeiten (J1104) → *vorschlagen* / *ausführen mit Freigabe*.
- **Output:** Lösungsempfehlungen für Zahlungsausnahmen, verarbeitete Avise.
- **Technologie:** **Payment Exception Analysis (Beta, J375)** + **Processing of Payment Advices with Document AI (GA, J1104)** [FAKT, sap_ai/AI Features Data.csv].
- **Voraussetzungen:** Lizenz/AI-Units (in Verhandlung, OF-6); J59/J60 aktiv.
- **Nutzen:** mittel–hoch – direkt am Cash-Prozess, GA-Baustein sofort nutzbar.
- **Aufwand:** S–M (Aktivierung/Konfiguration).
- **Risiken/Compliance:** Zahlungsbezug, Datenschutz.
- **Verfügbarkeit/Reifegrad:** J1104 **GA**, J375 **Beta** [FAKT, sap_ai/AI Features Data.csv].

---

#### A-3 · CAMP4 / ConfigPilot – agentische Konfiguration · Kategorie A (Deloitte-Asset)

- **Problem / Rolle:** Manuelle, personengebundene Buchungskreis-Anlage; Skalierungsgrenze bei Serien-Zukäufen. Betroffen: Finance-/Basis-Team, Deloitte-Delivery.
- **Trigger / Frequenz:** je Deal-Close / neue Entität.
- **Inputs:** Entity-Template (T1–T4), Länderparameter; abgeleitete Zielkonfiguration; CBC, SSCUI.
- **Aktionen / Autonomiestufe:** Zielkonfiguration erzeugen (*vorbereiten*) → CBC-Scoping/Org/SSCUI herstellen (*ausführen mit Freigabe*, da CBC-Scoping irreversibel).
- **Output:** buchungsfähiger Buchungskreis; versioniertes, prüfbares Konfigurationsartefakt.
- **Technologie:** CAMP4/ConfigPilot (Deloitte) [Zielbild].
- **Voraussetzungen:** Entity-Templates definiert; Governance; Deloitte-Capability.
- **Nutzen:** **sehr hoch** – Kern-Skalierungshebel für VGG (Kap. 4).
- **Aufwand:** L (Template-Design + Einrichtung) einmalig, dann gering je Entität.
- **Risiken/Compliance:** irreversible CBC-Entscheidungen → Freigabe zwingend; Schreibpfad-Bewertung ggü. SAP [Zielbild Kap. 8].
- **Verfügbarkeit/Reifegrad:** Deloitte-Asset, kein SAP-Marktprodukt; End-to-End-Test bestanden [Zielbild].

---

#### B-1 · Intercompany-Abstimmungs-Agent · Kategorie A/B

- **Problem / Rolle:** IC-Abstimmung über viele CC ist aufwendig; Non-SAP-Gesellschaften via Excel-Upload [Datei: ICMR.xlsx]. Betroffen: Accounting/Group.
- **Trigger / Frequenz:** laufend + monatlich (2. Arbeitstag).
- **Inputs:** IC-Salden/-Belege beider Seiten, Excel-Uploads, Scope 40Y (ICMR), 1GP; **IC-Darlehen/Verzinsung aus E05** [FAKT, OF-7].
- **Aktionen / Autonomiestufe:** Differenzen erkennen, Ursachen clustern, Ausgleichsvorschläge; E05-Zins-/Abrechnungsbuchungen abstimmen → *vorschlagen* / *ausführen mit Freigabe*.
- **Output:** Abstimmungsstatus, Differenzliste, Buchungsvorschläge.
- **Technologie:** ICMR-Standard (40Y) + Task Automation (Beta, J1164) / Joule-Skill für Ursachenanalyse/Uploads; E05-Schnittstelle.
- **Voraussetzungen:** 40Y aktiv [Scope S.2]; einheitliche IC-Kennzeichnung.
- **Nutzen:** hoch – skaliert mit CC-Zahl.
- **Aufwand:** M–L.
- **Risiken/Compliance:** Konsolidierungswirkung; Prüfbarkeit.
- **Verfügbarkeit/Reifegrad:** Standard vorhanden; Agentenlogik Eigenbau (Joule Studio, Custom-Agent Beta ab 12/2025).

---

#### B-2 · Zahlungslauf-Agent mit 4-Augen-Freigabe · Kategorie B

- **Problem / Rolle:** Zahlläufe über viele Entitäten, sicherheitskritisch. Betroffen: AP/Treasury.
- **Trigger / Frequenz:** mehrmals/Woche, terminiert.
- **Inputs:** fällige Verbindlichkeiten, Zahlwege [Datei: Company code data for payment methods_Corrections.xlsx], Bankdaten; Scope 7MJ, 19M, 1EG.
- **Aktionen / Autonomiestufe:** Zahlvorschlag erstellen, Auffälligkeiten (Dubletten, Betragssprünge, neue Empfänger) markieren → *ausführen mit Freigabe*; **nie autonom**.
- **Output:** geprüfter Zahlvorschlag, Ausnahmebericht.
- **Technologie:** F110-Standard + Joule-Skill für Anomalie-Check; Freigabe-Workflow.
- **Voraussetzungen:** Payment-Config konsistent; SoD/Freigabe eingerichtet.
- **Nutzen:** mittel–hoch; hoher Compliance-Wert.
- **Aufwand:** M.
- **Risiken/Compliance:** **hoch** – Zahlungsverkehrssicherheit, Betrug; strikte 4-Augen + Limits.
- **Verfügbarkeit/Reifegrad:** Standard-Payment vorhanden; Anomalie-Agent Eigenbau.

---

#### B-3 · FX-Bewertungs-Agent · Kategorie B

- **Problem / Rolle:** FX-Bewertung fehleranfällig; aktueller Config-Vorfall zeigt Fragilität [Datei: FX_Valuation_Issue_2026.docx]. Betroffen: Accounting/Treasury.
- **Trigger / Frequenz:** Monats-/Jahresende.
- **Inputs:** offene Fremdwährungsposten, Marktkurse (Scope 1S4 – Automatic Market Rates), Ledger-Konfiguration.
- **Aktionen / Autonomiestufe:** Bewertungslauf vorbereiten, Kursquelle/Parameter prüfen, Ergebnisse plausibilisieren → *vorbereiten* / *ausführen mit Freigabe*.
- **Output:** geprüfter Bewertungslauf, Abweichungsanalyse.
- **Technologie:** Standard-FX-Valuation + 1S4 + Joule-Skill für Plausibilisierung.
- **Voraussetzungen:** 1S4 aktiv [Scope S.2]; korrekte Valuation-Area-Config (Lehre aus FX-Issue).
- **Nutzen:** mittel–hoch; reduziert Fehlerrisiko.
- **Aufwand:** M.
- **Risiken/Compliance:** Bewertungsfehler mit Bilanzwirkung; IFRS/HGB-Parallelität.
- **Verfügbarkeit/Reifegrad:** Standard vorhanden; Plausibilisierungs-Agent Eigenbau.

---

#### B-4 · Abschluss-Task-Orchestrierungs-Agent · Kategorie A/B

- **Problem / Rolle:** Close über viele CC koordinationsintensiv. Betroffen: Accounting/Group.
- **Trigger / Frequenz:** periodisch (Monats-/Quartals-/Jahresabschluss).
- **Inputs:** Task-Listen, Status, Abhängigkeiten; Scope 4HG (Advanced Financial Closing Integration), J58.
- **Aktionen / Autonomiestufe:** Tasks planen, Status überwachen, Standard-Tasks auslösen, Blocker eskalieren → *ausführen mit Freigabe*.
- **Output:** Close-Fortschritt, Eskalationen, erledigte Standard-Tasks.
- **Technologie:** Advanced Financial Closing (4HG) + Responsibility Management (1NJ) + Situation Handling (31N).
- **Voraussetzungen:** 4HG, 1NJ, 31N aktiv [Scope S.1–2].
- **Nutzen:** hoch – skaliert mit CC-Zahl.
- **Aufwand:** M.
- **Risiken/Compliance:** Termin-/Vollständigkeitsrisiko; Nachweispflicht.
- **Verfügbarkeit/Reifegrad:** Standard-Bausteine im Scope; Orchestrierungslogik teils Eigenbau.

---

#### B-5 · Stammdaten-Agent (BP, Bankkonto, Sachkonto) · Kategorie B

- **Problem / Rolle:** Stammdatenanlage/-pflege fehleranfällig; BP-Löschjob-Vorfall zeigt Risiko [Datei: VGG_DataInconsistency_BPDeletionJob.docx]. Betroffen: Stammdaten/Accounting.
- **Trigger / Frequenz:** laufend, v. a. bei neuer Entität/Geschäftspartner.
- **Inputs:** Anlage-Requests, Dublettencheck, Scope 1RK/7MI (Mass Load BP), 1RM.
- **Aktionen / Autonomiestufe:** Anlage vorbereiten, Dubletten prüfen, Vollständigkeit sichern → *ausführen mit Freigabe*; **Massenlösch/-änderung nur mit Dry-Run + Freigabe**.
- **Output:** konsistente Stammdaten, Dublettenreport.
- **Technologie:** Mass-Maintenance-Standard + Joule-Skill; Guardrails.
- **Voraussetzungen:** Mass-Load-Scope aktiv [Scope S.2]; Validierungsregeln.
- **Nutzen:** hoch – Datenqualität ist Grundlage aller anderen Agenten.
- **Aufwand:** M.
- **Risiken/Compliance:** **hoch** – Lehre aus BP-Löschjob; zwingend Guardrails/Dry-Run.
- **Verfügbarkeit/Reifegrad:** Standard vorhanden; Agentenlogik Eigenbau.

---

#### B-6 · Steuermelde-Agent (VAT/UStVA/ZM) · Kategorie B

- **Problem / Rolle:** Periodische Steuermeldungen über mehrere Länder. Betroffen: Tax/Accounting.
- **Trigger / Frequenz:** periodisch je Land.
- **Inputs:** Steuerkennzeichen-Buchungen, Scope 77N (VAT), 5XU (Document & Reporting Compliance), 1J2.
- **Aktionen / Autonomiestufe:** Meldung vorbereiten, plausibilisieren, Abweichungen markieren → *vorbereiten*; Einreichung mit Freigabe.
- **Output:** geprüfte Meldeentwürfe, Plausibilisierungsbericht.
- **Technologie:** Document & Reporting Compliance (5XU) + Joule-Skill.
- **Voraussetzungen:** 77N/5XU aktiv [Scope S.2–3]; korrekte Steuerkonfiguration je Land.
- **Nutzen:** mittel–hoch bei 7 Ländern.
- **Aufwand:** M.
- **Risiken/Compliance:** gesetzliche Fristen/Korrektheit; Land-Spezifika.
- **Verfügbarkeit/Reifegrad:** Standard-Compliance im Scope; Vorbereitungs-Agent Eigenbau.

---

#### B-7 · Prüfernachweis-/Audit-Retrieval-Agent · Kategorie B

- **Problem / Rolle:** Prüfer-/Auditanfragen sind recherche-intensiv. Betroffen: Accounting/Reporting.
- **Trigger / Frequenz:** ad hoc (Prüfungssaison).
- **Inputs:** Belege, Kontenauszüge, Berichte; Scope 2OO (External Tax Audit), Analytical Apps.
- **Aktionen / Autonomiestufe:** Anfrage interpretieren, Belege/Nachweise zusammenstellen → *vorschlagen* (Retrieval, kein Buchen).
- **Output:** Nachweispakete mit Quellenverweis.
- **Technologie:** Joule/Retrieval über Finance-Daten; 2OO-Standard.
- **Voraussetzungen:** saubere Belegablage; Berechtigungen.
- **Nutzen:** mittel; punktuell hohe Entlastung.
- **Aufwand:** S–M.
- **Risiken/Compliance:** Datenschutz, Zugriffskontrolle.
- **Verfügbarkeit/Reifegrad:** Retrieval-Skills baubar (Joule Studio GA-Bausteine).

---

#### B-8 · Rollen-/Berechtigungs-Provisionierungs-Agent · Kategorie B · **PRIO (Kunden-Painpoint)**

- **Problem / Rolle:** **Vom Kunden benannter Painpoint:** die Rollen-Erweiterung bei neuen Buchungskreisen. Bei 101 CC und laufenden Zukäufen wiederkehrender manueller Engpass; eine neue Gesellschaft ist ohne Rollen buchungs-, aber nicht bedienbar. Betroffen: IT/Berechtigungen, Finance-Team, externer Steuerberater.
- **Trigger / Frequenz:** je neue Entität / Rollenänderung – bei VGGs Zukauf-Takt regelmäßig.
- **Inputs:** Rollenkataloge, SoD-Regeln, Scope 1NJ (Responsibility Management); **Business-Role-Set je Entity-Template (T1–T4)**; Ergebnisse des laufenden Berechtigungs-Vereinfachungsprojekts [FAKT, Kundenauskunft].
- **Aktionen / Autonomiestufe:** bei Anlage einer Entität das Template-Rollen-Set auf die zuständigen User anwenden, SoD prüfen, Ausnahmen melden → *ausführen mit Freigabe*.
- **Output:** provisionierte Rollen für die neue Entität, SoD-Prüfprotokoll, Ausnahmeliste.
- **Technologie:** Responsibility Management (1NJ) + Provisioning-Skill / Task Automation (J1164); eingebettet in die Buchungskreis-Fabrik (Schritt 6, Kap. 4.3).
- **Voraussetzungen:** **vereinfachtes, templatisiertes Rollenmodell** (laufendes Projekt – idealer Zeitpunkt); Rollen-Set je Entity-Template; SoD-Matrix.
- **Nutzen:** **hoch** – behebt einen benannten Painpoint und macht die Buchungskreis-Fabrik erst vollständig; skaliert mit jedem Zukauf.
- **Aufwand:** M (nach Abschluss des Vereinfachungsprojekts geringer).
- **Risiken/Compliance:** **hoch** – SoD, Zugriffskontrolle; Sonderfall externer Steuerberater mit Buchungsrechten (OF-11).
- **Verfügbarkeit/Reifegrad:** 1NJ im Scope; Provisioning-Logik Eigenbau; **Priorität: mit dem Entity Onboarding, nicht danach.**

---

#### C-1 · Buchungskreis-Onboarding-Agent (End-to-End) · Kategorie C

- **Problem / Rolle:** Durchgängiges Entity-Onboarding von Deal-Close bis Betrieb. Betroffen: gesamtes Finance/IT.
- **Trigger / Frequenz:** je Deal-Close.
- **Inputs:** Deal-/Legal-Daten, Entity-Template, CAMP4-Zielkonfiguration, Stammdaten, Rollen.
- **Aktionen / Autonomiestufe:** orchestriert A-3 (Konfiguration) + B-5 (Stammdaten) + B-8 (Rollen) + Bank/Steuer-Vorbereitung → *ausführen mit Freigabe* an definierten Gates.
- **Output:** betriebsbereite Entität in wenigen Tagen.
- **Technologie:** CAMP4 + Joule-Orchestrierung + SAP AI Agent Hub (Govern) [Zielbild].
- **Voraussetzungen:** A-3, B-5, B-8 vorhanden; Governance/Gates.
- **Nutzen:** **sehr hoch** – die realisierte Buchungskreis-Fabrik.
- **Aufwand:** XL.
- **Risiken/Compliance:** Kette von Freigaben; Fehlerfortpflanzung.
- **Verfügbarkeit/Reifegrad:** Zielbild 12–24 Monate; setzt Kategorie-A/B-Bausteine voraus.

---

#### C-2 · Treasury-/Liquiditäts-**Integrations**-Copilot über alle Entitäten · Kategorie C

- **Problem / Rolle:** Konsolidierte Cash-/Liquiditätssicht über 101 Entitäten fehlt schnell verfügbar; Treasury liegt teils in **Drittsoftware + E05** (nicht in SAP-TRM). Betroffen: Treasury/CFO.
- **Trigger / Frequenz:** täglich + on demand.
- **Inputs:** Bankkontostände (BFA/BFB), Cash-Position (J78), FX (1S4), Planung (2FM) **plus Drittsoftware-Treasury-Daten und E05 (IC-Darlehen/Verzinsung)** [FAKT, OF-4/OF-7].
- **Aktionen / Autonomiestufe:** Cash-Position **über SAP + Drittsystem + E05** konsolidieren, Engpässe/Überschüsse erkennen, IC-Finanzierungsvorschläge → *vorschlagen* (Copilot).
- **Output:** entitätsübergreifendes Liquiditäts-Dashboard, Handlungsvorschläge.
- **Technologie:** Cash Management (J78) + Analytical Apps + Joule-Copilot + **Integration zu Drittlösung/E05** (BTP-seitig).
- **Voraussetzungen:** Schnittstellen zu Drittlösung + E05; Datenqualität; keine SAP-TRM-Objekte vorhanden (bewusst).
- **Nutzen:** hoch – strategische CFO-Sicht; **Integrations-, kein reiner SAP-On-Board-Agent**.
- **Aufwand:** L–XL (wegen Integration).
- **Risiken/Compliance:** Entscheidungsqualität; keine autonomen Anlagen; Schnittstellen-Stabilität.
- **Verfügbarkeit/Reifegrad:** SAP-Bausteine vorhanden; Integration + Copilot 6–18 Monate.

---

#### C-3 · Autonomer Abschluss für Holding-Entitäten · Kategorie C

- **Problem / Rolle:** Standardisierte SPV-Abschlüsse sind hoch repetitiv. Betroffen: Accounting/Group.
- **Trigger / Frequenz:** periodisch.
- **Inputs:** Close-Tasks (4HG), Salden, IC-Status (40Y), FX (B-3).
- **Aktionen / Autonomiestufe:** Standard-Close-Schritte für einfache Entitäten weitgehend autonom, Ausnahmen eskalieren → *ausführen mit Freigabe* → perspektivisch *autonom für T1-SPVs*.
- **Output:** vorbereiteter/erstellter Abschluss je Entität.
- **Technologie:** B-4 + B-3 + B-1 orchestriert.
- **Voraussetzungen:** stabile Standardprozesse; hohe Datenqualität; Prüfakzeptanz.
- **Nutzen:** sehr hoch bei vielen einfachen SPVs.
- **Aufwand:** XL.
- **Risiken/Compliance:** **hoch** – HGB/IFRS-Nachweis, Prüferakzeptanz autonomer Buchungen.
- **Verfügbarkeit/Reifegrad:** Zielbild 18–24+ Monate.

---

### 5.5 Kundenseitig priorisierte Use Cases (VGG-Eigenidentifikation)

[FAKT, Kundenauskunft 26.08.2026] VGG hat **selbst** konkrete AI-Use-Cases benannt. Diese haben strategisch die höchste Priorität, weil das Sponsorship und der Bedarf bereits belegt sind. Die folgende Zuordnung prüft jeden Use Case kritisch gegen die verfügbare Technologie (Kundenliste `sap_ai/AI Features Data.csv`) und trennt „heute mit GA-Feature machbar" von „Eigenbau nötig".

**Übersichts-Mapping:**

| # | Kunden-Use-Case | Machbarkeit / Technologie | Reifegrad |
|---|---|---|---|
| D-1 | Central Invoice Management: BuKr-Zuordnung anhand Rechnungsanschrift | Ariba CIM (4N6, im Scope) + Document AI / Joule-Extraktion | teils GA, teils Eigenbau |
| D-2 | Bilanzanalyse (Abweichung Vormonat/Vorjahr), ggf. Einzelpostenebene | Analytical Business Insights (J88, GA) + Analytical Apps (2JB/BGC) | **GA** |
| D-3 | Rückstellung ausstehende Eingangsrechnungen (Report ER im WF > Betrag X mit Konto/KoStl/PSP) | Task Automation (J1164, Beta) / Enterprise Search (J225) / Joule-Skill | teils GA, teils Beta |
| D-4 | Sachliche Prüfung der Kontierung (Rechnungstext vs. Sachkonto) | Eigenbau-Agent (Textabgleich) auf BTP; Anlehnung an Billing-Anomaly-Muster | Eigenbau |
| D-5 | Self-Service-Auswertung per natürlicher Frage (z. B. Bestellobligo) | **Joule (J74) + Enterprise Search (J225)** – genau dafür gebaut | **GA** |
| D-6 | Anlagevermögen / CO-Verrechnung (SAP-Austausch, Agreement unterschrieben) | Creation of Fixed Asset Master Data (J298, GA), Allocation Run Results (J1003, GA), Universal Allocation (2QL) + SAP-Co-Innovation | **GA-Bausteine + SAP-Dialog** |

**Wichtige Einordnung:** D-2 und D-5 sind **sofort mit GA-Features** adressierbar – die schnellsten Quick Wins im gesamten Papier, weil Bedarf *und* Technologie bereits vorhanden sind. D-6 hat mit dem unterschriebenen SAP-Agreement einen eigenen Kanal (Co-Innovation) und sollte aktiv nachgehalten werden.

---

#### D-1 · Central-Invoice-Management-Agent (BuKr-Zuordnung) · Kategorie A/B

- **Problem / Rolle:** Heute keine automatische Buchungskreis-Zuordnung anhand der Rechnungsanschrift; Rechnungen werden **manuell vorsortiert und dann hochgeladen** [FAKT, Kundenauskunft]. Bei 101 Buchungskreisen ein erheblicher manueller Aufwand. Betroffen: AP/Rechnungseingang.
- **Trigger / Frequenz:** je eingehender Rechnung, laufend.
- **Inputs:** Rechnungsdokument (Anschrift, Empfänger, USt-ID), CC-Stammdaten/Adressen (aus V_001_CLD / Company-Adressen), Scope 4N6 (Ariba Central Invoice Management), J60.
- **Aktionen / Autonomiestufe:** Rechnungsanschrift extrahieren → passenden Buchungskreis ermitteln → Rechnung dem richtigen CC zuordnen → *vorschlagen* (mit Confidence) / *ausführen mit Freigabe*. Ersetzt das manuelle Vorsortieren.
- **Output:** korrekt zugeordnete Rechnung im richtigen Buchungskreis, Ausnahmeliste bei Mehrdeutigkeit.
- **Technologie:** Ariba Central Invoice Management (4N6) + Document AI / Joule-Extraktion; Zuordnungslogik Anschrift↔CC als Joule-Skill / Task Automation (J1164).
- **Voraussetzungen:** saubere CC-Adress-/USt-Stammdaten; 4N6 aktiv [Scope S.4]; AI-Units (OF-6).
- **Nutzen:** hoch – behebt einen benannten, täglichen Schmerzpunkt mit 101-fachem Multiplikator.
- **Aufwand:** M.
- **Risiken/Compliance:** Fehlzuordnung → falscher CC; Freigabe/Confidence-Schwelle; Nachvollziehbarkeit.
- **Verfügbarkeit/Reifegrad:** 4N6 im Scope; Adress-basierte Zuordnung Eigenbau/Extraktion – teils GA-Bausteine (Document AI), teils Custom.

---

#### D-2 · Bilanzanalyse-/Abweichungs-Agent · Kategorie A (GA)

- **Problem / Rolle:** Abweichungsanalyse Vormonat/Vorjahr, wunschgemäß bis auf **Einzelpostenebene**. Betroffen: Accounting/Controlling.
- **Trigger / Frequenz:** periodisch (Monats-/Jahresabschluss) + on demand.
- **Inputs:** GL-Salden/-Einzelposten, Vergleichsperioden; Scope 2JB (Fiori Analytical Apps FI), BGC (G/L), 1SG (Group Reporting).
- **Aktionen / Autonomiestufe:** Abweichungen erkennen, erklären, auf Einzelposten drilldownen, zusammenfassen → *vorschlagen* (analytisch, kein Buchen).
- **Output:** Abweichungsbericht mit Erklärungen und Drilldown auf Belegebene.
- **Technologie:** **Analytical Business Insights (J88, GA)** – „analyze, summarize, turn data into insights" [FAKT, sap_ai/AI Features Data.csv] + Error Explanation (J227) + Analytical Apps.
- **Voraussetzungen:** Premium-Lizenz (J88 ist Premium/„Joule Premium for Financial Management"); Datenqualität.
- **Nutzen:** hoch – wiederkehrende Analyse, sofort GA-fähig.
- **Aufwand:** S (Aktivierung/Konfiguration).
- **Risiken/Compliance:** Interpretationsqualität; Analyse nur, keine Buchung.
- **Verfügbarkeit/Reifegrad:** **GA** (J88, Premium) [FAKT, sap_ai/AI Features Data.csv]. Einzelposten-Drilldown gegen tatsächliche App-Fähigkeit zu prüfen (kleiner Vorbehalt).

---

#### D-3 · Report-Agent „ausstehende Eingangsrechnungen / Rückstellungen" · Kategorie A/B

- **Problem / Rolle:** Für die Rückstellungsbildung ein Excel aller Rechnungen im Workflow für Monat X über Betrag X € – mit Sachkonto, Kostenstelle oder PSP-Element. Heute manuell. Betroffen: Accounting (Abschluss).
- **Trigger / Frequenz:** periodisch (Monatsende) + on demand.
- **Inputs:** Rechnungen im Genehmigungs-Workflow (offen), Schwellenbetrag, Kontierung (Sachkonto/Kostenstelle/PSP); Scope J60, 2V7 (Monitoring GR/IR), Purchase Order Accruals (2VB).
- **Aktionen / Autonomiestufe:** offene Workflow-Rechnungen filtern (Betrag > X), Kontierung anreichern, Liste/Export erzeugen → *vorschlagen* (Report); optional Rückstellungsvorschlag → *vorbereiten*.
- **Output:** strukturierte Liste/Excel als Rückstellungsgrundlage.
- **Technologie:** Enterprise Search (J225, GA) + Task Automation (J1164, Beta) / Joule-Skill; ggf. Purchase Order Accruals (2VB).
- **Voraussetzungen:** Zugriff auf Workflow-Status offener Rechnungen; AI-Units (OF-6).
- **Nutzen:** mittel–hoch; direkte Abschlussentlastung, wiederkehrend.
- **Aufwand:** S–M.
- **Risiken/Compliance:** Vollständigkeit der Rückstellungsbasis (Nachweispflicht); reiner Report unkritisch, Rückstellungsbuchung mit Freigabe.
- **Verfügbarkeit/Reifegrad:** Enterprise Search **GA**; Automatisierung teils **Beta** (J1164).

---

#### D-4 · Kontierungs-Prüf-Agent (sachliche Prüfung) · Kategorie B

- **Problem / Rolle:** Sachliche Prüfung, ob die Kontierung zum Rechnungsinhalt passt (Beispiel Kunde: „laut Rechnungstext Beratung → auch auf Beratung gebucht?"). Betroffen: AP/Accounting.
- **Trigger / Frequenz:** je Rechnung / stichprobenartig, laufend.
- **Inputs:** Rechnungstext/Positionstexte, gebuchtes Sachkonto/Kostenart, Kontenbeschreibungen; Scope J60, 2V7.
- **Aktionen / Autonomiestufe:** Rechnungstext semantisch mit gebuchtem Konto abgleichen, Auffälligkeiten markieren → *vorschlagen* (Prüfhinweis, kein Umbuchen).
- **Output:** Prüfliste „Kontierung plausibel / auffällig" mit Begründung.
- **Technologie:** Eigenbau-Agent (LLM-Textabgleich) auf BTP; methodisch verwandt mit Billing-Anomaly-Agent-Muster (J1550) und Task Automation (J1164).
- **Voraussetzungen:** Zugriff auf Belegtexte + Kontenstammdaten; Extensibility (OF-7b); AI-Units.
- **Nutzen:** mittel–hoch; verbessert Buchungsqualität, entlastet manuelle Prüfung (auch beim externen Steuerberater).
- **Aufwand:** M (Eigenbau, Prompt-/Regelkalibrierung).
- **Risiken/Compliance:** False Positives/Negatives; als Assistenz, nicht als automatische Umbuchung; menschliche Entscheidung bleibt.
- **Verfügbarkeit/Reifegrad:** Eigenbau (kein GA-Standardagent); Bausteine (Document AI, Task Automation) verfügbar.

---

#### D-5 · Self-Service-Auswertungs-Copilot · Kategorie A (GA)

- **Problem / Rolle:** Fachbereich soll Auswertungen (z. B. Bestellobligo) per einfacher natürlicher Frage erhalten, ohne Report-Bau. Betroffen: Self-Service-User (über Finance hinaus).
- **Trigger / Frequenz:** on demand.
- **Inputs:** Geschäftsdaten (Bestellungen/Obligo, FI/CO), natürliche Frage; Scope 2QU (PO Visibility/Procurement Spend), 1JI, Analytical Apps.
- **Aktionen / Autonomiestufe:** Frage interpretieren, passende Daten/Report liefern → *vorschlagen* (informational).
- **Output:** direkte Antwort/Auswertung im Dialog.
- **Technologie:** **Joule (J74, GA) + Enterprise Search (J225, GA)** – exakt der vorgesehene Anwendungsfall [FAKT, sap_ai/AI Features Data.csv]; ergänzt um KPI/Report Summary (J232).
- **Voraussetzungen:** Joule aktiviert, Berechtigungen; ggf. Premium-Features.
- **Nutzen:** hoch – breite Nutzerentlastung, kein Report-Bau; sofort GA.
- **Aufwand:** S (Aktivierung/Enablement).
- **Risiken/Compliance:** Berechtigungs-/Datenschutzgrenzen je User; Antwortqualität.
- **Verfügbarkeit/Reifegrad:** **GA** (J74, J225) [FAKT, sap_ai/AI Features Data.csv].

---

#### D-6 · Anlagevermögen & CO-Verrechnung (SAP-Co-Innovation) · Kategorie A/C

- **Problem / Rolle:** Optimierung von Anlagenbuchhaltung und CO-Verrechnung. **Besonderheit:** SAP hat aktiv einen Austausch gewünscht, VGG hat ein **Agreement unterschrieben** – bislang ohne Rückmeldung von SAP [FAKT, Kundenauskunft]. Betroffen: Accounting/Controlling.
- **Trigger / Frequenz:** laufend/periodisch (Verrechnungsläufe, Anlagenpflege).
- **Inputs:** Anlagenstammdaten, Verrechnungszyklen; Scope J62 (Asset Accounting), 1GB, 2QL (Universal Allocation), 1GI (Allocation Cycle), J54 (Overhead Cost Accounting).
- **Aktionen / Autonomiestufe:** Anlagenstammdaten-Anlage unterstützen (J298), Verrechnungsergebnisse aufbereiten/erklären (J1003) → *vorbereiten* / *vorschlagen*.
- **Output:** effizientere Anlagenpflege, transparente Verrechnungsergebnisse.
- **Technologie:** **Creation of Fixed Asset Master Data (J298, GA)**, **Allocation Run Results (J1003, GA)** [FAKT, sap_ai/AI Features Data.csv] + Universal Allocation (2QL) + potenzielle SAP-Co-Innovation.
- **Voraussetzungen:** SAP-Rückmeldung zum Agreement aktiv nachhalten; AI-Units.
- **Nutzen:** mittel–hoch; GA-Bausteine sofort, größeres Zielbild über SAP-Dialog.
- **Aufwand:** S (GA-Features) bis L (Co-Innovation-Scope).
- **Risiken/Compliance:** Abhängigkeit vom SAP-Dialog; Bewertungs-/Verrechnungskorrektheit.
- **Verfügbarkeit/Reifegrad:** GA-Bausteine (J298, J1003) verfügbar; Co-Innovation offen (SAP-seitig).

---

## 6. Bewertung, Priorisierung, Roadmap

### 6.1 Bewertungslogik

[EMPFEHLUNG] Zwei Achsen:

- **Impact** = FTE-Entlastung × Entitäts-Multiplikator + Durchlaufzeit-/Risiko-/Compliance-Wirkung + Skalierbarkeit bei Zukäufen.
- **Machbarkeit** = Verfügbarkeit (GA/Beta/Standard/Eigenbau) × Datenbasis × Public-Cloud-Konformität × Aufwand (invers).

### 6.2 Impact-/Machbarkeits-Matrix

| Agent | Impact | Machbarkeit | Feld |
|---|---|---|---|
| A-1 Bank-Statement/Cash-Application | hoch | hoch (Scope aktiv) | **Quick Win** |
| B-1 Intercompany-Abstimmung | hoch | mittel–hoch (40Y aktiv) | **Quick Win / Kern** |
| B-4 Abschluss-Task-Orchestrierung | hoch | mittel–hoch (4HG/1NJ/31N) | **Quick Win / Kern** |
| B-5 Stammdaten-Agent | hoch | mittel (Guardrails nötig) | **Quick Win (Enabler)** |
| B-8 Rollen-Provisionierung | **hoch (Kunden-Painpoint)** | mittel (1NJ aktiv; Rollenprojekt läuft) | **Quick Win / Fabrik-Pflichtteil** |
| A-3 CAMP4-Konfiguration | sehr hoch | mittel (Deloitte-Capability) | **Strategisch** |
| B-2 Zahlungslauf-Agent | mittel–hoch | mittel | mittelfristig |
| B-3 FX-Bewertung | mittel–hoch | mittel | mittelfristig |
| B-6 Steuermelde | mittel–hoch | mittel | mittelfristig |
| A-2 Payment-Exception/-Advice | mittel–hoch | hoch (J1104 GA, J375 Beta) | Quick Win (GA-Baustein) |
| B-7 Prüfernachweis | mittel | hoch | opportunistisch |
| C-1 Buchungskreis-Onboarding E2E | sehr hoch | niedrig (setzt Bausteine voraus) | **Strategisch** |
| C-2 Treasury-Copilot | hoch | niedrig–mittel | **Strategisch** |
| C-3 Autonomer Abschluss | sehr hoch | niedrig | Vision |
| C-4 Akquisitions-Onboarding | hoch | niedrig | Vision |
| **D-2 Bilanz-/Abweichungsanalyse** | hoch | **sehr hoch (J88 GA)** | **Quick Win (Kundenpriorität)** |
| **D-5 Self-Service-Copilot** | hoch | **sehr hoch (J74/J225 GA)** | **Quick Win (Kundenpriorität)** |
| **D-1 CIM BuKr-Zuordnung** | hoch | mittel (4N6 + Extraktion) | **Kundenpriorität** |
| **D-3 Report ausstehende ER** | mittel–hoch | mittel–hoch (J225 GA + Beta) | **Kundenpriorität** |
| **D-6 Anlagevermögen/CO** | mittel–hoch | hoch (J298/J1003 GA + SAP-Dialog) | **Kundenpriorität** |
| **D-4 Kontierungs-Prüfung** | mittel–hoch | mittel (Eigenbau) | **Kundenpriorität** |

*Die D-Use-Cases sind kundenseitig priorisiert (Kap. 5.5) und genießen dadurch Sponsorship-Vorrang gegenüber gleich bewerteten Kandidaten.*

### 6.3 Top-5 Quick Wins

1. **D-2 Bilanz-/Abweichungsanalyse** – Kundenpriorität, sofort GA (J88), reine Analyse ohne Buchungsrisiko.
2. **D-5 Self-Service-Auswertungs-Copilot** – Kundenpriorität, sofort GA (J74/J225), breite Nutzerentlastung.
3. **A-1 Bank-Statement/Cash-Application** – Scope aktiv (4X8/J78), behebt akuten Schmerzpunkt, hoher Entitäts-Multiplikator.
4. **D-1 Central Invoice Management (BuKr-Zuordnung)** – Kundenpriorität, behebt tägliches manuelles Vorsortieren über 101 CC.
5. **B-8 Rollen-Provisionierung** – **Kunden-Painpoint**; Rollen-Erweiterung bei neuen BuKr; Pflichtteil des Entity Onboarding, Zeitfenster durch laufendes Rollenprojekt.

*Nachrücker (weiterhin hoch priorisiert):* B-5 Stammdaten-Agent, B-1 Intercompany-Abstimmung, B-4 Abschluss-Task-Orchestrierung, D-3 Report ausstehende ER, D-6 Anlagevermögen/CO.

### 6.4 Top-3 strategische Initiativen

1. **A-3 CAMP4 – agentische Buchungskreis-Konfiguration** (höchste Skalenwirkung für Serien-Zukäufer).
2. **C-1 Buchungskreis-Onboarding-Agent E2E** (die realisierte Fabrik, orchestriert die Quick-Win-Bausteine + A-3).
3. **C-2 Treasury-/Liquiditäts-Copilot** (konsolidierte CFO-Sicht über alle Entitäten).

---

## 7. Roadmap

[EMPFEHLUNG] Drei Horizonte mit Abhängigkeiten. Alle Zeitangaben ab Projektstart; Reihenfolge wichtiger als absolute Termine.

### Horizont 0–3 Monate – Fundament & Quick Wins

- **Voraussetzungen schaffen:** Produktiv-Scope bestätigt (OF-1 geklärt: DEV=Prod); Datenqualität BP/Bank/GL prüfen (Lehre BP-Löschjob); AI-Units-/Lizenzmodell mit SAP finalisieren (OF-6 in Verhandlung).
- **Kundenprioritäten mit GA-Features sofort:** **D-2** Bilanz-/Abweichungsanalyse (J88) und **D-5** Self-Service-Copilot (J74/J225) aktivieren + Enablement.
- **A-2** Payment Advices (J1104, GA) einführen; Payment Exception Analysis (J375, Beta) pilotieren.
- **A-1** Bank-Statement/Cash-Application: Standard 4X8/J78 ausreizen, Situation Handling (31N) für Ausnahmen.
- **B-5** Stammdaten-Enabler starten (Guardrails, Templates).
- **B-8 Rollen-Provisionierung (Kunden-Painpoint):** an das laufende Berechtigungs-Vereinfachungsprojekt andocken – Rollen-Set je Entity-Template definieren, als Pflichtschritt ins Entity Onboarding einbauen.
- **D-6** SAP-Rückmeldung zum unterschriebenen Anlagevermögen/CO-Agreement aktiv nachhalten; GA-Bausteine (J298, J1003) nutzen.
- **Governance-Grundlage:** 4-Augen/SoD, Freigabe-Gates definieren (Kap. 8).
- *Abhängigkeit:* AI-Units-Lizenz (OF-6); Datenqualität.

### Horizont 3–12 Monate – Kernprozesse & Fabrik-Pilot

- **D-1** Central-Invoice-Management-Agent (BuKr-Zuordnung) produktiv.
- **D-3** Report-Agent ausstehende Eingangsrechnungen; **D-4** Kontierungs-Prüf-Agent (Eigenbau).
- **B-1** Intercompany-Abstimmung (inkl. E05), **B-4** Abschluss-Task-Orchestrierung produktiv.
- **B-2 / B-3 / B-6** Zahlungslauf-, FX-, Steuermelde-Agent (mit Freigabe).
- **A-3 CAMP4-Pilot:** Entity-Template T1 (SPV) auf Basis des Onboarding-Runbooks definieren, erste agentische Buchungskreis-Anlage mit Freigabe.
- *Abhängigkeit:* Task Automation (J1164)/Custom-Agent-Reife; BTP-Extensibility (OF-7b); Enablement des ~7-köpfigen Teams.

### Horizont 12–24 Monate – Autonomie & Skalierung

- **C-1** Buchungskreis-Onboarding-Agent E2E über Templates T1–T4.
- **C-2** Treasury-/Liquiditäts-Copilot über alle Entitäten.
- **C-3 / C-4** autonomer SPV-Abschluss und Akquisitions-Onboarding als kontrollierte Piloten.
- *Abhängigkeit:* Reife der Bausteine; SAP AI Agent Hub (Govern); Prüferakzeptanz; Change im Team.

**Querschnitt-Abhängigkeiten:** (a) Datenqualität ist Daueraufgabe; (b) Lizenz-/AI-Units-Klarheit steuert Ausbautempo; (c) Enablement des kleinen Teams ist kritischer Pfad – bei ~7 Personen ist Change-Kapazität knapp, daher die sequenzielle Einführung mit den GA-fähigen Kundenprioritäten (D-2/D-5) zuerst.

---

## 8. Risiken, Governance, Voraussetzungen

[EMPFEHLUNG] Leitplanken, die für jede Agenten-Initiative bei VGG gelten:

### 8.1 Clean Core & Public-Cloud-Extensibility

- Keine Kernmodifikation. Eigenbau nur Side-by-Side (BTP) über freigegebene APIs; Konfiguration nur über CBC/SSCUI [FAKT, Zielbild Kap. 5].
- Extensibility-Grenzen in Public Edition sind konkret zu belegen (OF-7) [ZU PRÜFEN].
- **Konsequenz:** Die Buchungskreis-Fabrik nutzt die deklarative „Beschreibung-vor-Herstellung"-Logik (Zielkonfiguration als versioniertes Artefakt) – Clean-Core-konform und reproduzierbar.

### 8.2 HGB/IFRS-Nachweispflichten

- Group Ledger IFRS (1GA) und HGB-Anforderungen parallel; jede agentische Buchung muss revisionssicher nachvollziehbar sein.
- **Autonome Buchungen** (C-3) brauchen frühzeitige Abstimmung mit Wirtschaftsprüfer (Prüferakzeptanz).

### 8.3 4-Augen-Prinzip & Segregation of Duties (SoD)

- **Kein autonomer Zahlungsverkehr.** Zahlläufe (B-2) und Massen-Stammdatenaktionen (B-5) immer mit Freigabe und SoD-Trennung.
- Agenten-Identitäten und ihre Berechtigungen unterliegen derselben SoD-Kontrolle wie menschliche User; Governance über SAP AI Agent Hub [FAKT, Zielbild Phase 3].

### 8.4 Zahlungsverkehrssicherheit

- Anomalie-Checks (neue Empfänger, Betragssprünge, Dubletten) vor jedem Zahllauf; Limits und Eskalation.
- Bankkonnektivität und Payment-Method-Config besonders schützen (kritische Außenwirkung).

### 8.5 Datenschutz & EU AI Act

- Verarbeitung personenbezogener Daten (BP, Zahlungsempfänger) DSGVO-konform; Data Protection & Privacy (5LE) im Scope [Scope S.2] – **aber**: Der BP-Löschjob-Vorfall zeigt, dass 5LE-Automatik selbst Risiken birgt [Datei: VGG_DataInconsistency_BPDeletionJob.docx].
- EU AI Act: Finance-Agenten mit Entscheidungswirkung sind hinsichtlich Risikoklassifizierung und Transparenzpflichten zu bewerten [ZU PRÜFEN, OF-8].

### 8.6 Change bei sehr kleinem Team

- 13–16 Personen [ANNAHME] tragen zugleich Betrieb und Transformation → Change-Kapazität ist der Engpass.
- **Empfehlung:** Wenige, hochwirksame Agenten sequenziell einführen (nicht alle parallel); Enablement und Vertrauen (Freigabe-Erfahrung) vor Autonomie-Ausbau.

### 8.7 Datenqualität als Grundvoraussetzung

- Kein Agent ist besser als seine Datenbasis [FAKT, Zielbild Kap. 4: „Kein System ist von Haus aus AI-ready"].
- Die dokumentierten Vorfälle (FX-Valuation, BP-Löschjob, Bankauszug, AA-Determination) sind vor breitem Agenten-Rollout zu bereinigen.

---

## 9. Offene Fragen an den Kunden und nächste Schritte

Der vollständige, gruppierte Fragenkatalog liegt in `offene-fragen.md`. Kernfragen:

**Stand nach Kundenantworten v2 (26.08.2026):** Die meisten strukturellen Fragen sind geklärt; offen bleiben vor allem Volumina und Prozess-Baselines.

| Nr. | Frage | Status | Warum entscheidend |
|---|---|---|---|
| OF-1 | Produktiv-Scope & Buchungskreise? | **geklärt** – DEV=Prod; 101 CC | Multiplikator/Template-Design |
| OF-2 | Treasury-/Payment-Gap-Items? | **geklärt** – Drittlösung, kein SAP-TRM/APM nötig | Gap-Analyse geschlossen |
| OF-3 | Verteilung Entitäten auf Templates T1–T4? | **teilweise** – Serien-SPVs dominieren (aus CC-Liste ersichtlich); genaue Zuordnung offen | Priorisierung der Fabrik |
| OF-4 | Volumina (Kontoauszüge, Zahlläufe, IC, Buchungen/Monat)? | **offen** | Quantifizierung des Nutzens |
| OF-5 | Durchlaufzeit Buchungskreis-Anlage (Deal-Close → buchungsfähig)? | **teilweise** – Runbook bekannt (~40 Schritte), Zeit offen | Baseline für Ziel-Durchlaufzeit |
| OF-6 | AI-Units-/Lizenzmodell? | **in Verhandlung** mit SAP | Steuert Ausbautempo/Business Case |
| OF-7 | Treasury-Architektur / E05? | **geklärt** – E05 (Eigenentwicklung) für Cash Pooling + IC-Darlehen | Integrationsdesign C-2 |
| OF-8 | EU-AI-Act-Klassifizierung der Finance-Agenten? | **offen** | Compliance |
| OF-9 | Deloitte-CAMP4-Kollaboration? | **angeteasert** – gemeinsame Entwicklung im Gespräch | strategische Partnerschaft |

**Nächste Schritte (Empfehlung):**
1. Kurz-Workshop zu den Restpunkten: Volumina (OF-4), Durchlaufzeit + Verantwortlichkeiten (OF-5), Template-Zuordnung (OF-3), EU AI Act (OF-8).
2. Datenqualitäts-Assessment (BP/Bank/GL) – Lehre aus BP-Löschjob/FX-Issue.
3. Quick-Win-Pilot A-1 (Bank-Statement/Cash-Application) + A-2 (Payment Advices/Exceptions, GA-Baustein) starten.
4. CAMP4-Template-Design T1 (SPV) auf Basis des vorhandenen Onboarding-Runbooks initiieren – und die von VGG angeteaserte **gemeinsame Entwicklung** (OF-9) konkretisieren.

---

## 10. Ausblick: Was das konkret bedeutet, wie wir es umsetzen, in welchem Horizont

[EMPFEHLUNG] Dieses Kapitel übersetzt die Strategie in ein konkretes Umsetzungsbild – von den heutigen Grundlagen bis zur weitgehend autonom betriebenen und agentisch konfigurierten VGG-Finanzplattform.

### 10.1 Das Zielbild in einem Satz

**Eine SAP-S/4HANA-Cloud-Umgebung, in der neue Buchungskreise nach einem Deal in Tagen agentisch entstehen (inkl. Konfiguration, Stammdaten und Rollen) und in der die wiederkehrenden Finanzprozesse über alle 101+ Entitäten weitgehend von Agenten mit menschlicher Freigabe betrieben werden – bedient über eine konversationale Oberfläche.** Das entspricht Deloittes „Autonomous Enterprise Plus": agentischer Betrieb (SAP-Stufe) plus agentische Konfiguration (CAMP4-Stufe) [FAKT, Zielbild].

### 10.2 Die technische Grundlage: SAP Business AI Platform

**Kontext:** Die Vorbereitung der **SAP Business AI Platform** übernimmt kundenseitig ein Kollege. Das ist die richtige Reihenfolge – sie ist die **Voraussetzung** für alles Agentische, denn „kein System ist von Haus aus AI-ready" [FAKT, Zielbild Kap. 4]. Was sie liefert und wofür VGG sie braucht:

| Schicht der Business AI Platform | Was sie leistet | Wofür VGG sie nutzt |
|---|---|---|
| **Contextualize & Reason** (Business Data Cloud, Knowledge Graph, Zugang zu LLMs) | Geschäftskontext + Sprachmodelle | Datenbasis für D-2/D-5, Retrieval für Prüfer-/Self-Service |
| **Build** (Joule Studio, Integration Suite) | Agenten/Skills bauen + orchestrieren | Eigenbau-Agenten (Kategorie B), Integration zu Drittlösung/E05 |
| **Govern** (SAP AI Agent Hub) | Registry, Observability, Freigabe/Authentifizierung | Kontrolle & Freigabe-Gates (Kap. 8.3), Kostentransparenz (AI-Units) |

**Konkret heißt das:** Sobald die Plattform steht und das AI-Units-Lizenzmodell geklärt ist (OF-6), lassen sich (a) die GA-Features (D-2, D-5) einschalten, (b) Eigenbau-Agenten (D-1, D-4, B-Serie) im Joule Studio entwickeln und (c) alle Agenten zentral über den AI Agent Hub steuern und freigeben. Ohne diese Plattform bleiben die Agenten Einzellösungen ohne gemeinsame Governance.

### 10.3 Wie wir vorgehen – vier konkrete Schritte

1. **Aktivieren, was da ist (GA).** D-2 (Bilanzanalyse, J88) und D-5 (Self-Service-Copilot, J74/J225) einschalten und das Team anlernen. Kein Entwicklungsaufwand, sofortiger Nutzen – der Beweis am lebenden Objekt.
2. **Painpoints gezielt bauen.** B-8 (Rollen-Provisionierung) an das laufende Rollenprojekt koppeln; D-1 (CIM BuKr-Zuordnung) und A-1 (Bank-Statement/Cash-Application) als erste Eigenbau-/Standard-Kombinationen. Jeweils mit Freigabe, Guardrails, Nachvollziehbarkeit.
3. **Die Fabrik zusammensetzen.** A-3 (CAMP4) mit Entity-Template T1 pilotieren; B-5 (Stammdaten) und B-8 (Rollen) als Bausteine integrieren – Ergebnis ist der End-to-End-Onboarding-Agent (C-1).
4. **Zur Konzernsicht skalieren.** C-2 (Treasury-Integrations-Copilot über SAP + Drittlösung + E05), C-3 (autonomer SPV-Abschluss) – kontrollierte Piloten mit Prüferabstimmung.

Jeder Schritt ist eigenständig nützlich und Voraussetzung für den nächsten – kein „Big Bang", sondern eine Kette belegbarer Zwischenergebnisse. Das passt zur knappen Change-Kapazität des ~7-köpfigen Teams.

### 10.4 Horizonte auf einen Blick

| Horizont | Was konkret entsteht | Bausteine | Voraussetzung |
|---|---|---|---|
| **0–3 Monate** | GA-Features live; Rollen-Painpoint adressiert; erste Cash-/Invoice-Automatisierung | D-2, D-5, B-8, A-1, A-2, D-6-Bausteine | Business AI Platform steht, AI-Units geklärt, Datenqualität |
| **3–12 Monate** | Kernprozesse agentisch (IC, Close, Zahllauf, FX, Steuer); Fabrik-Pilot T1; CIM/Report/Kontierung | B-1, B-2, B-3, B-4, B-6, D-1, D-3, D-4, A-3 | Joule Studio / Task Automation reif; BTP-Extensibility (OF-7b); Enablement |
| **12–24 Monate** | End-to-End-Buchungskreis-Fabrik; Konzern-Treasury-Copilot; autonome SPV-Abschlüsse (kontrolliert) | C-1, C-2, C-3, C-4 | reife Bausteine; AI Agent Hub; Prüferakzeptanz; Change |

### 10.5 Was VGG davon hat

- **Betriebskontinuität trotz kleiner Decke:** ~7 Personen bleiben für 101+ Entitäten handlungsfähig, auch bei weiterem Zukauf – ohne proportionalen Headcount-Aufbau.
- **Schnelleres Onboarding:** Deal-Close → bedienbarer Buchungskreis in Tagen statt Wochen; der Engpass verschiebt sich auf die unvermeidbaren externen Akte (Notar, Bankkonto, Steuer-ID).
- **Höhere Qualität & geringeres Risiko:** weniger manuelle Fehler (Kontoauszug, Kontierung, Rollen), durchgängige Nachvollziehbarkeit und Freigabe.
- **Kostenwirkung:** weniger externe Buchungs-/Abschlusskosten (Steuerberater), effizientere Nutzung der internen Kapazität.

### 10.6 Bedingungen für das Gelingen

Datenqualität (Dauerthema), geklärtes AI-Units-Modell (OF-6), abgeschlossenes/koordiniertes Rollen-Vereinfachungsprojekt, Prüferakzeptanz für höhere Autonomiestufen (OF-8) und – kritischster Pfad – die begrenzte Change-Kapazität des kleinen Teams, die die sequenzielle Einführung erzwingt. Die von VGG angeteaserte **gemeinsame CAMP4-Entwicklung** (OF-9) würde den Fabrik-Teil erheblich beschleunigen und ist strategisch separat zu bewerten (Scope, IP, Rollen, Governance).

---

## Anhang A – Scope-Item-Tabelle

[FAKT, Scope S.1–4] Aktivierte Scope-Items im Workspace „ERP VGG IMP DEV - CUST" (Customizing/DEV, Stand 25.08.2026). Länder: CA, FI, DE, LU, NL, UK, US. Status/Ländervariante je Item nicht in der PDF ausgewiesen [ZU PRÜFEN].

| ID | Bezeichnung | LoB / Cluster |
|---|---|---|
| 1GA | Accounting and Financial Close – Group Ledger IFRS | Ledger |
| 1NJ | Responsibility Management | App Platform / übergreifend |
| 31N | Situation Handling | App Platform / übergreifend |
| 4HI | Proactive Maintenance | Asset Mgmt |
| 4HH | Reactive Maintenance | Asset Mgmt |
| 2Q2 | Data Migration to S/4HANA from Staging | Data Mgmt |
| 5LE | Data Protection and Privacy | Data Mgmt |
| 1YB | Import Connection Setup with SAP Analytics Cloud | Data Mgmt |
| 1KA | Information Lifecycle Management | Data Mgmt |
| 1RK | Mass Load and Mass Maintenance for Business Partner | Data Mgmt |
| 7MI | Mass Load and Mass Maintenance for Business Partners | Data Mgmt |
| 1RM | Mass Load and Mass Maintenance for Product | Data Mgmt |
| 1FD | Workforce Enablement | Data Mgmt / HR |
| J58 | Accounting and Financial Close | Finance – Close |
| J60 | Accounts Payable | Finance – AP |
| J59 | Accounts Receivable | Finance – AR |
| 4X8 | Advanced Bank Statement Automation | Finance – Bank/Cash |
| J78 | Advanced Cash Operations | Finance – Bank/Cash |
| 4HG | Advanced Financial Closing Integration | Finance – Close |
| J62 | Asset Accounting | Finance – Assets |
| 1GB | Asset Accounting – Group Ledger IFRS | Finance – Assets |
| BFH | Asset Under Construction | Finance – Assets |
| 1GF | Asset Under Construction – Group Ledger IFRS | Finance – Assets |
| 2LH | Automated Invoice Settlement | Finance/Proc/SC |
| 1S4 | Automatic Market Rates Management | Finance – Treasury-nah |
| 1EG | Bank Integration with File Interface | Finance – Bank |
| BFA | Basic Bank Account Management | Finance – Bank |
| BFB | Basic Cash Operations | Finance – Cash |
| BD6 | Basic Credit Management | Finance – AR |
| 7MJ | Basic Payment Management | Finance – Payments |
| 1GO | Cash Journal | Finance – Cash |
| 1J2 | Compliance Formats – Support Preparation | Finance – Compliance |
| 19M | Direct Debit | Finance – Payments |
| 5XU | Document and Reporting Compliance | Finance – Compliance |
| 4GQ | Event-Based Revenue Recognition – Project-Based Sales | Finance – RevRec |
| 4GR | Event-Based Revenue Recognition – Project-Based Sales – IFRS | Finance – RevRec |
| 2OO | External Tax Audit | Finance – Tax |
| 1HB | Financial Plan Data Upload from File | Finance – Planning |
| 2FM | Financial Planning and Analysis | Finance – Planning |
| 1GI | General Ledger Allocation Cycle | Finance – GL |
| 1SG | Group Reporting – Financial Consolidation | Finance – Group |
| 1GP | Intercompany Financial Posting | Finance – IC |
| 40Y | Intercompany Reconciliation Process | Finance – IC |
| BEJ | Inventory Valuation for Year-End Closing | Finance/SC |
| 1ZT | Managing Material Price Changes and Inventory Values | Finance/SC |
| J55 | Margin Analysis | Finance – CO |
| 2V7 | Monitoring of Goods and Invoice Receipts | Finance/Proc |
| 4PG | Organizational Flexibility in Financial Accounting | Finance – GL |
| J54 | Overhead Cost Accounting | Finance – CO |
| BNA | Period-End Closing – Projects | Finance – Projects |
| 2I3 | Predictive Commitments Management | Finance |
| 1NT | Project Control – Finance | Finance / R&D |
| 4I9 | Project Control – Sales | Finance / R&D |
| 2VB | Purchase Order Accruals | Finance |
| 2QY | SAP Fiori Analytical Apps for Asset Accounting | Finance – Analytics |
| 2JB | SAP Fiori Analytical Apps for Financial Accounting | Finance – Analytics |
| BGC | SAP Fiori Analytical Apps for G/L Accounting | Finance – Analytics |
| BEG | Standard Cost Calculation | Finance – CO |
| 2QL | Universal Allocation | Finance – GL |
| 1FD | Workforce Enablement | HR |
| 1LQ | Output Management | IT Mgmt |
| 2QU | Analytics – Purchase Order Visibility and Procurement Spend | No LoB |
| 3AF | Group Account Preparation for Financial Consolidation | No LoB / Group |
| BGG | SAP Fiori Analytical Apps for Inventory and Warehouse Mgmt | No LoB |
| 77N | VAT Tax Calculation and Reporting | No LoB / Tax |
| 22P | Manage Documents | R&D |
| 35F | Project Control – Capital Projects | R&D |
| 1YF | Project Review | R&D |
| 1EZ | Credit Memo Processing | Sales |
| BKP | Customer Returns | Sales |
| 1F1 | Debit Memo Processing | Sales |
| 1MI | Delivery Processing Without Order Reference | Sales |
| BKA | Free Goods Processing | Sales |
| BDA | Free of Charge Delivery | Sales |
| BKL | Invoice Correction Process with Credit Memo | Sales |
| BDQ | Invoice Correction Process with Debit Memo | Sales |
| BDD | Lean Customer Returns | Sales |
| 1MC | Omnichannel Convergent Billing | Sales |
| 2EQ | Sale of Services | Sales |
| BDH | Sales Order Entry with One-Time Customer | Sales |
| 2ET | Sales Order Processing for Non-Stock Material | Sales |
| BKJ | Sales Order Processing with Customer Down Payment | Sales |
| BDG | Sales Quotation | Sales |
| 1BS | SAP Fiori Analytical Apps for Sales | Sales |
| BD9 | Sell from Stock | Sales |
| BNX | Consumable Purchasing | Sourcing/Proc |
| 4N6 | Invoice Processing with SAP Ariba Central Invoice Mgmt | Sourcing/Proc |
| J45 | Procurement of Direct Materials | Sourcing/Proc/SC |
| 22Z | Procurement of Services | Sourcing/Proc |
| BMD | Purchase Contract | Sourcing/Proc |
| 1JI | Real-Time Reporting and Monitoring for Procurement | Sourcing/Proc |
| 18J | Requisitioning | Sourcing/Proc |
| 2LN | Basic Available-to-Promise Processing | Supply Chain |
| BMC | Core Inventory Management | Supply Chain |
| BML | Physical Inventory – Inventory Count and Adjustment | Supply Chain |
| BMK | Return to Supplier | Supply Chain |

*Hinweis: Einige Items erscheinen in der PDF mehrfach unter verschiedenen LoB (z. B. 2LH, J45, 1NJ, 1FD, 1NT, 4I9) – hier einmal je Primärcluster geführt.*

---

## Anhang B – Daten-Inventar (Auszug)

[FAKT für Dateiexistenz; abgeleitete Zahlen ANNAHME] Sichtung Kundenordner `…/Projekt/Viessmann/`.

| Kategorie | Datei(en) | Relevanter Inhalt | Kennzeichnung |
|---|---|---|---|
| Buchungskreise / User | CIM User Mapping.xlsx; Authorization/Business Role - Business User_CashManagement.xlsx | CC-Nummern, ~13–16 Finance/Treasury-User, Rollen | ANNAHME (Indikator) |
| Kontenplan | GL_Accounts/G_L_AccountMapping.xlsx; Aktuelle Mapping IDL_ERP…xlsx | mehrere Tausend Konten, mehrere CoA-Varianten | ANNAHME |
| Zahlwege | Company code data for payment methods_Corrections.xlsx | Payment-Method-Config je CC | FAKT (Existenz) |
| Treasury/Bank | GL_Accounts/Treasury*.xlsx; BP_Masterdata/BankMapping_V1.xlsx; Treasury - 2nd_workshop.pptx | Bankverbindungen (mehrere Institute/Währungen), Cash-Pool-Prozesse | FAKT/ANNAHME |
| FX | FXValuation.xlsx; FX Valuation/…; FX_Valuation_Issue_2026.docx | FX-Bewertung + aktueller Config-Vorfall | FAKT |
| Intercompany | ICMR.xlsx | ICMR-Setup, Excel-Upload Non-SAP zum 2. AT | FAKT/ANNAHME |
| BK-Anlage (IST) | Documentation/CopyCoA2newCompanyCode.docx; CreateCopyAccounts.docx; Implementaion VESTA Gesellschaften/ | Copy-CoA-/Konten-Anlageprozess | FAKT (Existenz) |
| Migration/Volumen | Migration/Migration results OP …xlsx; VGG ERP - OP Sachkonten 31.12…xlsx | OP-Volumina (Migrationsstand) | FAKT (Existenz), ANNAHME (Betrieb) |
| Schmerzpunkte | VGG_DataInconsistency_BPDeletionJob.docx; Ticket_UploadBankstatement.docx; AA Acc Det Issue Ticket.docx; Issue_Overconsumption.docx | eskalierte Tickets/Issues | FAKT (Existenz) |
| Onboarding/Design | Viessmann_Phase 0 Finance…pptx; KDD_Draft.xlsx; Champion_S4 Public Cloud_KickOff.pptx | Projekt-/Design-Historie | FAKT (Existenz) |

**Datenqualitäts-Gesamteinschätzung (v2):** Mit dem Config-Export (`current_config/`), der SAP-AI-Liste (`sap_ai/`) und dem Onboarding-Runbook (`entity_onboaring_prozess/`) sind die zentralen Kennzahlen jetzt **belegt statt geschätzt** (CC-Zahl, Länder, Headcount, IST-Prozess, verfügbare AI-Features). Offen bleiben v. a. **Transaktionsvolumina** (OF-4) und die **gemessene Durchlaufzeit** der Buchungskreis-Anlage (OF-5).

---

## Anhang B2 – Buchungskreisliste (101 Company Codes)

[FAKT, [Datei: current_config/V_001_CLD.xlsx]] Verteilung: **88 DE, 4 CA, 3 US, 2 NL, 2 LU, 1 GB, 1 FI**; Währungen: 93 EUR, 4 CAD, 3 USD, 1 GBP. Auszug (repräsentativ; vollständige Liste in der Quelldatei):

| CC | Name | Land | Whg | Ort |
|---|---|---|---|---|
| 1024 | Bioferm GmbH | DE | EUR | Schwandorf |
| 1040 | Viessmann Generations Gr. | DE | EUR | Battenberg/Eder |
| 1850/1883/1884…2313 | Vis 1–13 Investment GmbH & Co KG (Serie) | DE | EUR | Battenberg/Eder |
| 1891–1899/2412/2413 | Vis n Invst Vwltng GmbH (Komplementär-Serie) | DE | EUR | Battenberg/Eder |
| 2615/2625/2630/2635/2640 | USA Residential Invest I–V | DE | EUR | Köln/Battenberg |
| 2780–2787/2730 | GForce n GmbH (Serie) | DE | EUR | Frankfurt/Battenberg |
| 3020/3021/3022 | Vesta Familienhold GmbH / Verwaltung / Investment | DE | EUR | Battenberg/Eder |
| 3070/3071 | Vesta Forest Group GmbH / Verwaltung | DE | EUR | Battenberg/Eder |
| 1503/1504/1506 | Vesta Forest Canada / Sustainable Forest Dev / WC Real Estate | CA | CAD | Halifax |
| 1502 | Vesta Forest Finland | FI | EUR | Helsinki |
| 1550/1551 | HKB Holding BV / HKB Ketelbouw Venlo B.V. | NL | EUR | Venlo |
| 2701/2702 | Vi Entrepreneurial Inv Ho / I | LU | EUR | Bertrange |
| 2320 | Viessmann Investment UK | GB | GBP | Birmingham |
| 2350 | Viessmann Invest Canada | CA | CAD | Waterloo |
| 2370 | Viessmann Investment NA | US | USD | Newark |
| 2711/2712 | Viessmann C&C NA Inc. / KPS Aggregator LLC | US | USD | Newark |

*Das Serien-Muster (Investment-KG + zugehörige Verwaltungs-GmbH als Komplementär, dazu Immobilien-/Forst-/Clean&Cold-Serien) ist der Kern des „Buchungskreis-Fabrik"-Arguments (Kap. 4).*

---

## Anhang B3 – SAP-AI-Features / -Agenten (Kundenliste, Public Edition)

[FAKT, [Datei: sap_ai/AI Features Data.csv]] Kundenexport aus SAP Discovery Center. Für Finance/übergreifend relevante Einträge (Auswahl):

| ID | Name | Typ | Status |
|---|---|---|---|
| J74 | Joule with S/4HANA Cloud Public Edition | AI Feature | GA |
| J225 | Enterprise Search | AI Feature | GA |
| J1104 | Processing of Payment Advices with SAP Document AI | AI Feature | GA |
| J298 | Creation of Fixed Asset Master Data | AI Feature | GA |
| J1003 | Allocation Run Results | AI Feature | GA |
| J918 | Aging Work in Progress Analytics and Management | AI Feature | GA |
| J227 / J336 | Error Explanation / Error Resolution for Cost Accounting | AI Feature | GA |
| J344 | Compliance Management | AI Feature | GA |
| J89 | Configuration for US Tax Jurisdictions | AI Feature | GA |
| J792 | SAP Joule for Developers (ABAP AI) | AI Feature | GA |
| J375 | Payment Exception Analysis | AI Feature | Beta |
| J1164 | Task Automation | AI Feature | Beta |
| J181 | Smart Solution for Situations in My Home | AI Feature | Beta |
| J1294 | Billing Posting Agent | AI Agent | Early Adopter Care |
| J1293 / J1550 / J1291 | Billing Adjustment / Anomaly / Creation Agent | AI Agent | Early Adopter Care |
| J1325 | Project Billing Price Verification Agent | AI Agent | Beta |

*Vollständige Liste (48 Einträge inkl. Supply Chain/Procurement/Sales) in der Quelldatei. Kein eigenständiger Cash-Application-/IC-/Financial-Close-Agent enthalten – bestätigt die Einordnung in Kap. 5.1.*

---

## Anhang C – Quellen

**Kundeninputs**
- Scope-Items: `Agents_AutonomusEnterprise/current_scope/ERP VGG IMP DEV - CUST scope (1).pdf` (4 Seiten, Stand 25.08.2026).
- Buchungskreise/Config: `Agents_AutonomusEnterprise/current_config/` – u. a. `V_001_CLD.xlsx` (101 Company Codes), `GL_ACCOUNT.xlsx`, `Summary.xlsx` (Config-Objekte mit SSCUI-IDs).
- SAP-AI-Features: `Agents_AutonomusEnterprise/sap_ai/AI Features Data.csv` (Discovery-Center-Export, 48 Einträge).
- Onboarding-Runbook: `Agents_AutonomusEnterprise/entity_onboaring_prozess/VGG_SAP_XX_Set up new Company Code.md` (v.01/16.04.24).
- Kundenauskünfte OF-1…OF-9 (26.08.2026).
- Kundendatenordner: `…/Projekt/Viessmann/` (Dateien wie in Anhang B zitiert).

**Deloitte-intern**
- `…/Projekt/CAMP4/Zielbild_Autonomous_Enterprise.md` – „Autonomous Enterprise Plus" (Talent Group, Stand 21.07.2026). Definitionen zu CAMP4, Kette Scoping→Org→SSCUI, Prinzipien, Wettbewerbs-/Faktenstand.
- `…/Projekt/SAP Knowledge/SAP Autonomous Suite/` – interne Ideensammlung/Übersicht (Kontext, nicht als Primärquelle für Verfügbarkeiten verwendet).

**Web (Abruf 25.08.2026)**
- https://www.viessmann.group – Geschäftsmodell, Portfolio, Purpose.
- https://news.sap.com/2026/04/sap-business-ai-release-highlights-q1-2026/ – Dispute Resolution Agent (Beta, Public Edition), 30+ Agenten/2.500+ Skills, Joule Studio Code Editor/CLI (GA).
- https://news.sap.com/2025/07/sap-business-ai-release-highlights-q2-2025/ – Accounts Receivable Agent (Beta), Joule Studio Skill Builder (GA).
- https://news.sap.com/2025/10/sap-connect-finance-ai-innovation/ – Cash Management Agent, Accruals Agent (angekündigt), „autonomous finance".
- https://news.sap.com/2025/10/sap-connect-business-ai-new-joule-agents-embedded-intelligence/ – 14 neue Joule Agents, Custom-Agent-Building (Beta ab 12/2025).
- https://news.sap.com/2025/02/joule-sap-uniquely-delivers-ai-agents/ – Cash Collection Agent (geplant).
- https://news.sap.com/2026/05/new-joule-studio-enterprise-scale-agentic-development/ – Joule Studio Enterprise Scale (noch nicht GA).
- https://news.sap.com/2026/08/customer-industry-solutions-shape-future-autonomous-enterprises/ – Autonomous-Enterprise-Vision (Industry AI).

**Nicht abrufbar (JS-gated/403), für Verifizierung nötig:** help.sap.com (AI Units), me.sap.com/processnavigator (Scope-Item-IDs der Gap-Kandidaten), community.sap.com.

---

## Anhang D – „Was ich nicht wusste" (offene Punkte)

**Stand v2 (26.08.2026):** Durch die Kundenantworten und die vier neuen Primärquellen sind die meisten v1-Unsicherheiten geschlossen. Was in v1 offen war und jetzt geklärt ist:

- ✅ **Produktiv-Scope** = DEV-Scope (OF-1).
- ✅ **Buchungskreise:** 101 belegt inkl. Länder/Währung (V_001_CLD.xlsx).
- ✅ **Headcount:** 7 intern + externer Steuerberater (OF-3).
- ✅ **Treasury-Gaps:** bewusst per Drittlösung + E05 gedeckt, kein SAP-TRM/APM nötig (OF-2/OF-7).
- ✅ **SAP-AI-Verfügbarkeit:** durch Kundenliste belegt (ersetzt Web-Schätzung); kein fertiger Cash-Application-/IC-/Close-Agent vorhanden.
- ✅ **IST-Onboarding:** vollständiges Runbook mit ~40 Schritten und SSCUI-IDs (OF-5, Schrittfolge).

**Weiterhin offen:**

1. **Transaktionsvolumina** (Kontoauszüge/Zahlläufe/IC-Beziehungen/Buchungen pro Monat) – für belastbaren Business Case (OF-4).
2. **Gemessene Durchlaufzeit** Deal-Close → buchungsfähiger CC und Verantwortlichkeiten je Phase (OF-5).
3. **Genaue Template-Zuordnung** der 101 Entitäten (T1–T4) – aus CC-Namen ableitbar, aber nicht bestätigt (OF-3).
4. **AI-Units-/Lizenzmodell:** aktuell zwischen VGG und SAP in Verhandlung (OF-6).
5. **Clean-Core-Extensibility-Grenzen** für Eigenbau: weiter separat zu belegen (OF-7-technisch).
6. **EU-AI-Act-Einordnung** der konkreten Finance-Agenten (OF-8).
7. **CAMP4-Produktivreife** bei VGG: Zielbild belegt E2E-Test, kein Produktiv-Rollout; VGG hat gemeinsame Entwicklung angeteasert (OF-9).

*Grundlage v2: Kundenantworten + Config-/AI-/Onboarding-Export (26.08.2026), Web-Recherche (25.08.2026), internes Zielbild (21.07.2026). SAP-Verfügbarkeiten unterliegen kurzen Änderungszyklen – vor externer Verwendung erneut prüfen.*

#### C-4 · Akquisitions-Onboarding-Agent · Kategorie C

- **Problem / Rolle:** Von Deal/Datenraum zur ERP-Grundausstattung inkl. Eröffnungsbilanz. Betroffen: M&A/Finance.
- **Trigger / Frequenz:** je Akquisition.
- **Inputs:** Deal-Daten, Eröffnungsbilanz, Kontenmapping, Stammdaten.
- **Aktionen / Autonomiestufe:** C-1 + initiale Datenübernahme/Mapping vorbereiten → *vorbereiten* / *ausführen mit Freigabe*.
- **Output:** onboardete Akquisition mit Eröffnungsdaten.
- **Technologie:** C-1 + Migrationswerkzeuge (Data Migration from Staging 2Q2).
- **Voraussetzungen:** C-1; Datenmigrations-Anbindung.
- **Nutzen:** hoch bei operativen Zukäufen (weniger bei reinen SPVs).
- **Aufwand:** XL.
- **Risiken/Compliance:** Datenqualität der Zielgesellschaft; Mapping-Fehler.
- **Verfügbarkeit/Reifegrad:** Zielbild 18–24+ Monate.
