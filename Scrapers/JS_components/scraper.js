const puppeteer = require('puppeteer');

// List of common user agents
const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0'
];
const net = require('net');
const working_proxy = ""

const proxy_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text";
const allowedPorts = [8080, 3128, 8000, 8888];

function isProxyAlive(ip, port) {
    return new Promise(resolve => {
        const socket = new net.Socket();
        socket.setTimeout(3000);

        socket.on('connect', () => {
            socket.destroy();
            resolve(true);
        });

        socket.on('error', () => resolve(false));
        socket.on('timeout', () => {
            socket.destroy();
            resolve(false);
        });

        socket.connect(port, ip);
    });
}

async function get_proxies(url) {
    var data = await fetch(url);
    var text = await data.text();
    const proxies = text.split(/\r?\n/).filter(line => line.trim() !== ""); // Split and remove empty lines
    return proxies;
}
async function findFirstAliveProxy(proxyList) {
    for (const proxy of proxyList) {
        try {
            const url = new URL(proxy);
            const ip = url.hostname;
            const port = parseInt(url.port);

            if (!port || !allowedPorts.includes(port)) {
                console.log(`Skipping ${proxy} — invalid or unsupported port`);
                continue;
            }

            const alive = await isProxyAlive(ip, port);
            if (alive) {
                foundProxy = { ip, port };
                console.log(`✅ Found working proxy: ${ip}:${port}`);
                return `${ip}:${port}`;
                
            } else {
                console.log(`❌ Dead proxy: ${ip}:${port}`);
            }

        } catch (error) {
            console.log(`Skipping invalid proxy format: ${proxy}`);
        }
    }

    if (foundProxy) {
        console.log('✅ Final chosen proxy:', foundProxy);
    } else {
        console.log('❌ No working proxy found.');
    }
}

async function main() {
    let proxy_list = await get_proxies(proxy_url);
    const working_proxy = await findFirstAliveProxy(proxy_list)

    console.log(working_proxy);
}

main();

async function scrapeTwitchAbout(url) {
    const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];

    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--proxy-server='+working_proxy
        ]
    });

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
