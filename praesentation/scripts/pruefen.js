// Prüft eine Präsentation in Headless-Chromium und meldet Befunde (Exit-Code 1, wenn es welche gibt).
//   Präsentation 1366×768 und 1920×1080, hell und dunkel, jede Folie:
//     - Überlauf: Inhalt ragt aus der Folie oder aus einem Container mit overflow≠visible
//     - Bilder geladen (complete, naturalWidth > 0)
//     - optional Mindest-Schriftgröße im Folieninhalt (--min-schrift 24)
//   Lesemodus 390×844 (mit und ohne JavaScript) und 1366×768 ohne JavaScript:
//     - alle Folien sichtbar, kein seitlicher Überlauf der Seite
// Aufruf:  node pruefen.js <deck.html> [--bilder <ordner>] [--min-schrift 24]
// (Playwright nötig — Docker-Befehl in SKILL.md, Abschnitt „Werkzeuge“)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

let datei = null, BILDER = null, MIN_SCHRIFT = null;
for (let i = 2; i < process.argv.length; i++) {
  const a = process.argv[i];
  if (a === '--bilder') { BILDER = process.argv[++i]; }
  else if (a === '--min-schrift') { MIN_SCHRIFT = Number(process.argv[++i]); }
  else { datei = a; }
}
if (!datei) { console.error('Aufruf: node pruefen.js <deck.html> [--bilder <ordner>] [--min-schrift 24]'); process.exit(2); }
const URL = 'file://' + path.resolve(datei);
if (BILDER) { fs.mkdirSync(BILDER, { recursive: true }); }

const befunde = [];
const melde = (wo, was) => befunde.push(`${wo}: ${was}`);

async function folieMessen(page, minSchrift) {
  return page.evaluate((minSchrift) => {
    const s = document.querySelector('.slide.active');
    const sr = s.getBoundingClientRect();
    const out = [];
    const name = (el) => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
    if (s.scrollHeight > s.clientHeight + 1) { out.push(`Folie läuft unten über (${s.scrollHeight - s.clientHeight} px)`); }
    if (s.scrollWidth > s.clientWidth + 1) { out.push(`Folie läuft rechts über (${s.scrollWidth - s.clientWidth} px)`); }
    s.querySelectorAll('*').forEach((el) => {
      if (el.closest('.notes') || el.closest('svg') && el.tagName.toLowerCase() !== 'svg') { return; }
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') { return; }
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) { return; }
      if (r.bottom > sr.bottom + 1 || r.right > sr.right + 1 || r.left < sr.left - 1 || r.top < sr.top - 1) {
        out.push(`${name(el)} ragt aus der Folie`);
      }
      if (cs.overflow !== 'visible' && el.tagName.toLowerCase() !== 'video' && !el.classList.contains('diagram-wrap')
          && (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)) {
        out.push(`${name(el)} schneidet Inhalt ab`);
      }
      if (el.tagName === 'IMG' && !(el.complete && el.naturalWidth > 0)) { out.push(`Bild nicht geladen: ${el.getAttribute('src').slice(0, 80)}`); }
      if (minSchrift) {
        const eigenerText = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
        const fs = parseFloat(cs.fontSize);
        if (eigenerText && fs < minSchrift - 0.5) { out.push(`${name(el)} mit ${fs} px unter ${minSchrift} px: „${el.textContent.trim().slice(0, 40)}“`); }
      }
    });
    return Array.from(new Set(out));
  }, minSchrift);
}

(async () => {
  const browser = await chromium.launch();

  // Präsentationsmodus
  for (const [w, h] of [[1366, 768], [1920, 1080]]) {
    for (const thema of ['hell', 'dunkel']) {
      const page = await browser.newPage({ viewport: { width: w, height: h } });
      await page.goto(URL);
      await page.evaluate(() => document.fonts.ready);
      const n = await page.evaluate((dunkel) => {
        if (!document.documentElement.classList.contains('deck')) { return -1; }
        if (dunkel) { document.documentElement.setAttribute('data-theme', 'dark'); }
        else { document.documentElement.removeAttribute('data-theme'); }
        return document.querySelectorAll('.slide').length;
      }, thema === 'dunkel');
      if (n < 0) { melde(`${w}×${h}`, 'Präsentationsmodus nicht aktiv'); await page.close(); continue; }
      await page.waitForFunction(() => Array.from(document.images).every((i) => i.complete), null, { timeout: 15000 }).catch(() => {});
      for (let i = 0; i < n; i++) {
        await page.evaluate((k) => window.deckGo(k), i);
        const wo = `Folie ${String(i + 1).padStart(2, '0')} · ${w}×${h} · ${thema}`;
        (await folieMessen(page, MIN_SCHRIFT)).forEach((b) => melde(wo, b));
        if (BILDER) { await page.screenshot({ path: path.join(BILDER, `folie-${String(i + 1).padStart(2, '0')}-${w}x${h}-${thema}.png`) }); }
      }
      await page.close();
    }
  }

  // Lesemodus
  for (const [w, h, js] of [[390, 844, true], [390, 844, false], [1366, 768, false]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, javaScriptEnabled: js });
    const page = await ctx.newPage();
    await page.goto(URL);
    const wo = `Lesemodus ${w}×${h}${js ? '' : ' ohne JS'}`;
    const r = await page.evaluate(() => ({
      deck: document.documentElement.classList.contains('deck'),
      quer: document.documentElement.scrollWidth - window.innerWidth,
      folien: document.querySelectorAll('.slide').length,
      sichtbar: Array.from(document.querySelectorAll('.slide')).filter((s) => s.offsetHeight > 0).length,
    }));
    if (r.deck) { melde(wo, 'steht im Präsentationsmodus statt im Lesemodus'); }
    if (r.quer > 1) { melde(wo, `seitlicher Überlauf (${r.quer} px)`); }
    if (r.sichtbar !== r.folien) { melde(wo, `nur ${r.sichtbar} von ${r.folien} Folien sichtbar`); }
    if (BILDER) { await page.screenshot({ path: path.join(BILDER, `lesemodus-${w}x${h}${js ? '' : '-ohne-js'}.png`), fullPage: true }); }
    await ctx.close();
  }

  await browser.close();
  if (befunde.length) {
    console.log(`${befunde.length} Befund(e):`);
    befunde.forEach((b) => console.log('  - ' + b));
    process.exit(1);
  }
  console.log('keine Befunde');
})().catch((e) => { console.error(e); process.exit(1); });
