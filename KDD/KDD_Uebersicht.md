# KDD-Übersicht DUS-Accounting – SAP S/4HANA Cloud Public Edition

Stand: 28.09.2026 · Quelle der Anforderungen: `KDD_Items_For Analysis.xlsx` (Sheet „Items_For Analysis", 53 Anforderungen) · Vorab-Klassifizierung: `KDD_Analyse_Ergebnis.xlsx` / `.json` · Vorlage: `KDD Template.pptx` (bindend, je KDD eine PPTX mit Deckblatt, Folie 1/2 „KDD Beschreibung", Folie 2/2 „Bewertung aus funktionaler Sicht"; Langfassungen und Quellenangaben in den Notizen der Folien 2 und 3).

Selektionskriterien: Drittsystem, BTP-Lösung, starker Change. Requirements, die im Standard, per Konfiguration oder In-App-Extensibility (Custom Fields, Custom Logic, Custom Analytical Queries, Situation Handling) abbildbar sind, erhalten keine KDD.

## Erstellte KDDs (9)

| Nr. | ID | Datei | Titel | Requirements | Kriterium | Empfehlung (Option 1, mit Stern) | Kritikalität | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | KDD_FI_001 | KDD_01_Workflow-Framework.pptx | Workflow- und Genehmigungsframework | 3-154, 3-99, 3-155, 3-156, 3-158, 3-84, 3-118, 3-172, 3-205, 3-153 (+ Freigabeanteil 3-103) | BTP, Change, Drittsystem (SuccessFactors) | Standard Flexible Workflow (Rechnungsfreigabe, Responsibility Management) plus SAP Build Process Automation auf SAP BTP für alle nicht abgedeckten Freigaben; SAP Task Center als Sammelinbox; Genehmiger zentral in Responsibility Management | hoch | Offen |
| 2 | KDD_FI_002 | KDD_02_Integrationsarchitektur.pptx | Integrationsarchitektur für Nicht-SAP-Schnittstellen (Leitfall ATLED/Unicad) | 3-396, 3-192, 3-197, Integrationspunkt 3-102; Plattform für 3-68, 3-182, 3-187, 3-156, 3-207 | Drittsystem, BTP | SAP Integration Suite (BTP) als zentrale Middleware; ATLED per REST/SOAP, Verkaufsaufträge über API_SALES_ORDER_SRV; Fallback Standard-Import-App | hoch | Offen |
| 3 | KDD_FI_003 | KDD_03_Parken-Kassenautomaten-ReconHub.pptx | B2C-Massenerlöse Parken und Recon-Hub-Ablösung | 3-68, 3-175 | Drittsystem, Change | Recon Hub (Abrantix) bleibt Abstimm-Engine; verdichtete Erlös-/Zahlungsbuchungen mit Projektkontierung per Integration Suite nach S/4HANA Cloud; Ablösung nach Vorliegen der Volumen neu bewerten | hoch | Offen |
| 4 | KDD_FI_004 | KDD_04_Airport-Billing-SkyBilling.pptx | Airport-Billing: Ablösung Sky Billing | 3-181, 3-182 | Drittsystem, BTP, Change | Zielbild SAP Subscription Billing mit Standard-Integration nach S/4HANA Cloud (Scope Item 57Z, zu verifizieren), unter Vorbehalt der Vermessung; Fallback: Sky Billing als Rating-Engine beibehalten | hoch | Offen |
| 5 | KDD_FI_005 | KDD_05_Archiv-DMS.pptx | Archiv und Dokumentenmanagement (Enscale-Ablösung) | 3-207, Ablageanteil 3-153 | Drittsystem, BTP | Dediziertes DMS/ECM (Enscale oder Nachfolger) als führendes Archiv, Anbindung über SAP Document Management Service Integration Option (CMIS) | hoch | Offen |
| 6 | KDD_FI_006 | KDD_06_Investitionsprojekte-AiB.pptx | Investitionsprojekte, Anlagen im Bau und CAPEX/OPEX | 3-64, 3-193 (Abhängigkeit 3-205, 3-197) | Change | Standardprozess Capital Projects (35F) mit vorgangsbezogener Abrechnung (EB0001), Investitionsprofil nur auf Maßnahmen-PSP (eine AiB je Maßnahme), OPEX über getrennte PSP-Elemente | hoch | Offen |
| 7 | KDD_FI_007 | KDD_07_Anlagenklassen-Nutzungsdauer-Migration.pptx | Anlagenklassen, Nutzungsdauer und Anlagenmigration | 3-188, 3-206 | Change | Granulare Standard-Anlagenklassen mit festen Nutzungsdauern/AfA-Schlüsseln je Bewertungsbereich; Migration kumulierter Werte plus laufendes Jahr über das Migrationscockpit (BH5) | hoch | Offen |
| 8 | KDD_FI_008 | KDD_08_HR-Gehaltszahlungen-Payroll.pptx | HR-Gehaltszahlungen und Payroll-Integration | 3-187 | Drittsystem | Zahlung durch das Payroll-System (Bankdatei), Buchung in S/4HANA Cloud (Übergang: Datei über Integration Suite, später Standard-Integration SuccessFactors Employee Central Payroll) | hoch | Offen |
| 9 | KDD_FI_009 | KDD_09_Kautionsverwaltung-Fioport.pptx | Kautionsverwaltung und Verzinsung (Fioport) | 3-176 | Drittsystem | Fioport bleibt für Kautionskonten und Verzinsung; Kautionen als Sonderhauptbuchposten je Mieter in S/4HANA Cloud; jährliche Zinsbuchung aus Fioport-Export | mittel | Offen |

Entscheidungsstatus aller KDDs: Offen (Entscheider und Datum leer). Felder Process Owner, Product Manager (IT), DAB-Entscheidungsdatum: „offen" (in den Dokumenten nicht enthalten). Deckblatt (Folie 1) bewusst leer gelassen.

## Bewusst keine KDD (29 Requirements)

| ID | Kurztitel | Begründung |
|---|---|---|
| 3-50 | SD-003 Gutschriftsformular, Referenz je Position (1EZ) | Formularanpassung (Adobe Forms); im Requirement als „kein KDD" markiert |
| 3-52 | SD-005 Lastschriftformular Brutto/Netto (1F1) | Formularkorrektur; „kein KDD" |
| 3-77 | SD-008 Rechnungskorrektur-Formular (BKL) | Formularanpassung; „kein KDD" |
| 3-286 | SD-021 Fakturaformular Auftragsnummer (BKZ) | Formularanpassung; „kein KDD" |
| 3-80 | FI-GL-05-01 Ausstehende Eingangsrechnungen auf Kreditor | Standard kann Abgrenzungen nicht auf den Kreditor buchen (Merkposten nur informativ); Fit-to-Standard-Entscheidung auf Stream-Ebene (Rückstellung auf Sachkonto, Kreditor als Referenz, PO-Accruals). Abweichung: Analyse „Process Change" |
| 3-88 | FI-GL-02-01 CSV/Excel-Massenupload | Standard-App „Hauptbuchbelege hochladen" deckt den Massenupload ab; Layoutumstellung per Excel-Mapping zumutbar; Abdeckung von Debitoren-/Kreditorenzeilen im System zu verifizieren. Abweichung: Analyse „Process Change" |
| 3-90 | FI-GL-03-03 Nicht-Standard-Reportings | Custom Analytical Queries (Key-User-Extensibility); Analytics-Strategie (SAC) ist Programmthema, nicht durch dieses Low-Requirement ausgelöst. Abweichung: Analyse „BTP" |
| 3-92 | FI-GL-06-01 Rückstellungsspiegel mit Bewegungsarten | Laut Fit/Gap FIT ohne BTP; Bewegungsarten sind Konfiguration und Schulung. Abweichung: Analyse „Process Change" |
| 3-93 | FI-GL-06-02 Altsalden-Migration mit Bewegungsarten | Migrationsthema Hauptbuch |
| 3-96 | FI-GL-07-01 MB5L-Pendant | Standard-App identifizieren und aktivieren |
| 3-97 | FI-AP-01-03 Leistungszeitraum-Feld, automatische RAP | Custom Field in CIM und S/4HANA plus Custom Logic; vorher Scope Item 2VB (Purchase Order Accruals) prüfen. Abweichung: Analyse „BTP" |
| 3-100 | FI-AP-03-01 E-Mail-Steuerung Zahlungsavis | In-App-BAdI für zusätzliche Avis-Empfänger, ggf. Custom Field |
| 3-101 | FI-AP-04-01 Nebenbuch-an-Nebenbuch | Dokumentierter Standard-Workaround über Verrechnungskonto |
| 3-102 | FI-AP-04-02 Endrechnungskennzeichen Baurechnungen | Kennzeichen und Obligo FIT; offener Integrationspunkt Cosware/RE-FX in KDD_FI_002 geführt. Abweichung: Analyse „BTP" |
| 3-103 | FI-AP-04-04 Dauerbuchung Kreditorenrechnung | App F4312 Standard; Freigabeanteil in KDD_FI_001 |
| 3-104 | FI-AP-05-02 Feldebene-Berechtigungen | Rollen-/App-Trennung Standard; Feldebene Bankverbindung über Standard-Prüfung sensibler Felder zu verifizieren |
| 3-105 | FI-AP-06-01 Workflow für FI-Rechnungen ohne Bestellbezug | Laut Fit/Gap FIT („Vollständig sichern" auch ohne Bestellbezug). Abweichung: aus Workflow-Bündel entfernt |
| 3-106 | FI-AP-06-02 Buchen-Button einschränken | Custom Validation plus Berechtigung (In-App). Abweichung: Analyse „BTP" |
| 3-108 | FI-AR-01-03 Info an Fachbereich ab Mahnstufe 2 | Situation Handling bzw. In-App-BAdI; Zuordnung Mahnung zu Fachbereich ist Konfiguration. Abweichung: aus Workflow-Bündel entfernt |
| 3-111 | FI-TAX-02-02 Automatischer Storno USt-Zahllast | Kleiner GAP mit Prozess-Workaround |
| 3-114 | FI-TAX-02-06 Lesbare Auswertung Meldungen | FIT über Data Preview in „Run Statutory Reports". Abweichung: Analyse „BTP" |
| 3-160 | FI-AP-04-05 Sicherheitseinbehalte | Standard-Zahlungssperre/Teilzahlung; Konzeption im Deep-Dive |
| 3-162 | FI-AP-05-03 Stammdaten-Governance, Onventis/Ariba | Governance ist organisatorisch; Frage des führenden Systems hängt an der Einkaufsplattform (offener Punkt in KDD_FI_002). Abweichung: Analyse „Process Change" |
| 3-171 | FI-AR-01-04 E-Mail-Steuerung Korrespondenzarten | Standard-Customizing bzw. In-App-BAdI je Korrespondenzart |
| 3-178 | FI-AR-05-01 Rechnungsnummer vs. Belegnummer | Konfigurationsentscheidung auf Stream-Ebene |
| 3-184 | FI-TAX-01-02 Ertragsteuern, §60 Abs. 2 EStDV | Ledger-Frage vom Kunden entschieden (kein Steuerledger, IFRS-Ledger nicht zweckentfremden); Restfrage Tooling (Excel mit Standardreports); nur bei Beschaffung eines Drittanbieter-Steuertools KDD. Abweichung: Analyse „BTP" |
| 3-199 | FI-AA-06-02 CSV-Upload Eigenleistung/Rückstellungen | Standard-App F2548/F0718 (analog 3-88) |
| 3-203 | FI-AA-08-02 Query tägliche Rechnungsdurchsicht | Standard-Apps F1614/F1060A plus Custom Analytical Query. Abweichung: Analyse „BTP" |
| 3-204 | FI-AA-08-03 Durchsicht kontierter Bestellungen | Standard-App F0842A, Custom Analytical Query, Application Job. Abweichung: Analyse „BTP" |

## Abweichungen von der vorhandenen Analyse (KDD_Analyse_Ergebnis)

- In der Analyse fehlen 3-156 (SuccessFactors-Abhängigkeit, jetzt in KDD_FI_001) und 3-187 (HR-Gehaltszahlungen, Very High, jetzt KDD_FI_008).
- Sieben BTP-Einstufungen wurden auf In-App-Lösungen zurückgestuft (3-90, 3-97, 3-102, 3-106, 3-114, 3-203, 3-204), drei „Process Changes" ohne Steering-Committee-Relevanz (3-80, 3-88, 3-92) und 3-184 (Ledger-Frage bereits entschieden), 3-162 (organisatorisch).
- 3-105 (FIT) und 3-108 (In-App) wurden aus dem Workflow-Bündel entfernt.
- 3-68 und 3-175 wurden zu einer KDD zusammengefasst (gleiche Designentscheidung), 3-182 der Billing-KDD zugeordnet, 3-192 und 3-197 der Integrations-KDD, 3-206 der Anlagen-KDD.

## Hinweise und Unsicherheiten

- Scope-Item-IDs, die nicht in den Dokumenten stehen, sind in den KDDs als „zu verifizieren" markiert (57Z Subscription Billing, BH5 Migrationscockpit, 16R Multi-Bank Connectivity, 2VB Purchase Order Accruals).
- Nicht aus den Dokumenten ableitbar und als offene Punkte geführt: technische Basis von Sky Billing (eigenständig oder R/3-Eigenentwicklung), Transaktionsvolumen Parken, Anzahl Freigeber/Web-User, HR-/Payroll-Zeitplan und -System, Fähigkeiten von Enscale (CMIS), Anzahl Z-Anlagenklassen, Volumen und Verzinsungsregeln der Kautionen.
- In jeder KDD stehen die zwei realistischsten Optionen in der Tabelle; verworfene Alternativen sind unter „Lösungsvorschläge beschreiben" genannt. Option 1 ist jeweils die empfohlene (Stern gemäß Vorlage).
- Die Sprechblase am linken Folienrand (Kategorien der Gap-Klassifizierung) ist Bestandteil der Vorlage und wurde unverändert belassen.
