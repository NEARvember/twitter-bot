#!/usr/bin/env python3

import tweepy
import logging
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_bot.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

mention_regex = re.compile(r'$(@\w+ ?)+')

class TwitterEchoBot:
    def __init__(self, last_mention_id=None):
        # Initialize Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_KEY_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )
        self.openai = OpenAI()

        # Get authenticated user's ID
        self.me = self.client.get_me()[0]
        logging.info(f"Bot initialized for user: {self.me.username}")

        self.last_mention_id = last_mention_id

    def get_mentions(self, since_id=None):
        """Fetch mentions since the last checked tweet"""
        try:
            mentions = self.client.get_users_mentions(
                self.me.id,
                since_id=since_id,
                tweet_fields=['created_at']
            )
            return mentions.data if mentions.data else []
        except Exception as e:
            logging.error(f"Error fetching mentions: {str(e)}")
            return []

    def on_mention(self, tweet):
        """Reply to a tweet with its own content"""
        try:
            logging.info(f"Checking conditions for tweet {tweet.id}: {tweet.text}")

            # Replace all mentions on the beginning of the tweet with empty string
            tweet.text = mention_regex.sub('', tweet.text)

            completion = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Twitter AI agent that does nothing useful and just replies to tweets acting like it knows everything, shills and bullposts AI, user-owned Internet, and other technical nonsense, in a way that people think that it's a bot. Your name is NEARvember AI. Your responses are short and you never use hashtags or other lame things in your responses. Your twitter handle is @NEARvemberAI, and other handles are responses to other people, not you."},
                    {
                        "role": "user",
                        "content": f"Reply to this tweet: {tweet.text}"
                    }
                ]
            )

            response = self.client.create_tweet(
                text=completion.choices[0].message.content,
                in_reply_to_tweet_id=tweet.id
            )
            print(f"Response to tweet {tweet.text}: {response.data["text"]}")
            return response
        except Exception as e:
            logging.error(f"Error replying to tweet {tweet.id}: {str(e)}")
            return None

    def run(self, check_interval=91):
        """Main bot loop"""
        logging.info("Starting bot loop...")
        last_mention_id = self.last_mention_id

        while True:
            try:
                mentions = self.get_mentions(since_id=last_mention_id)

                for mention in mentions:
                    self.on_mention(mention)
                    last_mention_id = mention.id
                    # Save the last mention ID for the next check
                    with open('last_mention_id.txt', 'w') as f:
                        f.write(str(last_mention_id))

                logging.info("Waiting for new mentions...")
                time.sleep(check_interval)

            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                time.sleep(check_interval)

if __name__ == "__main__":
    bot = TwitterEchoBot(
        last_mention_id=int(open('last_mention_id.txt').read()) if os.path.exists('last_mention_id.txt') else None
    )
    bot.run()
