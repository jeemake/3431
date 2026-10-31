// Usage: node topng.js in.svg out.png [width]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, out, w] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 1 });
  await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  const el = await p.$('svg'); await el.screenshot({ path: out });
  await b.close();
})();
