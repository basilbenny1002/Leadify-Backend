

import requests
import json
import sys
import random
import string
sys.stdout.reconfigure(encoding='utf-8')

def generate_device_id(length=32, only_a_to_d=False):
    if only_a_to_d:
        chars = 'abcdABCD' + string.digits  # Only a-d (case sensitive) + digits
    else:
        chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    key = ''.join(random.choices(chars, k=length))
    print(key)
    return key


def fetch_and_save(channel_name, channel_id):
  URL = 'https://gql.twitch.tv/gql'

  HEADERS = {
      'accept': '*/*',
      'accept-encoding': 'gzip, deflate, br, zstd',
      'accept-language': 'en-US',
      # 'authorization': 'OAuth z61c9og3og2cfy2npqdwnl7f4k0tud', #NOT NECESSARY
      'client-id': 'kimne78kx3ncx6brgo4mv6wki5h1ko', #HARDCODED CLIENT ID
      'client-session-id': f'{generate_device_id(16, only_a_to_d=True).lower()}', #ANY RANDOM ONE SHOUDL WORK
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
      'x-device-id': f'{generate_device_id(32)}' #ANY RANDOM ONE SHOULD'VE WORKED
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
  payload = payload_template.replace("__CHANNEL_NAME__", channel_name).replace("__CHANNEL_ID__", channel_id)
  print("Payload: ", payload)
  print("Headers: ", HEADERS)
    
  resp = requests.post(URL, headers=HEADERS, data=payload)
  print("Response status:", resp.status_code)
  emails = []
  socials = []
  try:
    resp.raise_for_status()
  except requests.HTTPError as e:
    print(f"HTTP error: {e} (status {resp.status_code})")
    return

  print("Response status:", resp.status_code)
  data = resp.json()
  better_data = json.loads(json.dumps(data, indent=2, ensure_ascii=False))
  for link in better_data[1]['data']['user']['channel']['socialMedias']:
    print(link['url'])
    # print(better_data[10]['data']['user']['channel']['socialMedias']) #Socials links
    # for link in better_data[10]['data']['user']['channel']['socialMedias']:
    #     print(link['url']) #Socials links
  for panel in better_data[2]['data']['user']['panels']:
        # print(panel['linkURL'])
    url = panel.get('linkURL')
    if url:
      print(url)
    else:
      print("No URL found for this panel.")
  print("Description: ", better_data[1]['data']['user']['description'])
    
  # with open('phoenix_python.json', 'w', encoding='utf-8') as f:
  #   json.dump(data, f, indent=2, ensure_ascii=False)
  # print("Data written to grim.json")

if __name__ == '__main__':
    fetch_and_save("phoenixsclive", "82826005")
