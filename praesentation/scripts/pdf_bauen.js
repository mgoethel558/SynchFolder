// Baut aus der Versandfassung die PDF-Fassung: eine Folie pro Seite (1920 × 1080),
// helles Farbschema, Videos als antippbare Links (.pdf-play / .video-link).
// Aufruf:  node pdf_bauen.js <versand.html> <ausgabe.pdf>
// (Playwright nötig — Docker-Befehl in SKILL.md, Abschnitt „Werkzeuge“)
const path = require('path');
const { chromium } = require('playwright');

const [, , htmlArg, pdfArg] = process.argv;
if (!htmlArg || !pdfArg) {
  console.error('Aufruf: node pdf_bauen.js <versand.html> <ausgabe.pdf>');
  process.exit(2);
}
const HTML = path.resolve(htmlArg);
const PDF = path.resolve(pdfArg);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + HTML);
  await page.evaluate(() => {
    const r = document.documentElement;
    r.classList.add('deck', 'pdf');
    r.removeAttribute('data-theme');
    document.body.classList.remove('on-brand', 'show-notes');
    // Chromium druckt sonst die Videoleiste (Abspielknopf, 0:00) über das Vorschaubild
    document.querySelectorAll('video').forEach((v) => v.removeAttribute('controls'));
  });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => Array.from(document.images).every((i) => i.complete && i.naturalWidth > 0));
  await page.pdf({
    path: PDF, width: '1920px', height: '1080px', printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  await browser.close();
  console.log('geschrieben:', PDF);
})().catch((e) => { console.error(e); process.exit(1); });
