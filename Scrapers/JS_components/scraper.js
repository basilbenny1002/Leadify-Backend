
const puppeteer = require('puppeteer');

async function scrapeTwitchAbout(url) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    await page.goto(url, { waitUntil: 'networkidle2' });

    // Extract social media links
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

    // Extract emails from page text
    const emailsFromText = await page.evaluate(() => {
        const text = document.body.innerText;
        const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
        return text.match(emailRegex) || [];
    });

    // Extract emails from the entire HTML source
    const pageHTML = await page.content();
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const emailsFromHTML = pageHTML.match(emailRegex) || [];

    // Merge and remove duplicates
    const emails = [...new Set([...emailsFromText, ...emailsFromHTML])];

    await browser.close();

    return { links, emails };
}

// Retrieve the URL from command-line arguments
const url = process.argv[2];
scrapeTwitchAbout(url).then(result => {
    console.log(JSON.stringify(result, null, 2));
}).catch(error => {
    console.error('Error:', error);
});
