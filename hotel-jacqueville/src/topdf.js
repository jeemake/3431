const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(inp), { waitUntil: 'networkidle' });
  await p.pdf({ path: out, width: '420mm', height: '297mm', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await b.close();
})();
