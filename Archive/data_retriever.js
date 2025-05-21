const fs = require('fs').promises;

const url = 'https://gql.twitch.tv/gql';

const headers = {
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
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
  'x-device-id': 'ZdzP9vQkHAZhyUFgLhxa2uuA2l4RBme7'
};

const payload = '[{"operationName":"HomeOfflineCarousel","variables":{"channelLogin":"phoenixsclive","includeTrailerUpsell":false,"trailerUpsellVideoID":"601752619"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"84e25789b04ac4dcaefd673cfb4259d39d03c6422838d09a4ed2aaf9b67054d8"}}},{"operationName":"StoryChannelQuery","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"efa575524a7a86bf6172801278301584a366e59a8049c667fd4abea01522b8a2"}}},{"operationName":"StreamEventCelebrationsChannelPageBadge","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"93d2d5760c148819e718d301141e62c91ddf0ef09b3f8b8102afbab6ba833174"}}},{"operationName":"ChannelAvatar","variables":{"channelLogin":"phoenixsclive","includeIsDJ":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"12575ab92ea9444d8bade6de529b288a05073617f319c87078b3a89e74cd783a"}}},{"operationName":"ChannelSupportButtons","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"834a75e1c06cffada00f0900664a5033e392f6fb655fae8d2e25b21b340545a9"}}},{"operationName":"LowerHomeHeader","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"08af264bf5d5231cadb05acaddce0992622f86a0d3d7f6f59955316564d3c008"}}},{"operationName":"HomeTrackQuery","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"129cbf14117ce8e95f01bd2043154089058146664df866d0314e84355ffb4e05"}}},{"operationName":"ChatScreenReaderAutoAnnounce","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"3ddf79c5dd411106eae1d44801f1a123ecf82cad7e973575b18367b2c5d63a0c"}}},{"operationName":"GlobalBadges","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"9db27e18d61ee393ccfdec8c7d90f14f9a11266298c2e5eb808550b77d7bcdf6"}}},{"operationName":"ChatRestrictions","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"7514aeb3d2c203087b83e920f8d36eb18a5ca1bfa96a554ed431255ecbbbc089"}}},{"operationName":"BlockedUsers","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"8044e3fd61f8158a39e07b38f5d1a279d1fdb748faa9889fde046feae640f76b"}}},{"operationName":"MessageBufferChatHistory","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"33dba0e0c249135052e930cbd6c4a66daa32249ba00d1c8def75857fa3f3431d"}}},{"operationName":"MessageBuffer_Channel","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"bfc959904f55b5003ae4674d4bea83ebdcd8867ad76e12f38957d433902d2fcc"}}},{"operationName":"PollChannelSettings","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"e31355d5fd19bf9b3c0907c8302ce9ff5466d06230bec209f78cf04724b7380c"}}},{"operationName":"CommunityPointsRewardRedemptionContext","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"f585e0d07bee16fa1355238b1762c095cc10470edc263d38c4e3a1b8a7e53f65"}}},{"operationName":"ChannelPointsPredictionContext","variables":{"count":1,"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"beb846598256b75bd7c1fe54a80431335996153e358ca9c7837ce7bb83d7d383"}}},{"operationName":"ChannelPointsContext","variables":{"channelLogin":"phoenixsclive","includeGoalTypes":["CREATOR","BOOST"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"374314de591e69925fce3ddc2bcf085796f56ebb8cad67a0daa3165c03adc345"}}},{"operationName":"ChannelPointsGlobalContext","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d3fa3a96e78a3e62bdd3ef3c4effafeda52442906cec41a9440e609a388679e2"}}},{"operationName":"SyncedSettingsChatPauseSetting","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"922f2a23e49da4ce2660f7fbfeefeefab19f7651196f9b54f03555590f173627"}}},{"operationName":"SyncedSettingsDeletedMessageDisplaySetting","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"79fbdf86e8ee5fa4ca27cad96c292702eed8a8cc14faedc874a577f6e8fe4004"}}},{"operationName":"SyncedSettingsCelebrations","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"8c5da4184cd8d48a962f93f4767abb648c0a3e64637b95d728e635e6f20a28fd"}}},{"operationName":"SyncedSettingsEmoteAnimations","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"64ac5d385b316fd889f8c46942a7c7463a1429452ef20ffc5d0cd23fcc4ecf30"}}},{"operationName":"SyncedSettingsReadableChatColors","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"cd9c43ab3cb4c04515a879bbd618055aab18c6ac4081ed9de333945ca91247ba"}}},{"operationName":"ChatFilterContextManager_User","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"98821224809f26e3f3a627a0e30134b00c4db33b602b4249cec518a8c21fe902"}}},{"operationName":"ChatRoomState","variables":{"login":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"9e0f79669e31950c658459564bc4cff236ac9c03e534cc32769ac58bc0cdd708"}}},{"operationName":"Chat_UserData","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"39985d1ff9324442a3a5df1be212e1bc4f358a31100e5025c4e61a07d7e70743"}}},{"operationName":"Chat_ChannelData","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"3c445f9a8315fa164f2d3fb12c2f932754c2f2c129f952605b9ec6cf026dd362"}}},{"operationName":"CommonHooks_BlockedUsers","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"7c87171d7497df41f9938d2bc18a26f7a97f32f11b7f28c4826950c4ebe000b2"}}},{"operationName":"PinnedCheersSettings","variables":{"login":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"ca73cb0396fe5bcbe05c906fd472622e4b873eeb07699c2664026a079aeec631"}}}]'
async function fetchData() {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: payload
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log("Response status: ", response.status);
      const data = await response.json();
      const dataString = JSON.stringify(data, null, 2); // Pretty-print with 2 spaces
      await fs.writeFile('response.json', dataString);
      console.log("Data written to response.json");
    } catch (error) {
      console.error('Error:', error);
    }
  }
  
  async function main(){
      await fetchData();
  }
  main();