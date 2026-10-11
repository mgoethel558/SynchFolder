# Prozesskontext: Warum Collections & Dispute Management?

Rein fachliche Erklärung der Prozesse aus Workshop 4: Welches Geschäftsproblem lösen sie, wer nutzt sie wann, und wie greifen sie ineinander. Ohne App-Klickfolgen; die stehen in `Workshop4_Vorbereitung_Collections_Dispute.md`.

---

## 1. Einordnung: Der letzte Abschnitt von Order-to-Cash

Order-to-Cash endet nicht mit der Rechnung, sondern mit dem Geldeingang. Zwischen Rechnungsstellung und Zahlung liegt der Abschnitt, in dem das Unternehmen Kapital gebunden hat, aber keinen Einfluss mehr über den Verkaufsprozess ausübt. Genau hier setzen die vier Prozesse des Workshops an:

| Abschnitt | Frage des Unternehmens | Prozess |
|---|---|---|
| Rechnung ist fällig, Kunde zahlt nicht | Wie erinnern wir standardisiert und rechtssicher? | Mahnwesen (J59) |
| Kunde zahlt trotz Mahnung nicht oder ist zu wichtig für Standardmahnungen | Wen sprechen wir persönlich an, in welcher Reihenfolge, mit welchem Ergebnis? | Collections Management (BFC/7MA) |
| Kunde zahlt nicht oder nicht vollständig, weil er die Rechnung bestreitet | Wie klären wir den Streitfall schnell, nachvollziehbar und über Abteilungsgrenzen hinweg? | Dispute Management (BFC/7MA) |
| Forderung ist gefährdet oder uneinbringlich | Wie bilden wir das Risiko in der Bilanz ab und wann buchen wir aus? | Wertberichtigung und Ausbuchung (2PD) |

Alle vier Prozesse arbeiten auf derselben Datenbasis: den offenen Posten der Debitorenbuchhaltung (FI-AR). Sie unterscheiden sich darin, **wie viel menschliche Aufmerksamkeit** pro Kunde eingesetzt wird: Das Mahnwesen ist vollautomatisch und unpersönlich, Collections Management ist personalisiert und priorisiert, Dispute Management ist fallbezogen und abteilungsübergreifend.

---

## 2. Das Grundproblem: Forderungen werden nicht von allein bezahlt

**Warum das Thema Geld kostet.** Jede überfällige Forderung bindet Liquidität, die das Unternehmen sonst für Investitionen oder Schuldentilgung nutzen könnte, und erhöht das Ausfallrisiko: Je länger eine Forderung offen ist, desto geringer ist die Wahrscheinlichkeit, dass sie überhaupt bezahlt wird. Die Kennzahl dafür ist Days Sales Outstanding (DSO): die durchschnittliche Zeit zwischen Rechnung und Zahlung. Eine Verbesserung um wenige Tage entspricht bei größeren Umsätzen schnell Millionen an freigesetztem Working Capital.

**Warum Kunden nicht zahlen.** In der Praxis gibt es drei sehr unterschiedliche Ursachen, die unterschiedliche Reaktionen verlangen:

1. **Vergessen oder Prozessfehler beim Kunden:** Rechnung nicht angekommen, nicht freigegeben, falsche Adresse. Hier reicht eine Erinnerung. Das ist der Fall für das Mahnwesen.
2. **Zahlungsunwilligkeit oder Liquiditätsprobleme:** Der Kunde zögert bewusst hinaus oder kann nicht zahlen. Hier braucht es persönlichen Kontakt, Verhandlung, Zahlungsvereinbarungen und Risikoeinschätzung. Das ist der Fall für Collections Management.
3. **Berechtigter oder unberechtigter Einwand:** Falscher Preis, falsche Menge, beschädigte Ware, nicht erbrachte Leistung, fehlende Gutschrift. Der Kunde zahlt gar nicht oder kürzt den Betrag. Hier muss intern geklärt werden, ob der Einwand stimmt. Das ist der Fall für Dispute Management.

Ein Unternehmen, das nur mahnt, behandelt alle drei Fälle gleich. Es verärgert gute Kunden mit berechtigten Einwänden, verschwendet Mahnstufen bei zahlungsunfähigen Kunden und erkennt Risiken zu spät.

---

## 3. Mahnwesen: Der automatisierte Grundschutz

**Warum.** Das Mahnwesen stellt sicher, dass kein überfälliger Posten unbeachtet bleibt, ohne dass jemand einzelne Kunden ansehen muss. Es ist außerdem die rechtliche Grundlage für Verzug: Mahnstufen, Fristen und Mahngebühren dokumentieren, dass der Kunde in Verzug gesetzt wurde.

**Business-Kontext.** Jeder Kunde erhält im Stammsatz ein Mahnverfahren. Das Verfahren legt fest, nach wie vielen Tagen welche Mahnstufe mit welchem Text erreicht wird. Der Mahnlauf wertet regelmäßig alle überfälligen Posten aus, ermittelt je Kunde die höchste erreichte Stufe und erzeugt die Mahnschreiben. Der Sachbearbeiter prüft nur noch den Vorschlag und sperrt Einzelfälle.

**Typische Ausprägungen.**
- Standardverfahren mit mehreren Stufen in festen Intervallen (im Workshop: alle 14 Tage, 4 Stufen) für die breite Masse der Kunden.
- Sanftes Verfahren mit einer Zahlungserinnerung erst 30 Tage nach Rechnung für Großkunden oder öffentliche Auftraggeber.
- Kein Mahnverfahren für Konzerngesellschaften oder Kunden mit Lastschrift.

**Grenzen.** Das Mahnwesen weiß nichts über den Grund der Nichtzahlung. Es kann einen Kunden nicht nach Wichtigkeit priorisieren, kein Gespräch dokumentieren und keine Zusage nachhalten. Deshalb ist es die Basis, nicht die Lösung.

**Schnittstelle zu den anderen Prozessen.** Posten mit offenem Dispute Case oder laufendem Zahlungsversprechen werden aus dem Mahnlauf ausgeklammert. Das verhindert, dass ein Kunde gemahnt wird, mit dem die Buchhaltung gerade im Gespräch ist. Das ist der wichtigste Grund, warum Collections und Dispute Management im selben System laufen müssen wie das Mahnwesen.

---

## 4. Collections Management: Vom reaktiven Mahnen zum gesteuerten Forderungsmanagement

**Warum.** Persönlicher Kontakt ist das wirksamste Mittel, um Zahlungen zu beschleunigen, aber er ist teuer. Ein Collections-Team kann pro Tag nur eine begrenzte Zahl von Kunden kontaktieren. Collections Management beantwortet deshalb die Frage: **Welche Kunden soll das Team heute kontaktieren, damit die Wirkung auf Liquidität und Risiko am größten ist?**

**Business-Kontext.** Der Prozess lohnt sich, wenn mindestens eine der folgenden Bedingungen erfüllt ist:
- Viele Kunden mit überfälligen Posten, sodass niemand mehr den Überblick über Excel-Listen behält.
- Hoher Anteil weniger Großkunden am Forderungsbestand, bei denen eine Standardmahnung die Beziehung belasten würde und ein Anruf beim Einkauf mehr bringt.
- Mehrere Mitarbeiter, die sich die Kunden teilen, mit Vertretungsbedarf und dem Wunsch nach einheitlicher Dokumentation.
- Management, das wissen will, wie viel überfälliges Volumen das Team tatsächlich "bewegt" und welche Zusagen eingehalten werden.

**Wie der Prozess funktioniert, fachlich.**
1. **Übertragung:** Jede Nacht werden die offenen Posten aus der Debitorenbuchhaltung in das Collections Management übernommen.
2. **Bewertung:** Jeder Kunde wird gegen die Regeln seiner Collections-Strategie geprüft: Wie viel ist überfällig, wie lange, gibt es große Einzelposten, offene oder gebrochene Zahlungsversprechen, wann war der letzte Kontakt? Jede zutreffende Regel bringt Punkte.
3. **Priorisierung:** Aus den Punkten wird eine Priorität abgeleitet. Kunden ohne Punkte erscheinen nicht.
4. **Arbeitsliste:** Jeder Spezialist bekommt die Kunden seiner Gruppe, sortiert nach Priorität. Das ist die Worklist.
5. **Kontakt:** Der Spezialist ruft an oder schreibt. Das Ergebnis wird als strukturiertes Objekt festgehalten: Zahlungsversprechen, Wiedervorlage, Dispute Case, Korrespondenz, Kontaktnotiz.
6. **Nachhalten:** Das System prüft automatisch, ob ein Zahlungsversprechen eingehalten wurde. Gebrochene Versprechen fließen wieder in die Bewertung ein.
7. **Steuerung:** Der Manager sieht Fortschritt, offene Versprechen und Auslastung je Spezialist.

**Organisatorische Voraussetzung.** Collections Management setzt eine eigene Organisation voraus, die nicht mit Buchungskreisen identisch sein muss: Segmente (zum Beispiel Inland/Ausland oder Geschäftsbereiche), Gruppen (Teams mit einer gemeinsamen Vorgehensweise) und Spezialisten. Jeder Kunde wird über ein Profil in diese Struktur eingehängt. Das ist der Teil, über den der Kunde im Workshop entscheiden muss, weil er seine Teamstruktur widerspiegelt.

**Nutzenargument gegenüber dem Mahnwesen.** Das Mahnwesen erzeugt Briefe; Collections Management erzeugt Gespräche und Zusagen. Die Kennzahlen dafür sind: eingehaltene Zahlungsversprechen, überfälliges Volumen im Zeitverlauf je Spezialist, Anzahl Kontakte bis Zahlung.

---

## 5. Worklist: Tagessteuerung des Teams

**Warum eine Arbeitsliste statt einer Kundenliste.** Eine Liste aller überfälligen Kunden hilft nicht; sie ist zu lang. Die Worklist ist eine **Reihenfolge**, die aus Risiko- und Betragslogik entsteht und jeden Tag neu berechnet wird. Der Spezialist muss nicht entscheiden, wen er anruft, sondern nur, was er mit dem Kunden vereinbart.

**Business-Kontext.**
- **Für den Spezialisten:** Morgens die Liste öffnen, von oben abarbeiten, jeden Kontakt mit Ergebnis abschließen. Kunden mit Wiedervorlage oder laufendem Versprechen verschwinden automatisch bis zum vereinbarten Datum.
- **Für die Vertretung:** Bei Urlaub oder Krankheit sieht der Vertreter dieselbe Liste mit derselben Historie. Kein Wissensverlust.
- **Für den Manager:** Alle Kunden mit überfälligen Posten, wer zuständig ist, wo niemand zuständig ist, wie weit das Team ist. Kunden können umverteilt werden, wenn jemand überlastet ist.
- **Für die Massenbearbeitung:** Für Kunden mit kleinen Beträgen reicht eine Serien-Korrespondenz aus der Liste statt Einzelkontakt.

**Was die Worklist nicht ist.** Sie ist keine To-do-Liste, die man manuell pflegt. Sie ist ein berechnetes Ergebnis. Wer die Reihenfolge ändern will, ändert die Strategie, nicht die Liste.

---

## 6. Zahlungsversprechen, Wiedervorlage, Kontaktdokumentation

Diese drei Objekte machen aus einem Telefonat einen nachvollziehbaren Prozessschritt.

**Zahlungsversprechen (Promise to Pay).** Der Kunde sagt zu, einen Betrag bis zu einem Datum zu zahlen. Das Versprechen hat drei Wirkungen: Der Posten wird nicht gemahnt, solange das Versprechen läuft; das System prüft am Fälligkeitstag automatisch gegen den Zahlungseingang, ob es eingehalten wurde; ein gebrochenes Versprechen erhöht die Priorität des Kunden. Damit wird das Zahlungsverhalten des Kunden messbar: Ein Kunde, der regelmäßig Versprechen bricht, ist ein Risikokunde, unabhängig von der Bonitätsauskunft.

**Wiedervorlage (Resubmission).** Der Kontakt hat kein Ergebnis gebracht, aber es gibt einen Termin: Der Ansprechpartner ist bis Montag im Urlaub, die Rechnung wird intern noch freigegeben. Die Wiedervorlage nimmt den Kunden bis zum Datum von der Liste, damit der Spezialist seine Zeit auf andere Kunden verwendet.

**Kontaktdokumentation.** Jeder Kontakt wird mit Ergebnis, Ansprechpartner und Notiz festgehalten. Das dient der Vertretung, der Eskalation (Was wurde dem Kunden schon zugesagt?) und im Streitfall der Beweisführung. Die Zusammenfassung kann dem Kunden als E-Mail geschickt werden, was die Verbindlichkeit der Zusagen erhöht.

---

## 7. Dispute Management: Reklamationen als Cash-Blocker

**Warum.** Ein bestrittener Posten wird nicht bezahlt, egal wie oft gemahnt wird. Jeder Tag, den die interne Klärung dauert, verlängert den DSO. Gleichzeitig ist die Klärung abteilungsübergreifend: Die Buchhaltung sieht den Abzug, der Vertrieb kennt die Preisabsprache, die Logistik weiß, ob die Lieferung vollständig war, der Kundenservice hat die Reklamation aufgenommen. Ohne Prozess läuft das über E-Mails und bleibt liegen.

**Business-Kontext: Wo Streitfälle entstehen.**
- **Beim Zahlungseingang:** Der Kunde zahlt weniger als den Rechnungsbetrag und gibt auf dem Zahlungsavis einen Grund an (Skonto trotz Fristüberschreitung, Mengendifferenz, Rücksendung). Der Restposten ist der klassische Auslöser; er ist oft klein, aber zahlreich. Hier lohnt sich die automatische Anlage.
- **Im Kundenkontakt:** Der Spezialist ruft an und erfährt, dass der Kunde die Rechnung bestreitet. Der Dispute Case wird aus dem Gespräch heraus angelegt.
- **Im Kundenservice oder Vertrieb:** Die Reklamation kommt per Mail oder Telefon, bevor die Rechnung fällig ist.

**Was ein Dispute Case leistet.**
- Er hält den strittigen Betrag, den Grund, die Priorität und die beteiligten Belege an einer Stelle zusammen.
- Er hat einen verantwortlichen Bearbeiter und einen Koordinator, der zuweist und eskaliert. Damit ist klar, wer am Zug ist.
- Er dokumentiert Notizen, Anhänge und Korrespondenz mit dem Kunden.
- Er sperrt den Posten für das Mahnwesen. Der Kunde wird nicht für etwas gemahnt, das gerade geprüft wird.
- Er liefert Auswertungen nach Grund und Ursache. Das ist der strategische Nutzen: Wenn 40 Prozent der Streitfälle Preisdifferenzen sind, liegt das Problem in der Preispflege, nicht in der Buchhaltung.

**Rollenmodell.** Der Koordinator ist typischerweise in der Debitorenbuchhaltung und verteilt. Der Bearbeiter kann in jeder Fachabteilung sitzen. Der Kunde muss im Workshop entscheiden, ob Vertrieb und Logistik direkt im System arbeiten oder ob die Buchhaltung stellvertretend pflegt.

---

## 8. Dispute-Lösung: Entscheidung und Konsequenzen

Jeder Dispute Case endet mit einer von drei Entscheidungen, die jeweils eine buchhalterische Konsequenz haben:

| Entscheidung | Bedeutung | Konsequenz |
|---|---|---|
| **Berechtigt** | Der Kunde hat recht. | Gutschrift über den strittigen Betrag. Mit dem Ausgleich der Rechnung schließt der Fall automatisch. Der Grund wird für die Ursachenanalyse festgehalten. |
| **Nicht berechtigt** | Der Kunde hat unrecht. | Die Forderung wird wieder eingetrieben: Mahnsperre fällt, Kunde kommt zurück auf die Worklist, der Spezialist konfrontiert ihn mit dem Ergebnis. |
| **Teilweise berechtigt** | Die Wahrheit liegt dazwischen. | Teilgutschrift, Rest wird eingetrieben. |
| **Abschreibung** | Der Betrag ist zu klein für den Aufwand oder nicht mehr durchsetzbar. | Ausbuchung als Aufwand, meist mit Betragsgrenzen und Freigabe. Automatisierbar für eskalierte Fälle. |
| **Fehlanlage** | Der Fall hätte nicht angelegt werden dürfen. | Storno (Void), bleibt nachvollziehbar. |

**Warum die automatische Schließung wichtig ist.** Der Fall schließt sich, sobald die Buchhaltung den Posten ausgeglichen hat. Niemand muss daran denken, den Fall zu schließen, und die Fallstatistik stimmt mit der Buchhaltung überein.

**Kennzahlen.** Durchlaufzeit je Fall, offene Fälle nach Alter, strittiges Volumen im Verhältnis zum Forderungsbestand, Anteil berechtigter Fälle je Grund. Die letzte Kennzahl ist die wertvollste: Sie zeigt, wo das Unternehmen selbst Fehler macht, die Cash kosten.

---

## 9. Collections-Strategie: Risikopolitik in Regeln

**Warum konfigurieren statt Standard nehmen.** Die Strategie ist die Stelle, an der das Unternehmen festlegt, was ihm wichtig ist. Zwei Unternehmen mit demselben Forderungsbestand können völlig unterschiedliche Prioritäten haben:
- Ein Unternehmen mit wenigen Großkunden gewichtet große Einzelposten hoch und will frühen Kontakt vor Fälligkeit.
- Ein Unternehmen mit vielen Kleinkunden gewichtet die Summe der überfälligen Posten und die Tage seit letztem Kontakt, um systematisch durchzuarbeiten.
- Ein Unternehmen mit Bonitätsinformationen gewichtet die Risikoklasse, damit gefährdete Kunden zuerst drankommen.

**Wie die Strategie fachlich aufgebaut ist.**
- **Regeln:** Jede Regel ist eine Frage an den Kunden (Ist mehr als X seit mehr als Y Tagen überfällig? Gibt es ein gebrochenes Versprechen? War der letzte Kontakt vor mehr als Z Tagen?). Die Regeln sind vorgefertigt; das Unternehmen wählt aus und setzt die Schwellenwerte.
- **Gewichte:** Jede Regel bringt Punkte. Die Punktzahl drückt die relative Wichtigkeit aus.
- **Priorität:** Die Summe der Punkte im Verhältnis zum möglichen Maximum ergibt die Prioritätsstufe. Damit ist die Reihenfolge auf der Worklist bestimmt.
- **Zeitraster:** Überfälligkeits- und Fälligkeitsperioden steuern, wie Beträge in der Liste gruppiert werden.
- **Zusammenspiel mit dem Mahnwesen:** Die Strategie legt fest, ob Mahnstufen in die Bewertung eingehen.

**Warum mehrere Strategien.** Jede Gruppe hat genau eine Strategie. Wer Großkunden und Kleinkunden unterschiedlich behandeln will, braucht zwei Gruppen mit zwei Strategien. Das ist die eigentliche Designentscheidung im Workshop: Wie viele unterschiedliche "Vorgehensweisen" gibt es im Forderungsmanagement des Kunden?

**Wann Strategien angepasst werden.** Strategien sind keine einmalige Konfiguration. Wenn das Team feststellt, dass Kunden mit gebrochenen Versprechen zu spät auf der Liste erscheinen, wird die Gewichtung erhöht. Die Änderung wirkt beim nächsten nächtlichen Lauf.

---

## 10. Automatisierung mit Collections and Dispute Automation (7MA)

**Warum es diese Variante gibt.** Bei hohem Volumen sind die manuellen Schritte des klassischen Prozesses der Engpass: Dispute Cases von Hand anlegen und zuweisen, Kunden Gruppen zuordnen, Eskalationen beobachten. 7MA verlagert diese Entscheidungen in ein Regelwerk, das automatisch ausführt:
- Restposten mit einem bestimmten Zahlungsdifferenzgrund werden ohne Zutun zu Disputes mit passendem Grund und zuständigem Bearbeiter.
- Kunden werden anhand von Merkmalen automatisch Teams und Priorisierungsregeln zugeordnet.
- Disputes, die zu lange offen sind, werden automatisch eskaliert.
- Mahn- und Zahlsperren werden regelbasiert gesetzt und aufgehoben.

**Business-Kontext für die Entscheidung.** 7MA lohnt sich, wenn das Volumen an Streitfällen hoch ist, die Zuordnungslogik klar beschreibbar ist und jemand im Fachbereich die Regeln pflegen kann. BFC ist die richtige Wahl, wenn das Team kleiner ist, Einzelfallentscheidungen überwiegen und die Standard-Auswertungen ausreichen. Beide Varianten setzen eine Zusatzlizenz voraus; sie sind nicht parallel im Einsatz.

---

## 11. Wertberichtigung und Ausbuchung: Die bilanzielle Folge

**Warum.** Nicht jede Forderung wird bezahlt. Die Rechnungslegung verlangt, dass dieses Risiko im Abschluss abgebildet wird, bevor der Ausfall eintritt. Unter IFRS 9 geschieht das über erwartete Kreditverluste (Expected Credit Loss): Jede Forderung wird je nach Überfälligkeit mit einem Prozentsatz wertberichtigt, auch wenn der Kunde noch nicht ausgefallen ist. Nach HGB entspricht dem die Pauschal- und Einzelwertberichtigung.

**Business-Kontext.**
- **Periodisch zum Abschluss:** Ein Bewertungslauf wendet die Prozentsätze je Überfälligkeitsklasse auf alle offenen Posten an und bucht den Wertberichtigungsaufwand zum Stichtag. Die Buchung wird am Folgetag storniert, damit im nächsten Abschluss neu bewertet wird.
- **Analyse:** Die Buchhaltung sieht, welche Kunden und welche Altersklassen die Wertberichtigung treiben, und kann das an Collections zurückspielen.
- **Ausbuchung:** Ist eine Forderung endgültig uneinbringlich (Insolvenz, erfolglose Eintreibung, Verjährung), wird sie als Aufwand ausgebucht. Das Recht, den Betrag später doch noch einzuziehen, bleibt bestehen.

**Verbindung zu Collections und Dispute.** Je besser Collections und Dispute Management arbeiten, desto kleiner sind die alten Überfälligkeitsklassen und desto niedriger die Wertberichtigung. Die Wertberichtigung ist damit die finanzielle Messlatte für die Qualität des Forderungsmanagements.

---

## 12. Kennzahlen und Nutzenargumente für den Workshop

| Kennzahl | Was sie misst | Welcher Prozess sie beeinflusst |
|---|---|---|
| DSO (Days Sales Outstanding) | Durchschnittliche Zeit bis zum Zahlungseingang | Alle |
| Überfälliges Volumen nach Altersklasse | Wie viel ist wie lange überfällig | Mahnwesen, Collections |
| Collection Effectiveness | Anteil des überfälligen Volumens, das im Zeitraum eingetrieben wurde | Collections |
| Quote eingehaltener Zahlungsversprechen | Verlässlichkeit der Kundenzusagen | Collections |
| Durchlaufzeit Dispute Cases | Tage von Anlage bis Lösung | Dispute |
| Strittiges Volumen | Betrag, der wegen Streitfällen nicht eingetrieben werden kann | Dispute |
| Anteil berechtigter Streitfälle je Grund | Wo das Unternehmen selbst Fehler macht | Dispute, vorgelagerte Prozesse |
| Wertberichtigungs- und Ausbuchungsquote | Tatsächliche Verluste | Alle, 2PD |

**Nutzenargumente in einem Satz je Prozess.**
- Mahnwesen: Kein Posten bleibt unbeachtet, ohne dass jemand hinsieht.
- Collections Management: Das Team spricht jeden Tag mit den Kunden, bei denen es am meisten bringt.
- Worklist: Die Reihenfolge ist berechnet, nicht gefühlt; Vertretung ohne Wissensverlust.
- Dispute Management: Streitfälle werden schneller geklärt und zeigen, wo das Unternehmen Geld verliert.
- Strategie: Die Risikopolitik steht im System, nicht im Kopf einzelner Mitarbeiter.
- Wertberichtigung: Das Ausfallrisiko steht korrekt in der Bilanz, und die Buchhaltung sieht, wo es herkommt.

---

## 13. Welcher Baustein für welche Kundensituation

| Situation beim Kunden | Empfehlung |
|---|---|
| Wenige hundert Kunden, geringe Überfälligkeit, ein Sachbearbeiter | Mahnwesen mit zwei Verfahren, Dispute Cases manuell aus dem Kundenkontakt. Collections Management optional. |
| Viele Kunden, mehrere Sachbearbeiter, Überfälligkeit ist Thema im Management | Collections Management (BFC) mit einer Strategie je Kundengruppe, Dispute Management mit Koordinator in der Buchhaltung. |
| Hohes Volumen an Unterzahlungen und Abzügen (Handel, Konsumgüter) | Automatische Dispute-Anlage aus Restposten, Ursachenanalyse nach Grund. Bei sehr hohem Volumen 7MA prüfen. |
| Wenige Großkunden mit hohem Anteil am Bestand | Sanftes Mahnverfahren, Collections-Strategie mit Fokus auf Einzelposten und frühem Kontakt, Key-Account-Spezialisten. |
| Kreditversicherung oder Bonitätsprüfung im Einsatz | Risikoklasse als Strategiekriterium, Collections-Profil nur für kritische Risikoklassen. |
| Konzernabschluss nach IFRS | 2PD mit Provision Matrix verpflichtend einplanen, Wertberichtigungsschlüssel je Kundengruppe. |
