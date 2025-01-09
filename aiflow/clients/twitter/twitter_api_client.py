from twitter.account import Account

from sia.clients.client import SiaClient


class SiaTwitter(SiaClient):

    def __init__(self, login_cookies):
        super().__init__(client=Account(cookies=login_cookies))

    def publish_post(self, post):
        try:
            self.client.tweet(post)
            print("Tweet sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send tweet: {e}")
