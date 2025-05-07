import requests
import subprocess, json
from typing import Union
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright

import socket
import random
import re
import time
import functools
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
load_dotenv()
class AnyValue:
    """
    A class that returns the constructor value passed for any comparison operations
    """
    def __init__(self, choice: bool):
        self.value = choice
    def __eq__(self, other):
        return self.value
    def __ne__(self, other):
        return self.value
    def __lt__(self, other):
        return self.value
    def __le__(self, other):
        return self.value
    def __gt__(self, other):
        return self.value
    def __ge__(self, other):
        return self.value


def convert_to_percentage(value: int, max_value: int) -> int:
    """
    Converts a value to a percentage based on the given min and max values.
    :param value:
    :param max_value:
    :return:
    """ 
    if max_value == 0:
        return 0.0  # Avoid division by zero
    return round((value / max_value) * 100)
    # return int(percentage) 



def classify(choice_l: str, min_viewer_c: int, streams: dict):
    if choice_l == streams['language']:
        if int(min_viewer_c) < int(streams['viewer_count']):
            return True
        else:
            return False
    else:
        return False


def is_valid_text(text: str) -> bool:
    pattern = r'^[a-zA-Z0-9~`!@#$%^&*()_\-+={}\[\]:;"\'<>,.?/\\| ]+$'
    return bool(re.match(pattern, text))
def get_subscriber_count(channel_url):
    response = requests.get(channel_url)
    match = re.search(r"(\d+(\.\d+)?[KM]?)\s+subscribers", response.text)
    if match:
        num_str = match.group(1)
        if "K" in num_str:
            return int(float(num_str.replace("K", "")) * 1000)
        elif "M" in num_str:
            return int(float(num_str.replace("M", "")) * 1000000)
        else:
            return int(num_str)
    return None

def is_valid_email(mail_id: str) -> bool:
    """
    :param mail_id:
    :param deliverability_check:
    :return: bool
    """
    try:
        emailinfo = validate_email(mail_id, check_deliverability=True)
        return True
    except EmailNotValidError as e:
        return False

def time_it(func):
    """
    A decorator to check the time taken for execution for different functions
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        #print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper



@time_it
def scrape_twitter_profile(twitter_profile_url):
    """
    Scrapes Twitter profile for gmail
    :param twitter_profile_url:
    :return:
    Dictionary containing the profile info
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0"
    ]

    random_user_agent = random.choice(user_agents)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(user_agent=random_user_agent,proxy={"server": str(get_working_proxy())})
            page = context.new_page()
            page.goto(f'{twitter_profile_url}')
            page.wait_for_selector('[data-testid="UserName"]', timeout=10000)

            display_name_element = page.query_selector('[data-testid="UserName"]')
            display_name = display_name_element.text_content().strip() if display_name_element else "Not found"

            bio_element = page.query_selector('[data-testid="UserDescription"]')
            bio = bio_element.text_content().strip() if bio_element else "No bio"

            join_date_element = page.query_selector('span:has-text("Joined")')
            join_date = join_date_element.text_content().strip() if join_date_element else "Not found"

            followers_element = page.query_selector('[aria-label*="Followers"][role="link"]')
            followers = (followers_element.get_attribute('aria-label').split()[0]
                         if followers_element else "Not found")

            following_element = page.query_selector('[aria-label*="Following"][role="link"]')
            following = (following_element.get_attribute('aria-label').split()[0]
                         if following_element else "Not found")

            browser.close()
    except:
        return {
            "display_name": "",
            "bio": "",
            "join_date": "",
            "followers": "",
            "following": ""
        }
    else:
        return {
            "display_name": display_name,
            "bio": bio,
            "join_date": join_date,
            "followers": followers,
            "following": following
        }
@time_it
def extract_emails(text: str) -> list[str]:
    """
    Extract all email addresses from the given text.
    Returns them in lowercase, excluding obvious image‑file names.
    """
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
@time_it
def get_follower_count(client_id, access_token , user_id=None, user_login=None):
    """
    Returns follower count, requires either userId or user_login
    :param client_id:
    :param access_token:
    :param user_id:
    :param user_login:
    :return:
    """
    try:
        # Check if at least one parameter is provided
        if user_id is None and user_login is None:
            raise ValueError("You must provide either user_id or user_login")

        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}'
        }

        # If user_id is not provided, get it from user_login
        if user_id is None:
            users_url = 'https://api.twitch.tv/helix/users'
            users_params = {'login': user_login}
            users_response = requests.get(users_url, headers=headers, params=users_params)
            users_data = users_response.json()
            if not users_data['data']:
                return None  # User not found
            user_id = users_data['data'][0]['id']

        # Get the follower count using the user_id
        followers_url = 'https://api.twitch.tv/helix/channels/followers'
        followers_params = {'broadcaster_id': user_id, 'first': 1}
        followers_response = requests.get(followers_url, headers=headers, params=followers_params)
        if followers_response.status_code == 200:
            followers_data = followers_response.json()
            return followers_data['total'] #Returns follower count
        else:
            return 0  # Could not get follower count
    except:
        return 0


@time_it
def get_live_streams(game_id: str, client_id, access_token):
    """
    Returns a list of live streams
    user_name = streams[i]['user_name'], similar for viewer count
    :param game_id:
    :return:
    """
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }

    url = "https://api.twitch.tv/helix/streams"
    params = {
        "game_id": game_id,
        "first": 50  # Max results per request
    }

    all_streams = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        all_streams.extend(data["data"])

        # Check if there's a next page
        pagination = data.get("pagination", {}).get("cursor")
        if not pagination:
            break  # No more data

        # Set cursor for next request
        params["after"] = pagination

        # Wait for 80ms before next request (Since Twitch free tier API is refilled every 75ms)
        time.sleep(0.08)

    return all_streams
# @time_it
def scrape_twitch_about(url):
    """Scrapes the about part of a twitch user
        :param Twitch about url
        :return data: A json file
    """
    # script_path = os.path.join(os.path.dirname(__file__), 'JS_components', 'scraper.js')

    try:
        # Execute the Node.js script with the URL as an argument
        result = subprocess.run(
            ['node', r'Scrapers/JS_components/scraper.js', url],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the JSON output from the Node.js script
        # print(f"RESULT IS {result} and STDOUT THINGY IS {result.stdout}")
        # print(result.stdout)
        return result.stdout
        # data = json.loads(result.stdout)
        # #print(data)
        # return data

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")
        return {"links":"", "email":""}



def get_twitch_game_id(client_id: str, access_token: str, game_name: str) -> int:
    url = "https://api.twitch.tv/helix/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    params = {"name": game_name}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
        else:
            raise ValueError("Game not found")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


@time_it
def scrape_youtube(channel_url: Union[list, set]):
    """
    Scrapes about session for emails
    :param channel_url:
    :return: list containing all found mails
    """
    mails = []
    try:
        for link in channel_url:
            response = requests.get(link)
            mails.extend(str(i).lower() for i in set(extract_emails(response.text)))
        return mails
    except:
        return mails
def is_proxy_alive(ip, port, timeout=3):
    """
    Check if a proxy server at given IP and port is alive.

    Returns True if reachable, False otherwise.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False
    
def get_working_proxy():
    url = "https://api.proxyscrape.com/v2/?request=getproxies&proxytype=https&timeout=10000&country=all"
    valid_ports = [80, 8080, 3128, 1080, 8888, 443]
    response = requests.get(url)
    proxies = response.text.split("\r\n")
    for proxy in proxies:
        if 'https' not in proxy:
            ip, port = proxy.split(":")
            if int(port) in valid_ports:
                if is_proxy_alive(ip, port):
                    print(f"Working proxy found: {proxy}")
                    return f"http://{proxy}"
    return None
if __name__ == '__main__':
    get_working_proxy()
