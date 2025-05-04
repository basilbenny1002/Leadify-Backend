const puppeteer = require('puppeteer');

// List of common user agents
const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0'
];

async function scrapeTwitchAbout(url) {
    const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];

    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
    const page = await browser.newPage();

    await page.setUserAgent(randomUserAgent);

    await page.goto(url, { waitUntil: 'networkidle2' });

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

    const pageHTML = await page.content();
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const emailsFromHTML = pageHTML.match(emailRegex) || [];

    const emails = [...new Set([...emailsFromText, ...emailsFromHTML])];

    await browser.close();

    return { links, emails };
}

const url = process.argv[2];
scrapeTwitchAbout(url).then(result => {
    console.log(JSON.stringify(result, null, 2));
}).catch(error => {
    console.error('Error:', error);
});
