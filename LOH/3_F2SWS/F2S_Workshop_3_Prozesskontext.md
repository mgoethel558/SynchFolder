# F2S-Workshop 3 – Prozesskontext: Warum und wann die Prozesse genutzt werden

Rein prozessuale Erklärung ohne App-Details, als Grundlage für die Theorieteile der Folien. SAP S/4HANA Cloud Public Edition, Scope Items J59 (Accounts Receivable) und BD6 (Basic Credit Management).

---

## 0. Die Debitorenbuchhaltung im Unternehmen

**Aufgabe.** Die Debitorenbuchhaltung (Accounts Receivable, AR) bildet alle Forderungen des Unternehmens gegenüber Kunden ab: Sie entstehen mit der Leistung und der Rechnung, bestehen als offene Posten und enden mit dem Zahlungseingang, einer Gutschrift oder einer Ausbuchung. Der Forderungsbestand ist Vermögen in der Bilanz und zugleich die Quelle des Liquiditätszuflusses. Alles, was hier schlecht läuft, zeigt sich spät und teuer: Zahlungsverzug, Streitfälle, Wertberichtigungen, Forderungsausfälle.

**Prozesskette (Order-to-Cash aus Finance-Sicht).**

| Phase | Frage, die der Prozess beantwortet | Workshop |
|---|---|---|
| Kunde kennen | Mit wem machen wir Geschäfte, zu welchen Konditionen, mit welchem Risiko? | 3 |
| Forderung entstehen lassen | Wie kommt die Leistung korrekt, vollständig und zeitnah als Rechnung in die Bücher? | 3 |
| Forderung führen | Wie bleibt jeder offene Posten nachvollziehbar, fällig datiert und zuordenbar? | 3 |
| Geld einziehen | Wie wird die Zahlung erkannt, zugeordnet, ausgeglichen, wie wird gemahnt? | 4 |
| Risiko steuern | Wann liefern wir nicht mehr, wann berichtigen wir, wann schreiben wir ab? | 3 (Kredit), 4 (Wertberichtigung) |

Der Workshop 3 behandelt die ersten drei Phasen: Stammdaten, Rechnungsentstehung und Führung des offenen Postens, plus die Konfiguration, die diese Phasen trägt.

---

## 1. Debitorenstammdaten

### Warum es den Prozess gibt

Jede Rechnung, jede Zahlung, jede Mahnung und jede Kreditentscheidung greift auf den Kundenstamm zu. Der Stamm ist die einzige Stelle, an der das Unternehmen festlegt, **wer** der Kunde rechtlich ist (Name, Anschrift, Steuernummern), **wie** mit ihm abgerechnet wird (Zahlungsbedingung, Zahlweg, Bankverbindung, Rechnungsempfänger, Versandkanal) und **wer intern** zuständig ist (Sachbearbeiter, Mahnverfahren, Kreditanalyst). Fehler im Stamm vervielfachen sich: Eine falsche E-Mail-Adresse bedeutet, dass hundert Rechnungen nicht ankommen; eine falsche Zahlungsbedingung verschiebt die Fälligkeit und damit Liquidität und Mahnung.

### Geschäftlicher Kontext

- **Vertrieb und Buchhaltung teilen sich einen Kunden.** Der Vertrieb braucht Preis-, Liefer- und Fakturadaten, die Buchhaltung braucht Abstimmkonto, Zahlungs- und Mahndaten, das Kreditmanagement braucht Limit und Risikoklasse. Das Geschäftspartner-Modell bildet genau diese Sichten als Rollen auf einem Objekt ab. Es gibt keine doppelte Kundennummer mehr zwischen Vertrieb und Finance.
- **Steuerliche und rechtliche Pflichten.** USt-IdNr. und Steuerland entscheiden über Steuerkennzeichen und Meldungen (EU-Lieferungen, Zusammenfassende Meldung). Zertifikate und Identifikationsnummern sind in manchen Ländern Voraussetzung für Rechnungsstellung oder Zahlung.
- **Interne Kontrolle.** Wer Kunden anlegen oder Bankverbindungen ändern darf, ist eine klassische Kontrollfrage (Betrugsrisiko bei Gutschriften und Rückzahlungen). Deshalb ist die Trennung zwischen Anlage (Stammdaten-Team oder Vertrieb) und Nutzung (Buchhaltung) der Normalfall, optional mit Genehmigungsworkflow.
- **Auswertung.** Sachbearbeiter, Risikoklasse, Land und Kundengruppe sind die Dimensionen, nach denen das Unternehmen später Überfälligkeit, DSO und Mahnstufen auswertet. Was im Stamm nicht gepflegt ist, kann später nicht ausgewertet werden.

### Auslöser und Ablauf

1. Neukunde aus Vertrieb oder Vertrag: allgemeine Daten anlegen, Vertriebsbereich (Vertrieb), Buchungskreisdaten (Buchhaltung).
2. Änderung im Lebenszyklus: neue Bankverbindung, Adresswechsel, geänderte Zahlungsbedingung, Mahnsperre bei Streitfall, Kreditlimit nach Bonitätsprüfung.
3. Periodische Prüfung: Vollständigkeit (fehlende E-Mail, fehlendes Mahnverfahren), Dubletten, inaktive Kunden sperren oder löschvormerken.

### Kreditmanagement als Teil der Stammdaten (BD6)

**Warum.** Jede Lieferung auf Rechnung ist ein Kredit. Das Unternehmen entscheidet mit dem Kreditlimit, wie viel Obligo es je Kunde eingehen will, und mit der Risikoklasse, wie streng geprüft wird. Die Prüfung findet dort statt, wo das Risiko entsteht: im Kundenauftrag und in der Lieferung, nicht erst in der Buchhaltung.

**Kontext.** Basic Credit Management ist der Mittelweg zwischen „gar keine Prüfung“ und einer eigenen Kreditabteilung mit externen Ratings. Es rechnet offene Aufträge, Lieferungen, Fakturen und offene Posten zum Obligo zusammen, vergleicht mit dem Limit und sperrt bei Überschreitung. Die Entscheidung über die Sperre (freigeben oder ablehnen) wird dokumentiert, damit sie später prüfbar ist. Typische Nutzer: Unternehmen mit vielen Geschäftskunden, Lieferung auf Ziel, wiederkehrenden Aufträgen. Weniger relevant bei Vorkasse, Lastschrift oder wenigen Großkunden mit Vertrag.

**Ergebnis.** Keine Lieferung an Kunden, die ihr Limit überzogen haben oder überfällig sind, ohne bewusste Freigabe durch eine berechtigte Person.

---

## 2. Manuelle Kundenrechnung ohne Auftragsbezug

### Warum es den Prozess gibt

Der Normalfall ist die Rechnung aus dem Vertriebsprozess: Auftrag, Lieferung, Faktura, automatische Buchung. Es gibt aber immer Forderungen, hinter denen kein Vertriebsbeleg steht. Für diese braucht die Buchhaltung einen Weg, eine Forderung direkt zu buchen, inklusive Steuer, Fälligkeit, Erlöskontierung und Rechnungsdruck. Ohne diesen Weg würden solche Fälle außerhalb des Systems (Word-Rechnung, Excel-Liste) laufen und wären weder im Forderungsbestand noch im Mahnlauf noch in der Umsatzsteuer.

### Geschäftlicher Kontext, typische Fälle

- Weiterberechnung von Kosten (Reisekosten, Material, Schäden, Nebenkosten) an Kunden oder Partner.
- Mieten, Pachten, Wartungspauschalen ohne Vertriebsauftrag.
- Verkauf von Anlagevermögen oder Sonstigem außerhalb des Produktsortiments.
- Rechnungen aus Vorsystemen, für die (noch) keine Schnittstelle existiert.
- Korrekturen: Nachberechnung, manuelle Gutschrift, Umbuchung zwischen Kunden.
- Anzahlungsanforderungen vor der Leistung.

### Was der Prozess sicherstellt

- **Vollständigkeit der Erlöse und der Umsatzsteuer**: Jede Forderung landet auf dem Kundenkonto, dem Erlöskonto und der Steuerkontierung, in der richtigen Periode.
- **Fälligkeitslogik**: Über Basisdatum und Zahlungsbedingung wird das Nettofälligkeitsdatum festgelegt. Daran hängen Mahnung, Zinsen, Liquiditätsplanung und DSO.
- **Ergebnisrechnung**: Erlöse werden einem Ergebnisobjekt (Kunde, Produkt, Region, Profit Center) zugeordnet. Deshalb erzwingt das System die Kontierung, auch wenn der Buchhalter sie als lästig empfindet.
- **Belegprinzip**: Rechnungsnummer, Referenz, Belegdatum und Buchungsdatum machen die Forderung eindeutig und zuordenbar beim Zahlungseingang.
- **Rechnungsausgabe aus der Buchhaltung**: Auch die manuelle Rechnung muss den Kunden erreichen, als PDF per E-Mail oder Druck, in einem definierten Formular.

### Kontrollfragen, die der Prozess aufwirft

Wer darf manuell buchen, gibt es ein Vier-Augen-Prinzip (Vorerfassung und Buchung getrennt)? Welche Erlöskonten sind erlaubt? Wie wird verhindert, dass Rechnungen doppelt erfasst werden (Referenzpflicht)? Wie hoch ist der Anteil manueller Rechnungen, und sollte er sinken (Hinweis auf fehlende Prozesse im Vertrieb oder fehlende Schnittstellen)?

---

## 3. Automatisierte Rechnungserstellung

### Warum es den Prozess gibt

Manuelle Erfassung skaliert nicht und ist fehleranfällig. Sobald Rechnungen in Serie entstehen, aus einem anderen System kommen oder zu einem Vertriebsbeleg gehören, soll die Buchung ohne Eingriff der Buchhaltung erfolgen. Ziel: Die Buchhaltung kontrolliert, sie tippt nicht ab.

### Drei Wege und ihr Kontext

**Weg 1: Faktura aus dem Vertrieb.** Der Standard für alles, was über Auftrag und Lieferung oder Leistungserbringung läuft. Die Faktura ist der rechtlich relevante Rechnungsbeleg, der Buchhaltungsbeleg entsteht automatisch mit ihr. Erlöskonten, Steuer, Zahlungsbedingung und Ergebnisobjekt sind durch Vertriebs- und Materialstammdaten bestimmt. Für die Buchhaltung heißt das: kein Erfassungsaufwand, aber Abhängigkeit von der Qualität der Vertriebs- und Stammdaten. Fehler äußern sich als falsche Konten, falsche Steuer oder nicht zuordenbare Posten, und sie werden nicht in der Buchhaltung, sondern in der Vertriebskonfiguration behoben.

**Weg 2: Massenupload.** Für periodische oder projektbezogene Mengen, die nicht aus dem Vertrieb kommen und für die sich keine Schnittstelle lohnt: Nebenkostenabrechnungen, Mitgliedsbeiträge, Gebühren, Weiterbelastungen aus einem Abrechnungstool, Abgrenzungen. Die Buchhaltung bereitet eine Datei vor, lädt sie, prüft die Fehlerliste, korrigiert und bucht in einem Schritt. Der Prozess verlagert die Qualitätsprüfung vor die Buchung (Prüflauf statt Storno).

**Weg 3: Schnittstelle.** Für Vorsysteme mit laufendem Rechnungsvolumen (Abrechnungssystem, Shop, Portal, Branchenlösung). Die Rechnung wird im Vorsystem erstellt und per API gebucht. Die Buchhaltung überwacht nur noch Fehlermeldungen. Voraussetzung ist eine saubere Abbildung von Kundennummern, Steuerkennzeichen und Konten im Vorsystem.

### Entscheidungslogik für den Kunden

| Rechnungsquelle | Volumen | Regelmäßigkeit | Empfohlener Weg |
|---|---|---|---|
| Lieferung oder Leistung aus Kundenauftrag | beliebig | laufend | Faktura (Vertrieb) |
| Vorsystem mit eigener Rechnungsstellung | hoch | laufend | Schnittstelle |
| Liste aus Abrechnungstool oder Fachbereich | mittel | periodisch | Upload |
| Einzelfälle, Korrekturen | niedrig | unregelmäßig | manuelle Rechnung |

### Was der Prozess sicherstellt

Gleiche Buchungslogik auf allen Wegen: Jeder Weg erzeugt denselben offenen Posten mit Fälligkeit, Referenz und Ergebnisobjekt. Zahlungseingang, Mahnung und Auswertung unterscheiden nicht, woher die Rechnung kam. Deshalb muss die Konfiguration (Konten, Steuer, Ergebnisobjekt-Ableitung) für alle Wege gleich gepflegt sein.

---

## 4. Buchung, Führung des offenen Postens und Basis-Konfiguration

### Warum es den Prozess gibt

Mit der Buchung beginnt das Leben des offenen Postens. Zwischen Rechnung und Zahlung liegen Tage bis Monate, in denen Fragen auftauchen: Ist die Rechnung angekommen? Ist sie strittig? Wurde eine Zahlsperre gesetzt? Wann wird gemahnt? Der Posten muss diese Informationen tragen, und die Buchhaltung muss sie pflegen können, ohne den Beleg zu stornieren.

### Geschäftlicher Kontext

- **Kundenkonto als Verhandlungsgrundlage.** Kontoauszug, Offene-Posten-Liste und Saldenbestätigung sind die Dokumente, mit denen Kunde und Unternehmen den Stand abgleichen. Sie müssen jederzeit aus dem System erzeugbar sein.
- **Korrekturen gehören zum Alltag.** Falsche Rechnung, falscher Kunde, falscher Betrag: Der Prozess sieht Storno mit Stornogrund vor, nie das Löschen. Bereits ausgeglichene Posten müssen zuerst wieder geöffnet werden. Jede Änderung ist protokolliert (Änderungsbelege), weil Prüfer nachvollziehen müssen, wer wann was geändert hat.
- **Steuerung über Kennzahlen.** Überfälligkeit nach Alter, DSO, Days Beyond Terms, Mahnstufenverteilung und Top-Debitoren sagen dem Management, ob die Forderungen gesund sind. Diese Kennzahlen entstehen nur, wenn Stamm und Posten sauber gepflegt sind.
- **Vorbereitung des Zahlungseingangs (Workshop 4).** Referenz, Betrag und Kunde auf dem Posten sind die Schlüssel, über die der elektronische Kontoauszug später automatisch zuordnet. Schlechte Postenqualität heißt manuelle Nacharbeit beim Zahlungseingang.

### Was „Basis-Konfiguration“ bedeutet

Die Public Cloud liefert die Debitorenbuchhaltung vorkonfiguriert: Belegarten, Nummernkreise, Zahlungsbedingungen, Mahnverfahren, Zinskennzeichen, Kontenfindung für Steuer und Zahlungsdifferenzen, Formulare. Der Kunde entscheidet im Fit-to-Standard nicht, **ob** es diese Objekte gibt, sondern **welche Ausprägungen** er braucht und **wer** sie nutzt:

| Entscheidungsfeld | Geschäftliche Frage dahinter |
|---|---|
| Sachbearbeiter | Wer ist für welche Kunden verantwortlich, wer mahnt, wer wird in Kennzahlen ausgewiesen? |
| Zahlungsbedingungen | Welche Zahlungsziele und Skonti bieten wir an, und welche sind Standard? |
| Abstimmkonten | Wie gliedern wir Forderungen in der Bilanz (Inland, Ausland, verbunden, Sonstige)? |
| Erlöskonten und Ergebnisobjekt | Wie wollen wir Umsatz auswerten (Produkt, Kunde, Region)? |
| Rechnungs- und Korrespondenzformulare | Wie sieht unsere Rechnung aus, wie geht sie raus, in welcher Sprache? |
| Mahnverfahren und Zinsen | Wie konsequent und in welchen Stufen mahnen wir, berechnen wir Verzugszinsen? |
| Toleranzen und Grundcodes | Welche Zahlungsdifferenzen akzeptieren wir automatisch, wie dokumentieren wir Abzüge? |
| Ausbuchung | Ab wann und mit wessen Freigabe wird eine Forderung abgeschrieben? |
| Kreditmanagement | Prüfen wir Kreditlimits, wer legt sie fest, wer gibt frei? |
| Rollen | Wer darf Stammdaten ändern, buchen, stornieren, konfigurieren? |

Das Ergebnis des Workshops ist diese Liste mit Entscheidungen oder mit offenen Punkten, die in Key Design Decisions (KDDs) münden.

---

## 5. Zusammenfassung in drei Sätzen

Der Debitorenstamm legt fest, mit wem und zu welchen Bedingungen Forderungen entstehen dürfen. Rechnungen entstehen auf vier Wegen (Faktura, Schnittstelle, Upload, manuell), landen aber in demselben offenen Posten mit derselben Logik. Die Konfiguration bestimmt, wie dieser Posten aussieht, wer ihn verantwortet und wie das Unternehmen Forderungen auswertet und steuert.
