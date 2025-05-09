
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const userAgents = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
  "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
];

async function scrapeTwitchAbout(url) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];
  await page.setUserAgent(randomUserAgent);

  let result = {
    links: [],
    emails: [],
    html: '',
    error: null
  };

  try {
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 120000 // 2 minutes
    });
  } catch (err) {
    result.error = 'Timeout or navigation error: ' + err.message;
  }

  try {
    result.html = await page.content();

    const [links, emailsFromText] = await Promise.all([
      page.evaluate(() => {
        return Array.from(document.querySelectorAll('a[href]'))
          .map(a => a.href)
          .filter(link =>
            link.includes('twitter.com') ||
            link.includes('instagram.com') ||
            link.includes('youtube.com') ||
            link.includes('tiktok.com') ||
            link.includes('discord.gg') ||
            link.includes('facebook.com') ||
            link.includes('linkedin.com')
          );
      }),
      page.evaluate(() => {
        const text = document.body.innerText;
        const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
        return text.match(emailRegex) || [];
      })
    ]);

    const emailsFromHTML = result.html.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [];

    result.links = links;
    result.emails = [...new Set([...emailsFromText, ...emailsFromHTML])];
  } catch (innerErr) {
    result.error = 'Scraping failed: ' + innerErr.message;
  } finally {
    await browser.close();
  }

  return result;
}

const url = process.argv[2];

if (!url) {
  console.error('Please provide a URL as an argument.');
  process.exit(1);
}

scrapeTwitchAbout(url)
  .then(result => console.log(JSON.stringify(result, null, 2)))
  .catch(err => console.error('Unhandled error:', err));

