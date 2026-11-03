const { chromium } = require('playwright');
// Uso: node envia_dropbox.js EMAIL ARQUIVO1.mp4 [ARQUIVO2.mp4 ...]
// Envia para a pasta Dropbox "fotos dani" pela solicitação de arquivo h8mnnh4sl065msqmy8i2 (aberta, sem prazo).
const email = process.argv[2] || '';
const files = process.argv.slice(3);
(async () => {
  const b = await chromium.launch({ args: ['--ignore-certificate-errors'] });
  const p = await b.newPage({ viewport: { width: 1200, height: 900 } });
  await p.goto('https://www.dropbox.com/request/h8mnnh4sl065msqmy8i2', { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(3000);
  await p.click('text=Add files');
  await p.waitForTimeout(1000);
  const [fc] = await Promise.all([p.waitForEvent('filechooser', { timeout: 20000 }), p.click('text=Files from computer')]);
  await fc.setFiles(files);
  await p.waitForTimeout(3000);
  await p.fill('input[name=name]', 'Claude - edicao estilo sardinha');
  if (email) await p.fill('input[name=email]', email);
  await p.click('button:has-text("Upload")');
  for (let i = 0; i < 60; i++) {
    await p.waitForTimeout(5000);
    const txt = (await p.innerText('body')).replace(/\n+/g, ' | ');
    if (/uploaded|Enviado|success|Done|You've uploaded|Upload complete/i.test(txt) && !/Uploading/i.test(txt)) { console.log('FIM', txt.slice(0, 500)); break; }
    if (i % 4 === 0) console.log('...', txt.slice(0, 300));
  }
  await p.screenshot({ path: 'p7.png' });
  await b.close();
})();
