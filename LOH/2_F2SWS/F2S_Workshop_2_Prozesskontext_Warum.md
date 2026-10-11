# F2S-Workshop 2 – Prozesskontext: Warum und wofür die Prozesse genutzt werden

Ergänzung zur Vorbereitungsdatei. Hier geht es nicht um Apps, sondern um die betriebswirtschaftliche Begründung: Welches Problem löst der Prozess, wer löst ihn aus, wann im Zyklus findet er statt, was passiert ohne ihn, woran misst man ihn.

## 0. Der gemeinsame Rahmen: Purchase-to-Pay und Periodenabschluss

Alle fünf Themen hängen an einer Kette: Bedarf → Bestellung → Leistung (Wareneingang oder Leistungserfassung) → Rechnung → Zahlung. Finance interessiert sich für zwei Fragen entlang dieser Kette:

1. **Zahlen wir nur, was bestellt und erhalten wurde?** Das ist die Kontrollfrage. Sie wird bei jeder Rechnung beantwortet (Three-Way-Match) und nachgelagert bei der Klärung offener Differenzen (GR/IR-Monitoring).
2. **Steht der Aufwand in der richtigen Periode?** Das ist die Abgrenzungsfrage. Sie wird am Periodenende beantwortet: Wareneingänge ohne Rechnung und Rechnungen ohne Wareneingang (GR/IR-Umgliederung), Leistungen ohne beides (PO-Accruals), erfasste, aber nicht freigegebene Leistungen (SES-Accruals).

Die Bestellung ist der Dreh- und Angelpunkt. Sie liefert Preis, Menge, Kontierung, Laufzeit und Verantwortlichen. Jeder der fünf Prozesse nutzt die Bestellung als Referenz, deshalb ist „Bestellung vor Rechnung“ (No PO, no pay) die wichtigste organisatorische Voraussetzung für alle fünf.

## 1. PO-basierte Rechnungserfassung

**Business-Kontext.** Die Kreditorenbuchhaltung erhält täglich Lieferantenrechnungen für Materialien, Verbrauchsgüter und Dienstleistungen, die der Einkauf bestellt hat. Die Rechnung muss geprüft, kontiert, mit Steuer versehen, gebucht und zur Zahlung freigegeben werden.

**Warum mit Bestellbezug.**
- **Kontierung ist bereits entschieden.** Der Einkauf oder der Anforderer hat bei der Bestellung festgelegt, ob es Bestand oder Aufwand ist und welche Kostenstelle, welcher Auftrag oder welches Projekt belastet wird. Die Buchhaltung muss das nicht noch einmal interpretieren.
- **Prüfung statt Erfassung.** Das System schlägt Positionen, Mengen, Preise und Steuerkennzeichen aus der Bestellung und den Wareneingängen vor. Die Arbeit des Buchhalters verschiebt sich vom Abtippen zum Abgleichen.
- **Verantwortung bleibt beim Fachbereich.** Weicht die Rechnung ab, geht die Klärung an den, der bestellt hat. Die Buchhaltung ist nicht mehr die Stelle, die Preise mit Lieferanten verhandelt.
- **Auswertbarkeit.** Bestellbezug verbindet Einkaufsdaten (Lieferant, Warengruppe, Einkäufer) mit Finanzdaten (Zahlungsziele, Skonto, DPO). Ohne Bezug sind Spend-Analysen und Lieferantenbewertung lückenhaft.

**Was ohne den Prozess passiert.** Freie Rechnungen mit manueller Kontierung, Rückfragen per Mail an den Fachbereich, doppelte Erfassung derselben Rechnung, Zahlungen für nicht bestellte Leistungen, keine Verbindung zwischen Einkauf und Finanzbuchhaltung.

**Kennzahlen.** Anteil Rechnungen mit Bestellbezug, Durchlaufzeit Rechnungseingang bis Buchung, Anteil ohne manuellen Eingriff (Touchless Rate), Skontoausnutzung.

## 2. Three-Way-Match (Bestellung, Wareneingang, Rechnung)

**Business-Kontext.** Jede Rechnung ist eine Zahlungsaufforderung eines Dritten. Bevor Geld abfließt, muss das Unternehmen sicherstellen, dass die Leistung bestellt war (Bestellung), tatsächlich erbracht wurde (Wareneingang oder freigegebenes Leistungserfassungsblatt) und zum vereinbarten Preis berechnet wird (Rechnung).

**Warum.**
- **Internes Kontrollsystem.** Der Abgleich ist eine automatisierte, dokumentierte Kontrolle. Sie ersetzt die manuelle Prüfung „stimmt der Preis, war das geliefert“ und ist revisionssicher nachvollziehbar.
- **Funktionstrennung.** Besteller, Wareneingangsbucher und Rechnungsprüfer sind unterschiedliche Personen oder Rollen. Der Abgleich im System verbindet ihre drei Belege, ohne dass eine Person alle drei kontrolliert.
- **Betrugs- und Fehlerprävention.** Überhöhte Preise, Doppelrechnungen, Scheinrechnungen und Rechnungen vor Leistung werden erkannt, weil der dritte Beleg fehlt oder abweicht.
- **Zahlung ohne Verzögerung bei Übereinstimmung.** Wenn alle drei Belege passen, gibt es keinen Grund für eine manuelle Freigabe. Die Rechnung fließt direkt in den Zahllauf. Das ist die Grundlage für Skontoausnutzung.
- **Toleranzen als bewusste Entscheidung.** Nicht jede Abweichung lohnt eine Klärung. Das Unternehmen legt fest, bis zu welcher Preis- oder Mengenabweichung automatisch gebucht wird. Das ist eine Risiko-Kosten-Abwägung, keine Systemfrage.

**Zwei-Wege-Abgleich als Sonderfall.** Für Leistungen ohne physischen Eingang (Lizenzen, Abonnements, Pauschalen) gibt es keinen Wareneingang. Hier wird nur Bestellung gegen Rechnung geprüft. Die Kontrolle „Leistung erbracht“ verschiebt sich auf die Bestellfreigabe oder auf die Rechnungsfreigabe im Workflow.

**Was ohne den Prozess passiert.** Jede Rechnung braucht eine manuelle Unterschrift, Abweichungen werden erst beim Jahresabschluss oder durch den Lieferanten bemerkt, Skonto geht verloren, weil die Freigabe zu lange dauert.

**Kennzahlen.** Anteil automatisch freigegebener Rechnungen, Anzahl und Alter gesperrter Rechnungen, Anteil Preis- und Mengenabweichungen je Lieferant.

## 3. GR/IR-Monitoring

**Business-Kontext.** Das WE/RE-Verrechnungskonto (GR/IR) ist das Bindeglied zwischen Logistik und Finanzbuchhaltung. Jeder Wareneingang bucht darauf, jede Rechnung dagegen. Stimmen Mengen und Werte überein, ist das Konto für die Bestellposition ausgeglichen. In der Praxis bleiben Salden stehen: Teillieferungen ohne Rest, Rechnungen für nicht gelieferte Ware, Lieferanten, die nie eine Rechnung schicken, Bestellungen, die auslaufen.

**Warum.**
- **Bilanzrichtigkeit.** Der Saldo des GR/IR-Kontos ist zum Stichtag entweder eine Verbindlichkeit (geliefert, nicht berechnet) oder eine Forderung bzw. Anzahlung (berechnet, nicht geliefert). Unklare Altsalden verfälschen die Bilanz und sind ein Standardthema der Abschlussprüfung.
- **Prozessqualität in Einkauf und Logistik.** Jeder offene Saldo hat eine operative Ursache: fehlender Wareneingang, fehlende Rechnung, falsche Menge, nicht geschlossene Bestellung. Das Monitoring macht diese Ursachen sichtbar und ordnet sie einem Verantwortlichen zu.
- **Altersstruktur.** Je älter der Saldo, desto teurer die Klärung. Monatliches Monitoring hält die Klärungsfälle jung.
- **Nachvollziehbarkeit.** Status, Bearbeiter, Ursache und Notiz je Fall sind dokumentiert. Das ersetzt die Excel-Liste mit Kommentarspalte und ist später die Grundlage für die ML-Vorschläge.

**Rollen.** Die Buchhaltung erkennt und verteilt die Fälle, der Einkauf klärt mit dem Lieferanten oder schließt die Bestellung, die Logistik bucht fehlende Wareneingänge nach. Die Entscheidung „abschreiben“ liegt bei Finance mit Betragsgrenze.

**Zeitpunkt.** Laufend oder wöchentlich für große Beträge, in jedem Fall vor dem Monatsabschluss. Die Umgliederung zum Stichtag bucht das Ergebnis in die Bilanz, der Monitor sorgt dafür, dass das Ergebnis erklärbar ist.

**Was ohne den Prozess passiert.** Jahresend-Aktionen mit Listen über tausende Positionen, pauschale Abschreibungen, Diskussionen mit dem Wirtschaftsprüfer, keine Lernkurve im Einkauf.

**Kennzahlen.** Anzahl und Betrag offener GR/IR-Positionen nach Alter, Anteil WE-Überschuss zu RE-Überschuss, Durchlaufzeit von Erkennung bis Klärung, Anteil abgeschriebener Restbeträge.

## 4. ML-gestütztes GR/IR-Monitoring

**Business-Kontext.** Die Fälle im GR/IR-Monitor wiederholen sich: derselbe Lieferant liefert regelmäßig unvollständig, dieselbe Warengruppe wird regelmäßig vor Lieferung berechnet, dieselbe Abteilung ist zuständig. Ein erfahrener Buchhalter erkennt das Muster nach Sekunden. Ein neuer Mitarbeiter oder ein Shared Service Center braucht Monate.

**Warum.**
- **Erfahrung wird übertragbar.** Das Modell lernt aus den dokumentierten Entscheidungen (Status, Priorität, Ursache, Abteilung, Bearbeiter) und schlägt sie für neue Fälle vor. Routinefälle werden vorbelegt, der Mensch bestätigt.
- **Konsistenz.** Gleiche Fälle werden gleich behandelt, unabhängig davon, wer gerade die Liste bearbeitet.
- **Kapazität.** Die Bearbeitungszeit pro Fall sinkt, die Buchhaltung kann sich auf die Ausnahmen konzentrieren.

**Voraussetzungen, die man dem Kunden sagen muss.** Das Modell braucht Betriebsdaten, konkret mindestens 100 manuell bearbeitete Fälle mit gepflegter Ursache. Es ist also kein Go-live-Thema, sondern eine Ausbaustufe nach einigen Monaten. Die Qualität der Vorschläge hängt direkt an der Disziplin bei Status und Ursache in der Anfangsphase. Die Vorschläge sind Vorschläge, die Entscheidung bleibt beim Bearbeiter.

**Kennzahlen.** Übernahmequote der Vorschläge, Bearbeitungszeit pro Fall vor und nach Aktivierung.

## 5. Bestellabgrenzungen (PO-Accruals)

**Business-Kontext.** Dienstleistungen und Verbrauchsleistungen mit Laufzeit, etwa Beratung, Wartung, Marketingkampagnen, Mieten von Geräten, werden bestellt und über Wochen oder Monate erbracht. Die Rechnung kommt am Ende oder in Raten. Am Monatsende ist ein Teil der Leistung erbracht, aber weder Wareneingang noch Rechnung gebucht.

**Warum.**
- **Periodengerechte Gewinnermittlung.** Aufwand gehört in die Periode, in der die Leistung empfangen wurde, nicht in die Periode der Rechnung. Das gilt nach HGB (Realisations- und Imparitätsprinzip, Abgrenzung) ebenso wie nach IFRS (Accrual Basis).
- **Verlässliches Monatsergebnis.** Ohne Abgrenzung schwankt das Ergebnis mit dem Rechnungseingang. Controlling kann Budgetabweichungen nicht beurteilen, weil Kosten fehlen oder gehäuft auftreten.
- **Nachvollziehbare Grundlage.** Die Abgrenzung wird aus der Bestellung abgeleitet (geplante Kosten, Laufzeit, Fertigstellungsgrad), nicht aus einer Schätzung in Excel. Jede Buchung ist auf eine Bestellposition zurückführbar.
- **Vier-Augen-Prinzip mit Schwellen.** Kleine Beträge laufen automatisch, mittlere werden systemseitig plausibilisiert, große werden vom Einkäufer (kennt den Leistungsstand) und vom Controlling (verantwortet das Ergebnis) geprüft.
- **Automatischer Storno.** Die Abgrenzung wird in der Folgeperiode aufgelöst. Kommt dann die Rechnung oder der Wareneingang, ist der Aufwand nicht doppelt.

**Abgrenzung zu anderen Instrumenten.** Lagermaterial wird nicht abgegrenzt, weil der Wareneingang bereits bewertet bucht. Rückstellungen für ungewisse Verbindlichkeiten ohne Bestellung bleiben manuell. Rechnungen vor Leistung (Vorauszahlung) sind Deferrals; die Accrual Engine kann sie optional mitführen.

**Was ohne den Prozess passiert.** Controller sammeln per Mail Schätzungen aus den Fachbereichen, buchen Sammelabgrenzungen, Stornos werden vergessen, der Abschluss dauert länger, Prüfer fragen nach der Herleitung.

**Kennzahlen.** Anteil abgegrenzter Bestellungen am Bestellvolumen mit Laufzeit, Abweichung Abgrenzung zu späterer Rechnung, Anzahl manueller Abgrenzungsbuchungen außerhalb der Engine.

## 6. Abgrenzung auf Basis von Leistungserfassungsblättern (SES-Accruals)

**Business-Kontext.** Bei Lean Services (Reinigung, Zeitarbeit, Instandhaltung, Beratung nach Aufwand) erfasst der Lieferant oder der Fachbereich die erbrachte Leistung in einem Leistungserfassungsblatt. Der Aufwand wird erst gebucht, wenn der Fachbereich das Blatt freigibt. Diese Freigabe passiert oft erst Tage nach Monatsende, weil der Verantwortliche die Stunden prüft oder im Urlaub ist.

**Warum.**
- **Die Leistung ist bekannt, nur die Freigabe fehlt.** Anders als bei PO-Accruals muss nichts geschätzt werden. Der erfasste Betrag ist die beste verfügbare Information über den Aufwand der Periode.
- **Keine Lücke zwischen Logistik und Finance.** Ohne Abgrenzung erscheinen die Kosten im Folgemonat, obwohl die Leistung dokumentiert im Vormonat lag. Besonders bei Zeitarbeit und Fremdpersonal sind das große, regelmäßig wiederkehrende Beträge.
- **Disziplin im Fachbereich bleibt gefordert.** Die Abgrenzung ist ein Sicherheitsnetz, kein Ersatz für fristgerechte Freigabe. Je besser die Freigabedisziplin, desto kleiner der Abgrenzungsbetrag.

**Zusammenspiel mit PO-Accruals.** Dieselbe Bestellung könnte beide Abgrenzungen auslösen. Die Transferpriorität entscheidet, dass die SES-basierte Abgrenzung Vorrang hat, weil sie auf tatsächlichen Daten statt auf Planwerten beruht.

**Was ohne den Prozess passiert.** Fremdpersonalkosten springen zwischen Monaten, der Fachbereich wird für verspätete Freigaben nicht sichtbar, Controlling korrigiert manuell.

**Kennzahlen.** Betrag nicht freigegebener Leistungserfassungsblätter zum Stichtag, Freigabedauer nach Erfassung, Anteil abgegrenzter zu insgesamt erfassten Leistungen.

## 7. Zusammenfassung in einem Satz je Prozess

| Prozess | Löst dieses Problem | Ausgelöst durch | Zeitpunkt |
|---|---|---|---|
| PO-Rechnungserfassung | Rechnungen schnell und richtig kontiert buchen | Rechnungseingang | täglich |
| Three-Way-Match | Nur bezahlen, was bestellt und erhalten wurde | Rechnungsbuchung | je Rechnung |
| GR/IR-Monitoring | Offene Differenzen zwischen Lieferung und Rechnung klären | Saldo auf GR/IR-Konto | laufend, vor Abschluss |
| ML-Unterstützung | Wiederkehrende Fälle schneller und einheitlicher entscheiden | Historie bearbeiteter Fälle | nach Aufbau der Historie |
| PO-Accruals | Aufwand laufender Leistungen in die richtige Periode bringen | Freigegebene Bestellung mit Laufzeit | Monatsabschluss |
| SES-Accruals | Erfasste, nicht freigegebene Leistungen periodengerecht buchen | Eingereichtes Leistungserfassungsblatt | Monatsabschluss |
