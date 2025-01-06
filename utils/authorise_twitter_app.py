import os

import tweepy
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get your API keys from environment variables
consumer_key = os.getenv("TW_API_KEY")
consumer_secret = os.getenv("TW_API_KEY_SECRET")

# Step 1: Obtain a request token
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)

# Step 2: Redirect user to Twitter to authorize
try:
    redirect_url = auth.get_authorization_url()
    print(f"Please go to this URL and authorize the app: {redirect_url}")
except tweepy.TweepyException as e:
    print("Error! Failed to get request token.", e)

# Step 3: After authorization, get the verifier code from the callback URL
verifier = input("Enter the verifier code from the callback URL: ")

# Step 4: Get the access token
try:
    auth.get_access_token(verifier)
    print("Access token:", auth.access_token)
    print("Access token secret:", auth.access_token_secret)
except tweepy.TweepyException as e:
    print("Error! Failed to get access token.", e)

# Now you can use the access token and secret to authenticate API requests
api = tweepy.API(auth)

# Verify credentials
try:
    api.verify_credentials()
    print("Authentication OK")
except Exception as e:
    print("Error during authentication", e)

# # Example: Post a tweet
# try:
#     api.update_status("Hello, world! This is a tweet from my app.")
#     print("Tweet posted successfully!")
# except tweepy.TweepyException as e:
#     print("An error occurred:", e)
