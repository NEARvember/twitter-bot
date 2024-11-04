import tweepy
import os
from dotenv import load_dotenv
from flask import Flask, request
import webbrowser

load_dotenv()

app = Flask(__name__)

# Your developer account API keys
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_KEY_SECRET')

# OAuth 1.0a Handler
oauth1_user_handler = tweepy.OAuth1UserHandler(
    API_KEY,
    API_SECRET,
    callback="http://127.0.0.1:8000/callback"
)

@app.route('/')
def start_auth():
    auth_url = oauth1_user_handler.get_authorization_url()
    webbrowser.open(auth_url)
    return "Authentication started. Check your browser."

@app.route('/callback')
def callback():
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    # Get access tokens
    access_token, access_token_secret = oauth1_user_handler.get_access_token(
        oauth_verifier
    )

    # Print the tokens
    print("\n=== Save these tokens in your .env file ===")
    print(f"ACCESS_TOKEN={access_token}")
    print(f"ACCESS_TOKEN_SECRET={access_token_secret}")

    return "Authentication successful! Check your terminal for the access tokens."

if __name__ == "__main__":
    print("Starting authentication process...")
    print("1. A browser window will open")
    print("2. Log in with your BOT account (not your developer account)")
    print("3. Authorize the application")
    print("4. Copy the new access tokens to your .env file")

    # Start the Flask server
    app.run(port=8000)
