import puppeteer from 'puppeteer';
import { exec } from 'child_process';

(async () => {
  const browser = await puppeteer.launch({ headless: "new", args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  const server = exec('npm run preview -- --port 5000');
  
  await new Promise(r => setTimeout(r, 3000)); // wait for server to start

  await page.goto('http://localhost:5000/CRSAccounting/analytics');
  await new Promise(r => setTimeout(r, 4000));
  
  const bodyHTML = await page.evaluate(() => document.body.innerHTML);
  if (bodyHTML.includes('ERROR:')) {
    console.log('FOUND ERROR ON PAGE:', bodyHTML.substring(bodyHTML.indexOf('ERROR:'), bodyHTML.indexOf('ERROR:') + 500));
  } else {
    console.log('NO ERROR FOUND ON PAGE.');
  }
  
  await browser.close();
  server.kill();
})();
