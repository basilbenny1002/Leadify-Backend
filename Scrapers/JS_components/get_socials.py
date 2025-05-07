# import asyncio
# import aiohttp
# import aiofiles
# import json

# url = 'https://gql.twitch.tv/gql'

# headers = {
#     'accept': '*/*',
#     'accept-encoding': 'gzip, deflate, br, zstd',
#     'accept-language': 'en-US',
#     'authorization': 'OAuth z61c9og3og2cfy2npqdwnl7f4k0tud',
#     'client-id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
#     'client-session-id': '2d3cc8131e0b6a25',
#     'client-version': 'de99b9bb-52a9-4694-9653-6d935ab0cbcc',
#     'content-type': 'text/plain;charset=UTF-8',
#     'origin': 'https://www.twitch.tv',
#     'priority': 'u=1, i',
#     'referer': 'https://www.twitch.tv/',
#     'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
#     'x-device-id': 'ZdzP9vQkHAZhyUFgLhxa2uuA2l4RBme7'
# }

# payload = '[{"operationName":"HomeOfflineCarousel","variables":{"channelLogin":"phoenixsclive","includeTrailerUpsell":false,"trailerUpsellVideoID":"601752619"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"84e25789b04ac4dcaefd673cfb4259d39d03c6422838d09a4ed2aaf9b67054d8"}}},{"operationName":"StoryChannelQuery","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"efa575524a7a86bf6172801278301584a366e59a8049c667fd4abea01522b8a2"}}},{"operationName":"StreamEventCelebrationsChannelPageBadge","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"93d2d5760c148819e718d301141e62c91ddf0ef09b3f8b8102afbab6ba833174"}}},{"operationName":"ChannelAvatar","variables":{"channelLogin":"phoenixsclive","includeIsDJ":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"12575ab92ea9444d8bade6de529b288a05073617f319c87078b3a89e74cd783a"}}},{"operationName":"ChannelSupportButtons","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"834a75e1c06cffada00f0900664a5033e392f6fb655fae8d2e25b21b340545a9"}}},{"operationName":"LowerHomeHeader","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"08af264bf5d5231cadb05acaddce0992622f86a0d3d7f6f59955316564d3c008"}}},{"operationName":"HomeTrackQuery","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"129cbf14117ce8e95f01bd2043154089058146664df866d0314e84355ffb4e05"}}},{"operationName":"ChatScreenReaderAutoAnnounce","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"3ddf79c5dd411106eae1d44801f1a123ecf82cad7e973575b18367b2c5d63a0c"}}},{"operationName":"GlobalBadges","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"9db27e18d61ee393ccfdec8c7d90f14f9a11266298c2e5eb808550b77d7bcdf6"}}},{"operationName":"ChatRestrictions","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"7514aeb3d2c203087b83e920f8d36eb18a5ca1bfa96a554ed431255ecbbbc089"}}},{"operationName":"BlockedUsers","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"8044e3fd61f8158a39e07b38f5d1a279d1fdb748faa9889fde046feae640f76b"}}},{"operationName":"MessageBufferChatHistory","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"33dba0e0c249135052e930cbd6c4a66daa32249ba00d1c8def75857fa3f3431d"}}},{"operationName":"MessageBuffer_Channel","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"bfc959904f55b5003ae4674d4bea83ebdcd8867ad76e12f38957d433902d2fcc"}}},{"operationName":"PollChannelSettings","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"e31355d5fd19bf9b3c0907c8302ce9ff5466d06230bec209f78cf04724b7380c"}}},{"operationName":"CommunityPointsRewardRedemptionContext","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"f585e0d07bee16fa1355238b1762c095cc10470edc263d38c4e3a1b8a7e53f65"}}},{"operationName":"ChannelPointsPredictionContext","variables":{"count":1,"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"beb846598256b75bd7c1fe54a80431335996153e358ca9c7837ce7bb83d7d383"}}},{"operationName":"ChannelPointsContext","variables":{"channelLogin":"phoenixsclive","includeGoalTypes":["CREATOR","BOOST"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"374314de591e69925fce3ddc2bcf085796f56ebb8cad67a0daa3165c03adc345"}}},{"operationName":"ChannelPointsGlobalContext","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d3fa3a96e78a3e62bdd3ef3c4effafeda52442906cec41a9440e609a388679e2"}}},{"operationName":"SyncedSettingsChatPauseSetting","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"922f2a23e49da4ce2660f7fbfeefeefab19f7651196f9b54f03555590f173627"}}},{"operationName":"SyncedSettingsDeletedMessageDisplaySetting","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"79fbdf86e8ee5fa4ca27cad96c292702eed8a8cc14faedc874a577f6e8fe4004"}}},{"operationName":"SyncedSettingsCelebrations","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"8c5da4184cd8d48a962f93f4767abb648c0a3e64637b95d728e635e6f20a28fd"}}},{"operationName":"SyncedSettingsEmoteAnimations","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"64ac5d385b316fd889f8c46942a7c7463a1429452ef20ffc5d0cd23fcc4ecf30"}}},{"operationName":"SyncedSettingsReadableChatColors","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"cd9c43ab3cb4c04515a879bbd618055aab18c6ac4081ed9de333945ca91247ba"}}},{"operationName":"ChatFilterContextManager_User","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"98821224809f26e3f3a627a0e30134b00c4db33b602b4249cec518a8c21fe902"}}},{"operationName":"ChatRoomState","variables":{"login":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"9e0f79669e31950c658459564bc4cff236ac9c03e534cc32769ac58bc0cdd708"}}},{"operationName":"Chat_UserData","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"39985d1ff9324442a3a5df1be212e1bc4f358a31100e5025c4e61a07d7e70743"}}},{"operationName":"Chat_ChannelData","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"3c445f9a8315fa164f2d3fb12c2f932754c2f2c129f952605b9ec6cf026dd362"}}},{"operationName":"CommonHooks_BlockedUsers","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"7c87171d7497df41f9938d2bc18a26f7a97f32f11b7f28c4826950c4ebe000b2"}}},{"operationName":"PinnedCheersSettings","variables":{"login":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"ca73cb0396fe5bcbe05c906fd472622e4b873eeb07699c2664026a079aeec631"}}}]'

# async def fetch_data():
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, headers=headers, data=payload) as response:
#                 print(f"Response status: {response.status}")
#                 if response.status < 200 or response.status >= 300:
#                     raise Exception(f'HTTP error! status: {response.status}')
#                 data = await response.json()
#                 json_string = json.dumps(data, indent=2)
#                 print(data[0])
#                 print(data[0]['data'])
#                 print("\n\n\n")
#                 print(data[0]['data']['user']['channel']['socialMedias'])
                
                
#                 async with aiofiles.open(r'Leadify-Backend\Scrapers\JS_components\\response.json', 'w') as f:
#                     await f.write(json_string)
#                 print("Data written to response.json")
#     except Exception as e:
#         print(f'Error: {e}')

# async def main():
#     await fetch_data()

# if __name__ == '__main__':
#     asyncio.run(main())



import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')


URL = 'https://gql.twitch.tv/gql'

HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US',
    'authorization': 'OAuth z61c9og3og2cfy2npqdwnl7f4k0tud',
    'client-id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
    'client-session-id': '2d3cc8131e0b6a25',
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
    'x-device-id': 'ZdzP9vQkHAZhyUFgLhxa2uuA2l4RBme7'
}

payload = '[{"operationName":"UseLive","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"639d5f11bfb8bf3053b424d9ef650d04c4ebb7d94711d644afb08fe9a0fad5d9"}}},{"operationName":"SharedChatSession","variables":{"channelID":"82826005"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0ff9562b30cfa2b41ab1738485ced6f8f1e725a93abe732c396be5f4f1d13694"}}},{"operationName":"ChannelCollaborationEligibilityQuery","variables":{"options":{"channelIDs":["82826005"]}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"f32cb49f6bc54a4dc182b54c6e247d8344f8a16cc255acbc2e18fbd145df4cb2"}}},{"operationName":"GetHypeTrainExecutionV2","variables":{"userLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"897ef0c4e40e70e48037d4fcc48fea714ec02db153570f229d347f8dab957f9a"}}},{"operationName":"StoryPreviewChannel","variables":{"channelID":"82826005","capabilities":["FULL_FLATTENING","MENTION_STICKER","PORTRAIT_CLIP","VIDEO","RESHARE"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"2d5d66edb6b3ea7af518074fcbb9a4b04b17b5ee4dc87fe0e9001cbb31216709"}}},{"operationName":"GuestStarBatchCollaborationQuery","variables":{"options":{"channelIDs":["689206695"]},"canDropInFlagEnabled":false,"openCallingFlagEnabled":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"096d50357df5e938f4fa83fe2acf25cb0f4886149aa81ddb9754eae98c05f2dd"}}},{"operationName":"GuestStarBatchCollaborationQuery","variables":{"options":{"channelIDs":["191043512","167160215","597535246","136397315","75366734","469348555","40965449","654596520","213686587"]},"canDropInFlagEnabled":false,"openCallingFlagEnabled":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"096d50357df5e938f4fa83fe2acf25cb0f4886149aa81ddb9754eae98c05f2dd"}}},{"operationName":"GuestStarBatchCollaborationQuery","variables":{"options":{"channelIDs":["69239046","7877833","556462797","683529105","60994534"]},"canDropInFlagEnabled":false,"openCallingFlagEnabled":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"096d50357df5e938f4fa83fe2acf25cb0f4886149aa81ddb9754eae98c05f2dd"}}},{"operationName":"PersonalSectionsHypeTrains","variables":{"channelIDs":["469348555"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d4a42af6e461a470fb53073e19f52a03a66fca94af2fa88268ef095ca3b274ee"}}},{"operationName":"PersonalSectionsHypeTrains","variables":{"channelIDs":["7877833"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d4a42af6e461a470fb53073e19f52a03a66fca94af2fa88268ef095ca3b274ee"}}},{"operationName":"ChannelRoot_AboutPanel","variables":{"channelLogin":"phoenixsclive","skipSchedule":true,"includeIsDJ":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0df42c4d26990ec1216d0b815c92cc4a4a806e25b352b66ac1dd91d5a1d59b80"}}},{"operationName":"ActiveGoals","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"c855218eb019092b69369658150473e440e1c09cb8515396897b96cfe350e647"}}},{"operationName":"ExtensionsForChannel","variables":{"channelID":"82826005"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d52085e5b03d1fc3534aa49de8f5128b2ee0f4e700f79bf3875dcb1c90947ac3"}}},{"operationName":"ChannelPanels","variables":{"id":"82826005"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"06d5b518ba3b016ebe62000151c9a81f162f2a1430eb1cf9ad0678ba56d0a768"}}}]'.strip()
def fetch_and_save():
    resp = requests.post(URL, headers=HEADERS, data=payload)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTP error: {e} (status {resp.status_code})")
        return

    print("Response status:", resp.status_code)
    data = resp.json()
    better_data = json.loads(json.dumps(data, indent=2, ensure_ascii=False))
    # print(better_data[10]['data']['user']['channel']['socialMedias']) #Socials links
    for link in better_data[10]['data']['user']['channel']['socialMedias']:
        print(link['url']) #Socials links
    for panel in better_data[13]['data']['user']['panels']:
        # print(panel['linkURL'])
        url = panel.get('linkURL')
        if url:
            print(url)
        else:
            print("No URL found for this panel.")
    
    # with open('phoenix_python.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, indent=2, ensure_ascii=False)
    # print("Data written to grim.json")

if __name__ == '__main__':
    fetch_and_save()
