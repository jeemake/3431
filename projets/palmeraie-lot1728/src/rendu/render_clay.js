// usage : node render_clay.js <html> <scene.json> <out.png> '<cam json>'
const { chromium } = require('playwright');
(async () => {
  const [html, scene, out, cam] = process.argv.slice(2);
  const b = await chromium.launch({args: ['--allow-file-access-from-files', '--use-gl=swiftshader']});
  const p = await b.newPage({viewport: {width: 1600, height: 1000}});
  p.on('console', m => console.log('console:', m.text()));
  p.on('pageerror', e => console.log('err:', e.message));
  await p.addInitScript(s => { window.SCENE = s; }, JSON.parse(require('fs').readFileSync(scene, 'utf8')));
  const url = 'file://' + html + '?cam=' + encodeURIComponent(cam);
  await p.goto(url);
  await p.waitForFunction(() => document.title === 'done', null, {timeout: 120000});
  await (await p.$('canvas')).screenshot({path: out});
  await b.close();
})();
