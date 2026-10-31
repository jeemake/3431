// node render3d.js outdir  -> rend axo_A_sw.png etc.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
  const root = path.join(__dirname, 'web'); const data = path.join(__dirname, '..', 'build', '3d', 'scenes.json');
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
  await p.route('http://local/**', r => { const f = r.request().url().split('/').pop().split('?')[0];
    const fp = f === 'scenes.json' ? data : path.join(root, f);
    r.fulfill({ body: fs.readFileSync(fp), contentType: f.endsWith('.js') ? 'text/javascript' : f.endsWith('.json') ? 'application/json' : 'text/html' }); });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('err:', e.message));
  for (const [v, cam, z] of [['A', 'sw', 1.15], ['B', 'sw', 1.15], ['C', 'sw', 1.15], ['A', 'se', 1.2], ['B', 'se', 1.2], ['C', 'se', 1.2]]) {
    await p.goto(`http://local/render.html?v=${v}&cam=${cam}&z=${z}`); await p.waitForFunction(() => window.done, null, { timeout: 120000 });
    await p.screenshot({ path: path.join(out, `axo3d_${v}_${cam}.png`) }); console.log('ok', v, cam);
  }
  await b.close();
})();
