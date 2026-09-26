import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  // We can't hit github.io immediately because it might be cached or require login.
  // We can serve the dist folder locally and test it!
  
  await browser.close();
})();
