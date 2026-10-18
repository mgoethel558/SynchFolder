(function(){
  "use strict";
  var root = document.documentElement;
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var counter = document.getElementById("counter");
  var fill = document.getElementById("progressFill");
  var notesText = document.getElementById("notesText");
  var themeBtn = document.getElementById("themeBtn");
  var deckMQ = window.matchMedia("(min-width: 900px) and (min-height: 560px)");
  var LABEL = { de: { dark: "Dunkel ", light: "Hell " }, en: { dark: "Dark ", light: "Light " } };
  var label = LABEL[(root.lang || "de").slice(0, 2)] || LABEL.de;
  var idx = 0;

  function isDeck(){ return root.classList.contains("deck"); }
  function pad(n){ return (n < 10 ? "0" : "") + n; }
  function pauseVideos(){
    Array.prototype.forEach.call(document.querySelectorAll("video"), function(v){ v.pause(); });
  }

  function go(n){
    idx = Math.max(0, Math.min(slides.length - 1, n));
    if (!isDeck()) {
      document.body.classList.remove("on-brand");
      if (idx > 0) { slides[idx].scrollIntoView(); }
      return;
    }
    slides.forEach(function(s, k){ s.classList.toggle("active", k === idx); });
    document.body.classList.toggle("on-brand", slides[idx].classList.contains("slide--brand"));
    if (counter) { counter.textContent = pad(idx + 1) + " / " + pad(slides.length); }
    if (fill) { fill.style.width = (((idx + 1) / slides.length) * 100) + "%"; }
    if (notesText) {
      var note = slides[idx].querySelector(".notes");
      notesText.innerHTML = note ? note.innerHTML : "—";
    }
    pauseVideos();
    try { history.replaceState(null, "", "#" + (idx + 1)); } catch (e) {}
  }
  function next(){ go(idx + 1); }
  function prev(){ go(idx - 1); }

  /* Farbschema: Standard hell (Sonnenlicht, Beamer), Umschalten per Knopf oder T */
  function applyTheme(t){
    if (t === "dark") { root.setAttribute("data-theme", "dark"); }
    else { root.removeAttribute("data-theme"); }
    if (themeBtn) { themeBtn.firstChild.textContent = t === "dark" ? label.light : label.dark; }
    try { localStorage.setItem("deck-theme", t); } catch (e) {}
  }
  function toggleTheme(){ applyTheme(root.hasAttribute("data-theme") ? "light" : "dark"); }
  var saved = null;
  try { saved = localStorage.getItem("deck-theme"); } catch (e) {}
  applyTheme(saved === "dark" ? "dark" : "light");

  function toggleNotes(){ if (notesText) { document.body.classList.toggle("show-notes"); } }
  function toggleFullscreen(){
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else if (root.requestFullscreen) { root.requestFullscreen(); }
  }

  function on(id, fn){ var el = document.getElementById(id); if (el) { el.addEventListener("click", fn); } }
  on("themeBtn", toggleTheme);
  on("notesBtn", toggleNotes);
  on("fsBtn", toggleFullscreen);
  on("nextBtn", next);
  on("prevBtn", prev);

  /* Tastatur — im Lesemodus scrollen die Pfeiltasten wie gewohnt */
  document.addEventListener("keydown", function(e){
    if (!isDeck()) {
      if (e.key === "t" || e.key === "T") { toggleTheme(); }
      return;
    }
    if (e.target && (e.target.tagName === "VIDEO" || e.target.tagName === "BUTTON")) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") { return; }
    }
    switch (e.key) {
      case "ArrowRight": case "ArrowDown": case "PageDown": case " ":
        e.preventDefault(); next(); break;
      case "ArrowLeft": case "ArrowUp": case "PageUp":
        e.preventDefault(); prev(); break;
      case "Home": e.preventDefault(); go(0); break;
      case "End": e.preventDefault(); go(slides.length - 1); break;
      case "t": case "T": toggleTheme(); break;
      case "n": case "N": toggleNotes(); break;
      case "f": case "F": toggleFullscreen(); break;
    }
  });

  /* Klick: rechts weiter, linkes Drittel zurück — Bedienelemente ausgenommen */
  document.getElementById("deck").addEventListener("click", function(e){
    if (!isDeck() || e.target.closest("video,button,a,.player,.notes-panel")) { return; }
    if (e.clientX < window.innerWidth / 3) { prev(); } else { next(); }
  });

  /* Wischen */
  var tx = null, ty = null;
  document.addEventListener("touchstart", function(e){
    if (!isDeck() || e.target.closest(".player,.notes-panel")) { tx = null; return; }
    tx = e.changedTouches[0].clientX; ty = e.changedTouches[0].clientY;
  }, { passive: true });
  document.addEventListener("touchend", function(e){
    if (tx === null) { return; }
    var dx = e.changedTouches[0].clientX - tx;
    var dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) { if (dx < 0) { next(); } else { prev(); } }
    tx = null;
  }, { passive: true });

  /* Startknopf der Player; „started“ auch bei Start über die native Leiste */
  Array.prototype.forEach.call(document.querySelectorAll(".player"), function(p){
    var v = p.querySelector("video");
    var b = p.querySelector(".start button");
    if (!v) { return; }
    if (b) { b.addEventListener("click", function(){ v.play(); }); }
    v.addEventListener("play", function(){ p.classList.add("started"); });
  });

  /* Untertitel als <script type="text/vtt"> in der Datei (Versandfassung): eine Blob-Adresse
   * hat denselben Ursprung wie die Seite und lädt deshalb auch über file:// */
  Array.prototype.forEach.call(document.querySelectorAll("track[data-vtt]"), function(t){
    var src = document.getElementById(t.getAttribute("data-vtt"));
    if (!src) { return; }
    try { t.src = URL.createObjectURL(new Blob([src.textContent.replace(/^\s+/, "")], { type: "text/vtt" })); } catch (e) {}
  });

  /* Fenstergröße ändert sich (Drehen, Verkleinern): Modus neu bestimmen */
  function applyMode(){ if (!root.classList.contains("pdf")) { root.classList.toggle("deck", deckMQ.matches); } go(idx); }
  if (deckMQ.addEventListener) { deckMQ.addEventListener("change", applyMode); }
  else if (deckMQ.addListener) { deckMQ.addListener(applyMode); }

  var start = parseInt((location.hash || "").replace("#", ""), 10);
  go(isNaN(start) ? 0 : start - 1);
  window.deckGo = go; /* für pruefen.js */
})();
