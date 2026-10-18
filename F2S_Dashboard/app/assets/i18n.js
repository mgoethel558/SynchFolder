/* i18n.js -- zentrale Uebersetzungen DE/EN fuer das F2S Outcome Dashboard.
   Jeder sichtbare Text, jedes Label, jede Achse und jeder Statuswert ist hier
   hinterlegt. Umschaltung ueber I18N.t(key) + aktuell gewaehlte Sprache. */
const I18N = (() => {
  const dict = {
    // --- Header / allgemein ---
    app_title:        { de: "Fit-to-Standard Outcome Dashboard", en: "Fit-to-Standard Outcome Dashboard" },
    app_subtitle:     { de: "Workshop-Ergebnisse fuer Status-Meetings", en: "Workshop outcomes for status meetings" },
    last_update:      { de: "Letzte Aktualisierung", en: "Last update" },
    never:            { de: "noch nie", en: "never" },
    btn_refresh:      { de: "Aktualisieren", en: "Refresh" },
    btn_pdf:          { de: "PDF-Export", en: "Export PDF" },
    refreshing:       { de: "Aktualisiere …", en: "Refreshing …" },

    // --- Status-Phasen beim Refresh ---
    phase_download:   { de: "Lade Dateien aus SharePoint …", en: "Downloading files from SharePoint …" },
    phase_parse:      { de: "Werte Dateien aus …", en: "Parsing files …" },
    phase_snapshot:   { de: "Speichere Snapshot …", en: "Saving snapshot …" },
    refresh_ok:       { de: "Aktualisierung erfolgreich", en: "Refresh successful" },
    refresh_unchanged:{ de: "Keine Aenderungen gegenueber dem letzten Lauf", en: "No changes since last run" },
    refresh_failed:   { de: "Aktualisierung fehlgeschlagen", en: "Refresh failed" },
    files_processed:  { de: "Dateien verarbeitet", en: "files processed" },
    refresh_file_mode_title: { de: "Zum Aktualisieren bitte „Aktualisieren.bat“ ausführen", en: "To refresh, please run “Aktualisieren.bat”" },
    refresh_file_mode_hint:  { de: "Das Laden aus SharePoint läuft über Aktualisieren.bat (Download + Auswertung). Danach dieses Dashboard neu laden.", en: "Loading from SharePoint runs via Aktualisieren.bat (download + analysis). Then reload this dashboard." },

    // --- leerer Zustand ---
    empty_title:      { de: "Noch keine Daten", en: "No data yet" },
    empty_hint:       { de: "Bitte auf „Aktualisieren“ klicken, um die Workshop-Ergebnisse zu laden.", en: "Please click “Refresh“ to load the workshop outcomes." },
    empty_hint_file:  { de: "Bitte „Aktualisieren.bat“ ausführen, um die Workshop-Ergebnisse aus SharePoint zu laden.", en: "Please run “Aktualisieren.bat” to load the workshop outcomes from SharePoint." },

    // --- Sektions-Titel ---
    section_charts:   { de: "Grafiken", en: "Charts" },
    section_kpis:     { de: "Kennzahlen (KPIs)", en: "Key figures (KPIs)" },

    // --- Grafiken ---
    chart_a_title:    { de: "A – Verlauf (Burn-up)", en: "A – Trend (burn-up)" },
    chart_a_desc:     { de: "Kumuliert angelegt vs. geschlossen über die Snapshot-Historie", en: "Cumulative created vs. closed across snapshot history" },
    chart_b_title:    { de: "B – Status pro LoB", en: "B – Status per LoB" },
    chart_b_desc:     { de: "Gestapelt nach Status, je Typ", en: "Stacked by status, per type" },
    chart_c_title:    { de: "C – Workshops pro LoB", en: "C – Workshops per LoB" },
    chart_c_desc:     { de: "Durchgeführte Workshops", en: "Conducted workshops" },
    chart_d_title:    { de: "D – Fit-Assessment pro LoB", en: "D – Fit assessment per LoB" },
    chart_d_desc:     { de: "Verteilung Fit / Gap je LoB", en: "Distribution of fit / gap per LoB" },
    created:          { de: "angelegt", en: "created" },
    closed:           { de: "geschlossen", en: "closed" },
    type_filter:      { de: "Typ", en: "Type" },
    all_types:        { de: "Alle Typen", en: "All types" },

    // --- KPIs ---
    kpi_workshops:    { de: "Workshops", en: "Workshops" },
    kpi_requirements: { de: "Requirements", en: "Requirements" },
    kpi_issues:       { de: "Issues", en: "Issues" },
    kpi_tasks:        { de: "Tasks", en: "Tasks" },
    kpi_decisions:    { de: "Decisions", en: "Decisions" },
    kpi_done_share:   { de: "Anteil erledigt", en: "Share done" },
    kpi_conducted:    { de: "durchgeführt", en: "conducted" },
    kpi_open_of:      { de: "offen von", en: "open of" },

    // --- Drill-down / Detailansicht ---
    entries:          { de: "Einträge", en: "entries" },
    no_entries:       { de: "Keine Einträge", en: "No entries" },
    col_outcome_id:   { de: "Outcome ID", en: "Outcome ID" },
    col_topic:        { de: "Thema / Prozessschritt", en: "Topic / process step" },
    col_status:       { de: "Status", en: "Status" },
    col_owner:        { de: "Verantwortlich", en: "Owner" },
    col_due:          { de: "Fällig", en: "Due" },
    col_workshop:     { de: "Workshop", en: "Workshop" },
    col_date:         { de: "Datum", en: "Date" },
    open_in_sharepoint: { de: "In SharePoint öffnen", en: "Open in SharePoint" },

    // --- Tabelle ---
    table_title:      { de: "Übersicht pro Workstream / LoB", en: "Overview per workstream / LoB" },
    col_lob:          { de: "Workstream / LoB", en: "Workstream / LoB" },
    col_workshops:    { de: "Workshops", en: "Workshops" },
    col_requirements: { de: "Requirements", en: "Requirements" },
    col_issues:       { de: "Issues", en: "Issues" },
    col_tasks:        { de: "Tasks", en: "Tasks" },
    col_decisions:    { de: "Decisions", en: "Decisions" },
    col_extra:        { de: "Assumption / Information", en: "Assumption / Information" },
    row_total:        { de: "Summe", en: "Total" },
    expand_hint:      { de: "Zum Auf-/Zuklappen der Areas klicken", en: "Click to expand/collapse areas" },

    // --- Typen (fuer Achsen/Legenden) ---
    typ_requirement:  { de: "Requirements", en: "Requirements" },
    typ_issue:        { de: "Issues", en: "Issues" },
    typ_task:         { de: "Tasks", en: "Tasks" },
    typ_decision:     { de: "Decisions", en: "Decisions" },
    typ_assumption:   { de: "Assumptions", en: "Assumptions" },
    typ_information:  { de: "Information", en: "Information" },

    // --- Statuswerte ---
    "status_offen":        { de: "offen", en: "open" },
    "status_in Arbeit":    { de: "in Arbeit", en: "in progress" },
    "status_erledigt":     { de: "erledigt", en: "done" },
    "status_nicht relevant": { de: "nicht relevant", en: "not required" },
    "status_unbekannt":    { de: "unbekannt", en: "unknown" },

    // --- Warnungen ---
    warnings_title:   { de: "Hinweise aus der letzten Auswertung", en: "Notices from last run" },
    warn_unknown_status: { de: "Unbekannter Statuswert", en: "Unknown status value" },
    warn_unknown_record_type: { de: "Unbekannter Record Type", en: "Unknown record type" },
    warn_placeholder_workshop: { de: "Unausgefüllte Vorlage übersprungen (Platzhalter-Workshop-ID)", en: "Skipped unfilled template (placeholder workshop ID)" },
    in_column:        { de: "in Spalte", en: "in column" },
    in_file:          { de: "Datei", en: "file" },

    // --- Footer ---
    footer_note:      { de: "Läuft vollständig lokal · SharePoint-Zugriff nur lesend", en: "Runs fully local · read-only SharePoint access" },
  };

  let lang = "de";

  function detect() {
    const saved = localStorage.getItem("f2sLang");
    if (saved === "de" || saved === "en") return saved;
    const codes = (navigator.languages || [navigator.language || "de"])
      .map(x => String(x).toLowerCase().split("-")[0]);
    return codes.includes("de") ? "de" : "en";
  }

  function t(key) {
    const e = dict[key];
    if (!e) return key;
    return e[lang] !== undefined ? e[lang] : (e.de || key);
  }

  function status(raw) { return t("status_" + raw); }
  function typ(raw) { return t("typ_" + raw); }

  function set(l) { lang = l; localStorage.setItem("f2sLang", l); }
  function get() { return lang; }

  return { t, status, typ, set, get, detect };
})();
