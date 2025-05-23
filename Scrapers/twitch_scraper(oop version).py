from abc import ABCMeta, abstractmethod

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