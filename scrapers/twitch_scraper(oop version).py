from abc import ABCMeta, abstractmethod
import os
import requests
import re
import time

class Creator:
    def __init__(self, user_name, channel_id, viewer_count, language, followers, category ):
        self.user_name = user_name
        self.channel_url = f"https://www.twitch.tv/{self.user_name}"
        self._channel_id = channel_id
        self.viewer_count = viewer_count
        self.language = language
        self.followers = followers
        self.youtube = ""
        self.subscriber_count = 0
        self.discord = ""
        self.twitter = ""
        self.instagram = ""
        self.twitch = ""
        self.linkedin = ""
        self.facebook = ""
        self.tiktok = ""
        self.mail = ""
        self.category = category

    def scrape_twitch(self):
        raise NotImplementedError

    def scrape_youtube(self):
        raise NotImplementedError

    def scrape_instagram(self):
        raise NotImplementedError
    
    
class Scrape:
    def __init__(self, max_followers: int, min_followers: int, viewer_count: int, user_id: str, game_id: str, language: str):
        self.access_token = os.getenv("access_token") 
        self.client_id = os.getenv("client_id") 
        self.max_followers = max_followers
        self.min_followers = min_followers
        self.viewer_count = viewer_count
        self.user_id = user_id
        self.game_id = game_id
        # self.game_name
        self.language = language
        self.streamers = self.get_streams()    
        self.stage
        self.all_streamer_count = len(self.streamers)
        self.filtered_streamers = []
        self.processed_data 
        

    def get_streams(self):
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        url = "https://api.twitch.tv/helix/streams"
        params = {
            "game_id": self.game_id,
            "first": 50  # Max results per request
        }

        all_streams = []
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            all_streams.extend(data["data"])
            pagination = data.get("pagination", {}).get("cursor")
            if not pagination:
                break  
            params["after"] = pagination
            time.sleep(0.08)
        return all_streams


        # raise NotImplemented
    def filter_streamer(self):
        for i in range(self.all_streamer_count):
            follower_count = self.get_follower_count(self.streamers[i]["user_id"])
            if follower_count > self.min_followers and follower_count < int(self.max_follower) and self.classify(choice_l=self.language, min_viewer_c=self.viewer_count, streams=self.streamers[i]) and self.is_valid_text(self.streamers[i]["user_name"]):        
                self.filtered_streamers.append(Creator(self.streamers[i]['user_name'], 
                                                       self.streamers[i]['user_id'], 
                                                       self.streamers[i]['viewer_count'], 
                                                       self.streamers[i]['language'],  
                                                       follower_count, 
                                                       self.streamers[i]['game_name']))
                                                       
            #     self.filtered_streamers.append({
            #     'username': self.streamers[i]['user_name'],
            #     "channel_id": self.streamers[i]['user_id'],
            #     'channel_url': f"https://www.twitch.tv/{self.streamers[i]['user_name']}",
            #     'followers': self.streamers[i]['followers'],
            #     'viewer_count': self.streamers[i]['viewer_count'],
            #     'language': self.streamers[i]['language'],
            #     'game_name': self.streamers[i]['game_name'],
            #     'discord': [],
            #     'youtube': [],
            #     'subscriber_count': 0,
            #     'gmail': [],
            #     "instagram": [],
            #     "twitter": [],
            #     "facebook":[],
            #     "tiktok": [],
            #     "linkedin": []
            # })

    def classify(self, streams):
        if self.language == streams['language']:
            if int(self.min_viewer_c) < int(streams['viewer_count']):
                return True
            else:
                return False
        else:
            return False
    def get_follower_count(self, user_id):
        try:
            # Check if at least one parameter is provided
            if user_id is None :
                raise ValueError("You must provide either user_id or user_login")

            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}'
            }
            followers_url = 'https://api.twitch.tv/helix/channels/followers'
            followers_params = {'broadcaster_id': user_id, 'first': 1}
            followers_response = requests.get(followers_url, headers=headers, params=followers_params)
            if followers_response.status_code == 200:
                followers_data = followers_response.json()
                return followers_data['total'] 
            else:
                return 0  # Could not get follower count
        except:
            return 0
        

    def is_valid_text(text: str) -> bool:
        pattern = r'^[a-zA-Z0-9~`!@#$%^&*()_\-+={}\[\]:;"\'<>,.?/\\| ]+$'
        return bool(re.match(pattern, text))
