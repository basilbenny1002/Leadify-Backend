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

const payload = '[{"operationName":"UseLive","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"639d5f11bfb8bf3053b424d9ef650d04c4ebb7d94711d644afb08fe9a0fad5d9"}}},{"operationName":"SharedChatSession","variables":{"channelID":"82826005"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0ff9562b30cfa2b41ab1738485ced6f8f1e725a93abe732c396be5f4f1d13694"}}},{"operationName":"ChannelCollaborationEligibilityQuery","variables":{"options":{"channelIDs":["82826005"]}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"f32cb49f6bc54a4dc182b54c6e247d8344f8a16cc255acbc2e18fbd145df4cb2"}}},{"operationName":"GetHypeTrainExecutionV2","variables":{"userLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"897ef0c4e40e70e48037d4fcc48fea714ec02db153570f229d347f8dab957f9a"}}},{"operationName":"StoryPreviewChannel","variables":{"channelID":"82826005","capabilities":["FULL_FLATTENING","MENTION_STICKER","PORTRAIT_CLIP","VIDEO","RESHARE"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"2d5d66edb6b3ea7af518074fcbb9a4b04b17b5ee4dc87fe0e9001cbb31216709"}}},{"operationName":"GuestStarBatchCollaborationQuery","variables":{"options":{"channelIDs":["689206695"]},"canDropInFlagEnabled":false,"openCallingFlagEnabled":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"096d50357df5e938f4fa83fe2acf25cb0f4886149aa81ddb9754eae98c05f2dd"}}},{"operationName":"GuestStarBatchCollaborationQuery","variables":{"options":{"channelIDs":["191043512","167160215","597535246","136397315","75366734","469348555","40965449","654596520","213686587"]},"canDropInFlagEnabled":false,"openCallingFlagEnabled":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"096d50357df5e938f4fa83fe2acf25cb0f4886149aa81ddb9754eae98c05f2dd"}}},{"operationName":"GuestStarBatchCollaborationQuery","variables":{"options":{"channelIDs":["69239046","7877833","556462797","683529105","60994534"]},"canDropInFlagEnabled":false,"openCallingFlagEnabled":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"096d50357df5e938f4fa83fe2acf25cb0f4886149aa81ddb9754eae98c05f2dd"}}},{"operationName":"PersonalSectionsHypeTrains","variables":{"channelIDs":["469348555"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d4a42af6e461a470fb53073e19f52a03a66fca94af2fa88268ef095ca3b274ee"}}},{"operationName":"PersonalSectionsHypeTrains","variables":{"channelIDs":["7877833"]},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d4a42af6e461a470fb53073e19f52a03a66fca94af2fa88268ef095ca3b274ee"}}},{"operationName":"ChannelRoot_AboutPanel","variables":{"channelLogin":"phoenixsclive","skipSchedule":true,"includeIsDJ":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0df42c4d26990ec1216d0b815c92cc4a4a806e25b352b66ac1dd91d5a1d59b80"}}},{"operationName":"ActiveGoals","variables":{"channelLogin":"phoenixsclive"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"c855218eb019092b69369658150473e440e1c09cb8515396897b96cfe350e647"}}},{"operationName":"ExtensionsForChannel","variables":{"channelID":"82826005"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d52085e5b03d1fc3534aa49de8f5128b2ee0f4e700f79bf3875dcb1c90947ac3"}}},{"operationName":"ChannelPanels","variables":{"id":"82826005"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"06d5b518ba3b016ebe62000151c9a81f162f2a1430eb1cf9ad0678ba56d0a768"}}}]'
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
      await fs.writeFile('panels.json', dataString);
      console.log("Data written to response.json");
    } catch (error) {
      console.error('Error:', error);
    }
  }
  
  async function main(){
      await fetchData();
  }
  main();