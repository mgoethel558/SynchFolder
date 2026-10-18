/* app.js -- Rendering des F2S Outcome Dashboards aus snapshots.json.
   Grafiken via Chart.js (lokal). DE/EN ueber I18N. PDF via window.print(). */

const COLORS = {
  offen: "#b7791f", "in Arbeit": "#2563eb", erledigt: "#157347",
  "nicht relevant": "#9aa3af", unbekannt: "#d14343",
};
const FIT_COLORS = {
  "Fit": "#157347", "Fit with Configuration": "#2f9e5f",
  "Fit with Process Change": "#7bb661", "Gap / Extension Required": "#e50043",
  "Open / To Be Assessed": "#b7791f", "Out of Scope": "#9aa3af",
};
const LOB_PALETTE = ["#e50043","#2563eb","#157347","#b7791f","#7c3aed","#0891b2","#c2410c","#4b5563"];

const state = {
  store: { snapshots: [] },
  cfg: { status_keys: [], main_types: [], extra_types: [], fit_assessment_values: [] },
  charts: {}, sortKey: "lob", sortDir: 1, expanded: {},
};

// ---------- Hilfsfunktionen ----------
function el(id){ return document.getElementById(id); }
function latest(){ const s = state.store.snapshots; return s.length ? s[s.length-1] : null; }
function pct(done, total){ return total ? Math.round(done/total*100) : 0; }

function applyStaticI18n(){
  document.querySelectorAll("[data-i18n]").forEach(n => {
    const v = I18N.t(n.dataset.i18n);
    if (v) n.textContent = v;
  });
  document.documentElement.lang = I18N.get();
  document.body.className = "lang-" + I18N.get();
}

// ---------- Modus-Erkennung ----------
// Datei-Modus: Dashboard.html wurde per Doppelklick (file://) geoeffnet und
// die Daten liegen in window.F2S_DATA (aus data/snapshots.js).
// Server-Modus: Dashboard laeuft ueber localhost mit Backend-API.
function isFileMode(){ return location.protocol === "file:" || !!window.F2S_DATA; }

// ---------- Datenbeschaffung ----------
async function loadSnapshots(){
  if (isFileMode()){
    state.store = (window.F2S_DATA && window.F2S_DATA.store) || {snapshots:[]};
    return;
  }
  const r = await fetch("/api/snapshots", {cache:"no-store"});
  state.store = await r.json();
}
async function loadConfig(){
  if (isFileMode()){
    if (window.F2S_DATA && window.F2S_DATA.config) state.cfg = window.F2S_DATA.config;
    return;
  }
  try { state.cfg = await (await fetch("/api/config",{cache:"no-store"})).json(); }
  catch(e){ /* Defaults bleiben */ }
}

// ---------- Refresh ----------
async function doRefresh(){
  // Im Datei-Modus kann der Browser den SharePoint-Download nicht ausloesen
  // (kein Python/Dateizugriff). Stattdessen Hinweis auf Aktualisieren.bat.
  if (isFileMode()){
    showToast("err", I18N.t("refresh_file_mode_title"), I18N.t("refresh_file_mode_hint"));
    return;
  }
  const btn = el("btnRefresh");
  btn.disabled = true;
  showToast("spin", I18N.t("refreshing"), "");
  setProgress(15);
  try {
    const r = await fetch("/api/refresh", {method:"POST"});
    setProgress(80);
    const res = await r.json();
    if (res.ok){
      await loadSnapshots();
      render();
      setProgress(100);
      const msg = res.unchanged ? I18N.t("refresh_unchanged")
        : `${I18N.t("refresh_ok")} · ${res.files_processed} ${I18N.t("files_processed")}`;
      showToast("ok", msg, "");
    } else {
      showToast("err", I18N.t("refresh_failed"), res.error || "");
    }
  } catch(e){
    showToast("err", I18N.t("refresh_failed"), String(e));
  } finally {
    btn.disabled = false;
    setTimeout(()=>setProgress(0), 600);
  }
}
function setProgress(p){ el("progress").style.width = p + "%"; }
function showToast(kind, title, detail){
  const t = el("toast");
  t.className = "toast show " + (kind==="ok"?"ok":kind==="err"?"err":"");
  const spin = kind==="spin" ? '<span class="spin"></span>' : "";
  t.innerHTML = `${spin}<b>${title}</b>${detail?`<br><span style="font-size:13px;color:#667085">${detail}</span>`:""}`;
  if (kind!=="spin") setTimeout(()=>t.classList.remove("show"), 6000);
}

// ---------- Render-Hauptfunktion ----------
function render(){
  applyStaticI18n();
  const snap = latest();
  const has = !!snap && Object.keys(snap.lob_aggregates||{}).length>0;

  el("emptyState").classList.toggle("hidden", has);
  ["chartSection","kpiSection","tableSection"].forEach(id=>el(id).classList.toggle("hidden", !has));

  // letzte Aktualisierung
  if (snap){
    const d = new Date(snap.timestamp);
    const txt = d.toLocaleString(I18N.get()==="de"?"de-DE":"en-GB");
    el("lastUpdate").textContent = txt;
    el("printDate").textContent = txt;
  } else {
    el("lastUpdate").textContent = I18N.t("never");
  }
  if (!has){ renderWarnings(snap); return; }

  renderWarnings(snap);
  renderTypeSelectors();
  renderKpis(snap);
  renderTable(snap);
  renderCharts(snap);
}

// ---------- Warnungen ----------
function renderWarnings(snap){
  const box = el("warnBox"), list = el("warnList");
  const w = (snap && snap.warnings) || [];
  if (!w.length){ box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  const labelMap = {
    unknown_status: "warn_unknown_status",
    unknown_record_type: "warn_unknown_record_type",
    placeholder_workshop: "warn_placeholder_workshop",
  };
  list.innerHTML = w.map(x=>{
    const label = labelMap[x.type] ? I18N.t(labelMap[x.type]) : x.type;
    return `<li>${label}: „${x.value}“ ${x.column?`(${I18N.t("in_column")} ${x.column})`:""} — ${I18N.t("in_file")} ${x.file}</li>`;
  }).join("");
}

// ---------- Typ-Auswahl (Grafik A & B) ----------
function renderTypeSelectors(){
  const burn = el("burnupType"), stat = el("statusType");
  const opts = (withAll) => {
    let s = withAll ? `<option value="__all__">${I18N.t("all_types")}</option>` : "";
    state.cfg.main_types.forEach(t => s += `<option value="${t}">${I18N.typ(t)}</option>`);
    return s;
  };
  const bPrev = burn.value || "__all__";
  const sPrev = stat.value || (state.cfg.main_types[0]||"requirement");
  burn.innerHTML = opts(true); burn.value = bPrev;
  stat.innerHTML = opts(false); stat.value = sPrev;
  burn.onchange = ()=>renderChartA(latest());
  stat.onchange = ()=>renderChartB(latest());
}

// ---------- KPIs (Variante B) ----------
// Jede Excel-Zeile zaehlt einmal nach Record Type. Tasks/Decisions sind
// Zeilen-Attribute -> als "offen von gesamt" dargestellt, nicht als Zeilenzahl.
function aggregateTotals(snap){
  const totals = {}; state.cfg.main_types.forEach(t=>totals[t]={});
  let workshops=0, openTasks=0, totalTasks=0, openDec=0, totalDec=0;
  Object.values(snap.lob_aggregates).forEach(lob=>{
    workshops += lob.workshops_conducted||0;
    openTasks += lob.open_tasks||0; totalTasks += lob.total_tasks||0;
    openDec += lob.open_decisions||0; totalDec += lob.total_decisions||0;
    state.cfg.main_types.forEach(t=>{
      const c = lob.counts[t]||{};
      Object.entries(c).forEach(([s,n])=> totals[t][s]=(totals[t][s]||0)+n);
    });
  });
  return { workshops, totals, openTasks, totalTasks, openDec, totalDec };
}
function sumType(c){ return Object.values(c).reduce((a,b)=>a+b,0); }
function doneOf(c){ return c["erledigt"]||0; }

function renderKpis(snap){
  const t = aggregateTotals(snap);
  const cards = [];
  cards.push(kpiCard(I18N.t("kpi_workshops"), t.workshops, null, I18N.t("kpi_conducted")));
  [["requirement","kpi_requirements"],["issue","kpi_issues"]].forEach(([typ,key])=>{
    const c = t.totals[typ]||{}; const tot=sumType(c); const dn=doneOf(c);
    cards.push(kpiCard(I18N.t(key), tot, pct(dn,tot), null));
  });
  // Tasks/Decisions als "offen / gesamt" (Zeilen-Attribut, keine eigene Zeile)
  cards.push(kpiCard(I18N.t("kpi_tasks"), t.openTasks,
    null, `${I18N.t("kpi_open_of")} ${t.totalTasks}`));
  cards.push(kpiCard(I18N.t("kpi_decisions"), t.openDec,
    null, `${I18N.t("kpi_open_of")} ${t.totalDec}`));
  el("kpis").innerHTML = cards.join("");
}
function kpiCard(label, big, share, suffix){
  let shareHtml = "";
  if (share!==null && share!==undefined){
    shareHtml = `<div class="share">${share}% ${I18N.t("kpi_done_share")}
      <div class="barmini"><i style="width:${share}%"></i></div></div>`;
  } else if (suffix){
    shareHtml = `<div class="share" style="color:var(--muted)">${suffix}</div>`;
  }
  return `<div class="kpi"><div class="label">${label}</div>
    <div class="big">${big}</div>${shareHtml}</div>`;
}

// ---------- Tabelle (Variante B) ----------
// Status-Pills je Typ; jede Pill ist KLICKBAR -> Drill-down.
// filterCtx: {lob, area|null, typ, status} zur Eintragsauswahl im Modal.
function statusCells(c, ctx){
  const order = ["offen","in Arbeit","erledigt"];
  const extra = ["nicht relevant","unbekannt"];
  let html = "";
  const pill = (s)=>{
    const n = c[s]||0;
    const cls = s.replace(/\s/g,"").toLowerCase();
    const clickable = n>0 ? "clickable" : "";
    const data = n>0 ? `data-lob="${esc(ctx.lob)}" data-area="${esc(ctx.area||"")}" data-typ="${ctx.typ}" data-status="${s}"` : "";
    return `<span class="pill ${n?cls:'zero'} ${clickable}" ${data} title="${I18N.status(s)}">${n}</span>`;
  };
  order.forEach(s=> html += pill(s));
  extra.forEach(s=>{ if ((c[s]||0)>0) html += pill(s); });
  return `<td class="num celltyp">${html}</td>`;
}
// Zelle fuer Tasks/Decisions (offen / gesamt), ebenfalls klickbar.
function attrCell(open, total, ctx){
  const clickable = total>0 ? "clickable" : "";
  const data = total>0 ? `data-lob="${esc(ctx.lob)}" data-area="${esc(ctx.area||"")}" data-attr="${ctx.attr}"` : "";
  return `<td class="num"><span class="attrpill ${clickable}" ${data}>`+
         `<b>${open}</b> / ${total}</span></td>`;
}
function extraCell(counts, ctx){
  const a = sumType(counts.assumption||{}), i = sumType(counts.information||{});
  const mk = (n,typ)=> n>0
    ? `<span class="miniclick clickable" data-lob="${esc(ctx.lob)}" data-area="${esc(ctx.area||"")}" data-typ="${typ}" data-status="__all__">${n}</span>`
    : `<span class="miniclick zero">${n}</span>`;
  return `<td class="num">${mk(a,"assumption")} / ${mk(i,"information")}</td>`;
}
function esc(s){ return String(s).replace(/"/g,"&quot;"); }

function renderTableHead(){
  const cols = [
    ["lob","col_lob"],["workshops","col_workshops"],["requirement","col_requirements"],
    ["issue","col_issues"],["task","col_tasks"],["decision","col_decisions"],["extra","col_extra"],
  ];
  el("lobHead").innerHTML = "<tr>" + cols.map(([k,i18n])=>{
    const arrow = state.sortKey===k ? (state.sortDir>0?"▲":"▼") : "";
    const numcls = (k!=="lob")?"num":"";
    return `<th class="${numcls}" data-sort="${k}">${I18N.t(i18n)} <span class="arrow">${arrow}</span></th>`;
  }).join("") + "</tr>";
  el("lobHead").querySelectorAll("th").forEach(th=>{
    th.onclick = ()=>{ const k=th.dataset.sort;
      if(state.sortKey===k) state.sortDir*=-1; else {state.sortKey=k;state.sortDir=1;}
      renderTable(latest()); };
  });
}
function sortValue(name, agg, key){
  if (key==="lob") return name.toLowerCase();
  if (key==="workshops") return agg.workshops_conducted||0;
  if (key==="task") return agg.total_tasks||0;
  if (key==="decision") return agg.total_decisions||0;
  if (key==="extra") return sumType(agg.counts.assumption||{})+sumType(agg.counts.information||{});
  return sumType(agg.counts[key]||{});
}
function renderTable(snap){
  renderTableHead();
  const lobs = Object.entries(snap.lob_aggregates);
  lobs.sort((a,b)=>{
    const va=sortValue(a[0],a[1],state.sortKey), vb=sortValue(b[0],b[1],state.sortKey);
    return (va<vb?-1:va>vb?1:0)*state.sortDir;
  });
  const body = el("lobBody"); body.innerHTML = "";
  const totals = {workshops:0, counts:{}, open_tasks:0, total_tasks:0, open_decisions:0, total_decisions:0};
  ALL_T().forEach(t=>totals.counts[t]={});

  lobs.forEach(([name, agg])=>{
    const open = !!state.expanded[name];
    const row = document.createElement("tr");
    row.className = "lob-row";
    const ctx = {lob:name, area:null};
    row.innerHTML =
      `<td><span class="toggle">${open?"▾":"▸"}</span> ${name}</td>`+
      `<td class="num">${agg.workshops_conducted||0}</td>`+
      statusCells(agg.counts.requirement||{}, {...ctx, typ:"requirement"})+
      statusCells(agg.counts.issue||{}, {...ctx, typ:"issue"})+
      attrCell(agg.open_tasks||0, agg.total_tasks||0, {...ctx, attr:"task"})+
      attrCell(agg.open_decisions||0, agg.total_decisions||0, {...ctx, attr:"decision"})+
      extraCell(agg.counts, ctx);
    // Klick auf die LoB-Zeile (nicht auf eine Pill) klappt Areas auf/zu.
    row.querySelector(".toggle").parentElement.onclick = (ev)=>{
      if (ev.target.closest(".clickable")) return;
      state.expanded[name]=!state.expanded[name]; renderTable(latest());
    };
    body.appendChild(row);

    if (open && agg.areas){
      Object.entries(agg.areas).forEach(([aname, a])=>{
        const actx = {lob:name, area:aname};
        const ar = document.createElement("tr");
        ar.className = "area-row";
        ar.innerHTML =
          `<td>${aname}</td><td class="num">${a.workshops_conducted||0}</td>`+
          statusCells(a.counts.requirement||{}, {...actx, typ:"requirement"})+
          statusCells(a.counts.issue||{}, {...actx, typ:"issue"})+
          attrCell(a.open_tasks||0, a.total_tasks||0, {...actx, attr:"task"})+
          attrCell(a.open_decisions||0, a.total_decisions||0, {...actx, attr:"decision"})+
          extraCell(a.counts, actx);
        body.appendChild(ar);
      });
    }

    totals.workshops += agg.workshops_conducted||0;
    totals.open_tasks += agg.open_tasks||0; totals.total_tasks += agg.total_tasks||0;
    totals.open_decisions += agg.open_decisions||0; totals.total_decisions += agg.total_decisions||0;
    ALL_T().forEach(t=>{
      const c = agg.counts[t]||{};
      Object.entries(c).forEach(([s,n])=> totals.counts[t][s]=(totals.counts[t][s]||0)+n);
    });
  });

  const tctx = {lob:"__all__", area:null};
  el("lobFoot").innerHTML =
    `<tr class="total-row"><td>${I18N.t("row_total")}</td>`+
    `<td class="num">${totals.workshops}</td>`+
    statusCells(totals.counts.requirement, {...tctx, typ:"requirement"})+
    statusCells(totals.counts.issue, {...tctx, typ:"issue"})+
    attrCell(totals.open_tasks, totals.total_tasks, {...tctx, attr:"task"})+
    attrCell(totals.open_decisions, totals.total_decisions, {...tctx, attr:"decision"})+
    extraCell(totals.counts, tctx)+`</tr>`;

  // Klick-Handler fuer alle klickbaren Zellen -> Drill-down.
  el("lobTable").querySelectorAll(".clickable").forEach(elm=>{
    elm.onclick = (ev)=>{ ev.stopPropagation(); openDrilldown(elm.dataset); };
  });
}
function ALL_T(){ return state.cfg.main_types.concat(state.cfg.extra_types); }

// ---------- Grafiken ----------
function destroy(id){ if(state.charts[id]){ state.charts[id].destroy(); delete state.charts[id]; } }

function renderCharts(snap){ renderChartA(snap); renderChartB(snap); renderChartC(snap); renderChartD(snap); }

// A: Burn-up aus Snapshot-Historie
function renderChartA(snap){
  destroy("A");
  const typ = el("burnupType").value || "__all__";
  const snaps = state.store.snapshots;
  const labels=[], created=[], closed=[];
  const seen = new Set(), closedSeen = new Set();
  snaps.forEach(s=>{
    (s.entries||[]).forEach(e=>{
      if (typ!=="__all__" && e.typ!==typ) return;
      const key = e.uid || (e.outcome_id+"|"+e.typ);
      seen.add(key);
      if (e.status==="erledigt") closedSeen.add(key);
    });
    labels.push(new Date(s.timestamp).toLocaleDateString(I18N.get()==="de"?"de-DE":"en-GB"));
    created.push(seen.size); closed.push(closedSeen.size);
  });
  state.charts["A"] = new Chart(el("chartA"), {
    type:"line",
    data:{labels, datasets:[
      {label:I18N.t("created"), data:created, borderColor:"#2563eb", backgroundColor:"#2563eb22", tension:.25, fill:true},
      {label:I18N.t("closed"), data:closed, borderColor:"#157347", backgroundColor:"#15734722", tension:.25, fill:true},
    ]},
    options:baseOpts({stacked:false})
  });
}

// B: Status pro LoB (gestapelt) fuer gewaehlten Typ
function renderChartB(snap){
  destroy("B");
  const typ = el("statusType").value || state.cfg.main_types[0];
  const lobs = Object.keys(snap.lob_aggregates);
  const statuses = ["offen","in Arbeit","erledigt","nicht relevant","unbekannt"];
  const datasets = statuses.map(st=>({
    label:I18N.status(st),
    data:lobs.map(l=> (snap.lob_aggregates[l].counts[typ]||{})[st]||0),
    backgroundColor:COLORS[st],
  })).filter(ds=> ds.data.some(v=>v>0) || ["offen","in Arbeit","erledigt"].includes(ds.label));
  state.charts["B"] = new Chart(el("chartB"), {
    type:"bar", data:{labels:lobs, datasets}, options:baseOpts({stacked:true})
  });
}

// C: Workshops pro LoB
function renderChartC(snap){
  destroy("C");
  const lobs = Object.keys(snap.lob_aggregates);
  state.charts["C"] = new Chart(el("chartC"), {
    type:"bar",
    data:{labels:lobs, datasets:[{
      label:I18N.t("kpi_workshops"),
      data:lobs.map(l=>snap.lob_aggregates[l].workshops_conducted||0),
      backgroundColor:lobs.map((_,i)=>LOB_PALETTE[i%LOB_PALETTE.length]),
    }]},
    options:baseOpts({stacked:false, legend:false})
  });
}

// D: Fit-Assessment-Verteilung pro LoB (gestapelt)
function renderChartD(snap){
  destroy("D");
  const lobs = Object.keys(snap.lob_aggregates);
  const fitVals = state.cfg.fit_assessment_values.length ? state.cfg.fit_assessment_values
    : [...new Set(lobs.flatMap(l=>Object.keys(snap.lob_aggregates[l].fit_assessment||{})))];
  const datasets = fitVals.map(fv=>({
    label:fv,
    data:lobs.map(l=> (snap.lob_aggregates[l].fit_assessment||{})[fv]||0),
    backgroundColor:FIT_COLORS[fv]||"#9aa3af",
  })).filter(ds=>ds.data.some(v=>v>0));
  state.charts["D"] = new Chart(el("chartD"), {
    type:"bar", data:{labels:lobs, datasets}, options:baseOpts({stacked:true})
  });
}

function baseOpts({stacked, legend=true}){
  return {
    responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{display:legend, position:"bottom", labels:{boxWidth:12,font:{size:11}}} },
    scales:{
      x:{stacked, ticks:{font:{size:11}}},
      y:{stacked, beginAtZero:true, ticks:{precision:0,font:{size:11}}}
    }
  };
}

// ---------- Drill-down ----------
function fmtDate(iso){
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleDateString(I18N.get()==="de"?"de-DE":"en-GB");
}
function openDrilldown(ds){
  const snap = latest();
  if (!snap) return;
  let entries = snap.entries || [];
  // Filter nach LoB (ausser Summe) und ggf. Area.
  if (ds.lob && ds.lob!=="__all__") entries = entries.filter(e=>e.lob===ds.lob);
  if (ds.area) entries = entries.filter(e=>e.area===ds.area);

  let title;
  if (ds.attr){
    // Tasks/Decisions: alle Zeilen mit gefuelltem Attribut
    const key = ds.attr==="task" ? "has_task" : "has_decision";
    entries = entries.filter(e=>e[key]);
    title = (ds.attr==="task"?I18N.t("kpi_tasks"):I18N.t("kpi_decisions"));
  } else {
    entries = entries.filter(e=>e.typ===ds.typ);
    if (ds.status && ds.status!=="__all__") entries = entries.filter(e=>e.status===ds.status);
    title = I18N.typ(ds.typ) + (ds.status && ds.status!=="__all__" ? " · "+I18N.status(ds.status) : "");
  }
  const scope = ds.area ? `${ds.lob} / ${ds.area}` : (ds.lob==="__all__"?I18N.t("row_total"):ds.lob);
  renderDrilldown(title, scope, entries, ds);
}

function renderDrilldown(title, scope, entries, ds){
  el("modalTitle").textContent = title;
  el("modalScope").textContent = scope + " · " + entries.length + " " + I18N.t("entries");
  const showStatus = ds.attr || "";  // bei task/decision den Attribut-Status zeigen
  const head = `<tr>
    <th>${I18N.t("col_outcome_id")}</th>
    <th>${I18N.t("col_topic")}</th>
    <th>${I18N.t("col_status")}</th>
    <th>${I18N.t("col_owner")}</th>
    <th>${I18N.t("col_due")}</th>
    <th>${I18N.t("col_workshop")}</th>
    <th>${I18N.t("col_date")}</th>
    <th></th></tr>`;
  const rows = entries.map(e=>{
    let st = e.status;
    if (ds.attr==="task") st = e.task_status;
    if (ds.attr==="decision") st = e.decision_status;
    const stCls = (st||"").replace(/\s/g,"").toLowerCase();
    const link = e.source_url
      ? `<a href="${e.source_url}" target="_blank" rel="noopener" title="${I18N.t("open_in_sharepoint")}">↗</a>`
      : "";
    const topic = [e.topic, e.process_step].filter(Boolean).join(" · ");
    return `<tr>
      <td class="mono">${e.outcome_id||""}</td>
      <td>${topic||""}</td>
      <td><span class="pill ${stCls}">${st?I18N.status(st):""}</span></td>
      <td>${e.owner||""}</td>
      <td>${fmtDate(e.due_date)}</td>
      <td>${e.workshop_title||e.workshop_id||""}</td>
      <td>${fmtDate(e.workshop_date)}</td>
      <td class="num">${link}</td></tr>`;
  }).join("");
  el("modalTable").innerHTML = `<thead>${head}</thead><tbody>${rows||`<tr><td colspan="8" class="empty">${I18N.t("no_entries")}</td></tr>`}</tbody>`;
  el("modal").classList.add("show");
}
function closeModal(){ el("modal").classList.remove("show"); }

// ---------- PDF ----------
function doPdf(){ window.print(); }

// ---------- Sprache ----------
function setLang(l){
  I18N.set(l);
  document.querySelectorAll(".lang").forEach(b=>b.classList.toggle("active", b.dataset.lang===l));
  render();
}

// ---------- Version ----------
function showVersion(){
  const v = (window.F2S_DATA && window.F2S_DATA.app_version) || "";
  const node = el("appVersion");
  if (node && v) node.textContent = "v" + v;
}

// ---------- Init ----------
async function init(){
  I18N.set(I18N.detect());
  document.querySelectorAll(".lang").forEach(b=> b.onclick=()=>setLang(b.dataset.lang));
  el("btnRefresh").onclick = doRefresh;
  el("btnPdf").onclick = doPdf;
  // Modal schliessen (X-Button + Klick auf Overlay)
  const mc = el("modalClose"); if (mc) mc.onclick = closeModal;
  const mo = el("modal");
  if (mo) mo.onclick = (ev)=>{ if (ev.target===mo) closeModal(); };
  document.addEventListener("keydown", ev=>{ if (ev.key==="Escape") closeModal(); });
  await loadConfig();
  await loadSnapshots();
  showVersion();
  render();
}
init();
