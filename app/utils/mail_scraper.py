import requests
import random
import re
from fastapi.responses import JSONResponse

def extract_emails(text: str) -> list[str]:
    """
    Extract all email addresses from the given text.
    Returns them in lowercase, excluding obvious image‑file names.
    """
    if not text:
        return []
    # Simpler pattern: match word characters, dots, underscores, percent, plus, hyphen,
    # then '@', then domain chars, then a dot and 2+ letters.
    email_pattern = r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b'

    # Find all, lowercase them, filter out image filenames
    raw_emails = re.findall(email_pattern, text)
    return [
        email.lower()
        for email in raw_emails
        if not email.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    ]

def get_twitter_id(url: str):
    pattern = r"(?:https?://)?(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})"
    match = re.search(pattern, url)
    return match.group(1)

def scrape_twitter(url: str):
    """
    Scrapes about session for emails
    :param url:
    :return: list containing all found mails
    """
    id = get_twitter_id(url)
    url = f"https://www.twitterviewer.com/{id}"
    USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Safari macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    # Safari iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
    ]
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        text = response.text
        mails = extract_emails(text)
        return mails
    else:
        return

def scrapeEmails(links: list[str]):
    mails = []
    for link in links:
        if "twitter" in link.lower() or "x.com" in link.lower():
            mails.extend(scrape_twitter(link))
    return JSONResponse(status_code=200, content={"mails": mails})

