// Renders branding/logo.svg into every app icon CallenVoice ships.
// Usage: node scripts/callen/build_icons.mjs   (needs Playwright's Chromium and Python Pillow)
// Outputs to electron/build/icons: icon.png (1024), icon-macos.png and icon.icns
// (Apple grid: tile at 824/1024, centred), icon.ico (16–256), 32x32.png.
import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const svg = readFileSync(resolve(root, 'branding/logo.svg'), 'utf8');
const out = resolve(root, 'electron/build/icons');
const tmp = resolve(root, 'branding/.render');
mkdirSync(tmp, { recursive: true });

// CHROMIUM_PATH lets a machine reuse an already installed Chromium.
const browser = await chromium.launch(
  process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {},
);
const page = await browser.newPage({ viewport: { width: 1024, height: 1024 } });
async function render(file, tile) {
  const pad = (1024 - tile) / 2;
  await page.setContent(
    `<html><body style="margin:0;background:transparent">` +
      `<div style="position:absolute;left:${pad}px;top:${pad}px;width:${tile}px;height:${tile}px">` +
      svg.replace('<svg ', `<svg width="${tile}" height="${tile}" `) +
      `</div></body></html>`,
  );
  await page.screenshot({ path: file, omitBackground: true, clip: { x: 0, y: 0, width: 1024, height: 1024 } });
}
await render(`${tmp}/full.png`, 1024);
await render(`${tmp}/mac.png`, 824);
await browser.close();

execFileSync('python3', ['-c', `
from PIL import Image
full = Image.open("${tmp}/full.png").convert("RGBA")
mac = Image.open("${tmp}/mac.png").convert("RGBA")
full.save("${out}/icon.png")
full.resize((32, 32), Image.LANCZOS).save("${out}/32x32.png")
full.save("${out}/icon.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
mac.save("${out}/icon-macos.png")
mac.save("${out}/icon.icns")
`], { stdio: 'inherit' });
console.log('icons written to', out);
