const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [dir, out] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage();
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    await p.setContent(`<html><body style="margin:0;background:#fff">${fs.readFileSync(path.join(dir, f), 'utf8')}</body></html>`);
    await (await p.$('svg')).screenshot({ path: path.join(out, f.replace('.svg', '.png')) });
  }
  await b.close();
})();
