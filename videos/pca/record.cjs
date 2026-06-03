// Playwright record — Tecator PCA video. total 260s, record 260.8s
const { chromium } = require('playwright'); const path = require('path');
const PROJECT_DIR = __dirname;
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required','--mute-audio','--no-sandbox','--disable-setuid-sandbox'] });
  const context = await browser.newContext({ viewport:{width:1920,height:1080}, deviceScaleFactor:1, recordVideo:{dir:path.join(PROJECT_DIR,'renders'),size:{width:1920,height:1080}} });
  const page = await context.newPage();
  page.on('pageerror', err => console.error('PAGE ERROR:', err.message));
  await page.goto('file:///' + path.join(PROJECT_DIR,'index.html').replace(/\\/g,'/') + '?render=true');
  console.log('Recording 260.8s...'); await page.waitForTimeout(260800);
  await context.close(); await browser.close(); console.log('done');
})();
