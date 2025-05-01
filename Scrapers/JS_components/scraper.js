const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

const userAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
];

// Enable stealth mode
puppeteer.use(StealthPlugin());

async function scrapeTwitchAbout(url) {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];
    await page.setUserAgent(randomUserAgent);

    try {
        await page.goto(url, {
            waitUntil: 'domcontentloaded',
            timeout: 60000
        });

        const pageHTML = await page.content();

        const links = await page.evaluate(() => {
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
        });

        const emailsFromText = await page.evaluate(() => {
            const text = document.body.innerText;
            const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
            return text.match(emailRegex) || [];
        });

        const emailsFromHTML = pageHTML.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [];
        const emails = [...new Set([...emailsFromText, ...emailsFromHTML])];

        return { links, emails, html: pageHTML };

    } catch (error) {
        console.error('Navigation or scraping failed:', error);
        return { links: [], emails: [], html: '', error: error.message };
    } finally {
        await browser.close();
    }
}

// Run the function if URL is passed as argument
const url = process.argv[2];
if (!url) {
    console.error('Please provide a URL as an argument.');
    process.exit(1);
}

scrapeTwitchAbout(url)
    .then(result => console.log(JSON.stringify(result, null, 2)))
    .catch(err => console.error('Unhandled Error:', err));
