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