const puppeteer = require('puppeteer');

async function scrapeEmailsFromPages(urls) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    let allEmails = new Set();

    for (const url of urls) {
        try {
            await page.goto(url, { waitUntil: 'networkidle2' });

            // Extract emails from page text
            const emailsFromText = await page.evaluate(() => {
                const text = document.body.innerText;
                const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
                return text.match(emailRegex) || [];
            });

            // Extract emails from full HTML
            const pageHTML = await page.content();
            const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
            const emailsFromHTML = pageHTML.match(emailRegex) || [];

            // Combine emails
            const combinedEmails = [...emailsFromText, ...emailsFromHTML];

            // Filter gmails only and add to the set
            combinedEmails.forEach(email => {
                if (email.toLowerCase().includes('@gmail.com')) {
                    allEmails.add(email.toLowerCase());
                }
            });

        } catch (error) {
            console.error(`Failed to scrape ${url}:`, error.message);
        }
    }

    await browser.close();

    // Return as an array
    return Array.from(allEmails);
}

// Read input URLs from command-line arguments (as JSON string)
async function main() {
    const input = process.argv[2];

    if (!input) {
        console.error('No input URLs provided.');
        process.exit(1);
    }

    let urls;
    try {
        urls = JSON.parse(input);
        if (!Array.isArray(urls)) {
            throw new Error('Input must be an array of URLs.');
        }
    } catch (error) {
        console.error('Invalid input:', error.message);
        process.exit(1);
    }

    const emails = await scrapeEmailsFromPages(urls);

    console.log(JSON.stringify(emails, null, 2));
}

main();
