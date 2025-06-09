from dotenv import load_dotenv
from pathlib import Path
import json 
import os
import requests
from dotenv import load_dotenv
load_dotenv()
def get_twitch_live_categories(max_pages=696969): #Funny number
    headers = {
        'Client-ID': os.getenv('client_id'),
        'Authorization': f"Bearer {os.getenv('access_token')}"
    }

    url = 'https://api.twitch.tv/helix/streams'
    params = {
        'first': 100,  # Max per page
    }

    category_viewers = {}
    pages_fetched = 0

    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code} {response.text}")
        
        data = response.json()
        for stream in data['data']:
            category = stream['game_name']
            viewers = stream['viewer_count']
            if category in category_viewers:
                category_viewers[category] += viewers
            else:
                category_viewers[category] = viewers

        # Pagination
        if 'pagination' in data and 'cursor' in data['pagination']:
            params['after'] = data['pagination']['cursor']
            pages_fetched += 1
        else:
            break
    sorted_category_viewers = dict(sorted(category_viewers.items(), key=lambda item: item[1], reverse=True))
    # return category_viewers
    with open(r"Leadify-Backend\app\utils\datas\live_data.json", "w", encoding="utf-8") as f:
        # print(category_viewers[50:])
        json.dump(sorted_category_viewers,f, indent=2)


def load_config():
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / '.env')

def category_to_id(category: str):
    with open(r".\app\utils\datas\categories.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return int(data[category])
                  
if __name__ == "__main__":
    # print(category_to_id("League of Legends"))
    get_twitch_live_categories()
