const url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text";

async function get_proxies(url) {
    var data = await fetch(url);
    var text = await data.text();
    const proxies = text.split(/\r?\n/).filter(line => line.trim() !== ""); // Split and remove empty lines
    return proxies;
}

async function main() {
    let result = await get_proxies(url);
    console.log(result);
}

main();