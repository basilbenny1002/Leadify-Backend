from abc import ABCMeta, abstractmethod
import os
import requests
import re
import time
import json
import random, string
import requests
import json
import random
import string
import random
import gzip
import zlib
import brotli
import zstandard as zstd
import io
import json
import os
import requests
import re
import time
import io

class Creator:
    def __init__(self, user_name, channel_id, viewer_count, language, followers, category ):
        self.user_name = user_name
        self.channel_url = f"https://www.twitch.tv/{self.user_name}"
        self.channel_id = channel_id
        self.viewer_count = viewer_count
        self.language = language
        self.followers = followers
        self.youtube = []
        self.subscriber_count = 0
        self.discord = []
        self.twitter = []
        self.instagram = []
        self.twitch = []
        self.linkedin = []
        self.facebook = []
        self.tiktok = []
        self.mail = []
        self.category = category

    def scrape_twitch(self):
        time.sleep(random.randint(1, 3)) # Random sleep to avoid rate limiting
        URL = 'https://gql.twitch.tv/gql'
  
        session_id = self.__generate_device_id(16, only_a_to_d=True).lower()
        dev_id = self.__generate_device_id(32)


        HEADERS = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US',
            # 'authorization': '', #NOT NECESSARY
            'client-id': 'kimne78kx3ncx6brgo4mv6wki5h1ko', #HARDCODED CLIENT ID
            'client-session-id': f'{session_id}', #ANY RANDOM ONE SHOUDL WORK
            "client-integrity":"v4.local.XCpudNS28Ah9UCC6dAwSVJhWVxYiHNM7iuIj9uzHArFAt0Hen-ty3Z0fdvRmTeAaa_Z18AguQ1ONWgVaoTssa4aroUvbdqrpjfVsGCWqd_AEAIdkxSKCbpnoNSFv7WlxSLCXIwOjDG6p-TrjOlB5AzH_Q6ujsZK1fFmL4YMNKljr2hPBoGxcFhwgQov3G9uh-RAi-E1zWW6zlNW1xZVCzDha0IXyBC9m9uvFpmRDrwdltT1ogNII8sm-EwY6zqACSk34CNHwzAveGT9Ue7A1buGgRN8hrh6SF9oPEFGL9ThLd_IuUsHJq_AFL3NPbh7J2JcpF2FfJqpUwQaias5BGUuaPE75qvK3SZ6-EpN6lCp7GBHVH3n9Z0bArLFzGEXjczeKEDuY7XR0DLGVA-Sv4jsVBKuegoLBHk6RpZrbSA_xnAzYj2D9WRcw8p-FD0RFH-HzHBfoVvPYQ-Id",
            'client-version': 'de99b9bb-52a9-4694-9653-6d935ab0cbcc',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.twitch.tv',
            'priority': 'u=1, i',
            'referer': 'https://www.twitch.tv/',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'x-device-id': f'{dev_id}' #ANY RANDOM ONE SHOULD'VE WORKED
        }

        payload_template ="""
        [
        {
            "operationName": "UseLive",
            "variables": {
            "channelLogin": "__CHANNEL_NAME__"
            },
            "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "639d5f11bfb8bf3053b424d9ef650d04c4ebb7d94711d644afb08fe9a0fad5d9"
            }
            }
        },
        
        {
            "operationName": "ChannelRoot_AboutPanel",
            "variables": {
            "channelLogin": "__CHANNEL_NAME__",
            "skipSchedule": true,
            "includeIsDJ": true
            },
            "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "0df42c4d26990ec1216d0b815c92cc4a4a806e25b352b66ac1dd91d5a1d59b80"
            }
            }
        },
        
        {
            "operationName": "ChannelPanels",
            "variables": {
            "id": "__CHANNEL_ID__"
            },
            "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "06d5b518ba3b016ebe62000151c9a81f162f2a1430eb1cf9ad0678ba56d0a768"
            }
            }
        }
        ]""".strip() 
        payload = payload_template.replace("__CHANNEL_NAME__", self.user_name).replace("__CHANNEL_ID__", self.channel_id)
        resp = requests.post(URL, headers=HEADERS, data=payload)
        print("Response status:", resp.status_code)
        emails = []
        socials = []
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"HTTP error: {e} (status {resp.status_code})")
            print(resp, flush=True)
            print(resp.status_code)
            return {}

        data = self.__try_parse_json(resp)

        better_data = json.loads(json.dumps(data, indent=2, ensure_ascii=False)) 

        try:
            for link in better_data[1]['data']['user']['channel']['socialMedias']:
                print(link['url'])
                socials.append(link['url'])
        except TypeError as e:
            print(f"TypeError First loop: {e} (status {resp.status_code})")
        
        except Exception as e:
            print(f"Error First loop : {e} (status {resp.status_code})")
            
        try:
            for panel in better_data[2]['data']['user']['panels']:
                url = []
                description = panel.get('description')
                if description:
                    url.extend(self.__extract_urls(description))
                    emails.extend(self.__extract_emails(description))
    
                link = panel.get('linkURL')
                if url:
                    print(url)
                    socials.extend(url)
                else:
                    print("No URL found for this panel.")
        except TypeError as e:
            print(f"TypeError Second loop: {e} (status {resp.status_code})")
            return{
                "links": [], 
                "emails": []
            }
        except Exception as e:
            print(f"Error Second loop: {e} (status {resp.status_code})")
            return{
            "links": [], 
            "emails": []
        }
        emails = self.__extract_emails(better_data[1]['data']['user'].get('description'))
        if len(socials) < 1:
            print(resp.text, flush=True)
            print(resp.status_code)
            return{
                "links": [], 
                "emails": []
            }
        return {"emails": emails, "links": list(set(socials))}

    def scrape_youtube(self):
        mails = []
        try:
            for link in self.youtube:
                response = requests.get(link)
                mails.extend(str(i).lower() for i in set(self.__extract_emails(response.text)))
            return mails
        except:
            return mails
    def scrape_twitter(self):
        mails = []
        for link in self.twitter:
            id = self.__get_twitter_id(url)
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
                mail = self.__extract_emails(text)
                mails.extend(mail)
            else:
                pass
        return mails

    def scrape_instagram(self):
        raise NotImplementedError
    def __extract_emails(self,text: str) -> list[str]:
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
    

    def __extract_urls(self, text):
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        return re.findall(url_pattern, text)
    def __generate_device_id(length=32, only_a_to_d=False):
        if only_a_to_d:
            chars = 'abcdABCD' + string.digits  # Only a-d (case sensitive) + digits
        else:
            chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        key = ''.join(random.choices(chars, k=length))
        print(key)
        return key
    def __try_parse_json(self, response):
        try:
            return response.json()
        except Exception:
            # Fallback to manual decoding attempts
            content = response.content

            # Try gzip
            try:
                return json.loads(gzip.decompress(content).decode('utf-8'))
            except Exception:
                pass

            # Try deflate
            try:
                return json.loads(zlib.decompress(content).decode('utf-8'))
            except Exception:
                try:
                    return json.loads(zlib.decompress(content, -zlib.MAX_WBITS).decode('utf-8'))
                except Exception:
                    pass

            # Try brotli
            try:
                return json.loads(brotli.decompress(content).decode('utf-8'))
            except Exception:
                pass

            # Try zstd
            try:
                dctx = zstd.ZstdDecompressor()
                decompressed = dctx.decompress(content)
                return json.loads(decompressed.decode('utf-8'))
            except Exception:
                pass

            # Final fallback: try utf-8 text decoding
            try:
                return json.loads(content.decode('utf-8', errors='replace'))
            except Exception as e:
                raise ValueError("All decoding methods failed") from e
    def __get_twitter_id(self, url: str):
        pattern = r"(?:https?://)?(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})"
        match = re.search(pattern, url)
        return match.group(1)
        
    
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
        self.stage = 0
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
