const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: "new", args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

  // We need to serve the dist folder to test the actual build
  const { exec } = require('child_process');
  const server = exec('npx serve -s dist -p 5000');
  
  await new Promise(r => setTimeout(r, 2000)); // wait for server to start

  await page.goto('http://localhost:5000/analytics');
  await new Promise(r => setTimeout(r, 3000));
  
  await browser.close();
  server.kill();
})();
