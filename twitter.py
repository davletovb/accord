import json
import sys
import os
import pandas as pd
import tweepy

TWITTER_KEY = os.environ.get('TWITTER_KEY')
TWITTER_SECRET_KEY = os.environ.get('TWITTER_SECRET_KEY')


class TwitterAPI:
    def __init__(self):

        self.auth = tweepy.AppAuthHandler(TWITTER_KEY, TWITTER_SECRET_KEY)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        if not self.api:
            print("Can't Authenticate")
            sys.exit(-1)

    def get_user_profile(self, userid):

        if not os.path.exists('users'):
            os.makedirs('users')

        if not os.path.exists('users/' + userid + '.json'):
            user_json = {}
            user = self.api.get_user(screen_name=userid)
            # user_json = user._json
            user_json['userid'] = user.id
            user_json['username'] = user.screen_name
            user_json['name'] = user.name
            user_json['location'] = user.location
            user_json['bio'] = user.description
            #user_json['pronoun'] = preprocess.get_pron(user.description)
            user_json['profile_picture'] = user.profile_image_url_https.replace(
                '_normal', '')
            user_json['verified'] = user.verified
            user_json['protected'] = user.protected
            user_json['followers_count'] = user.followers_count
            user_json['following_count'] = user.friends_count
            user_json['tweets_count'] = user.statuses_count
            user_json['url'] = user.url  # user.entities['url']
            user_json['twitter_created_at'] = user.created_at
            with open('users/' + userid + '.json', 'w') as json_file:
                json.dump(user_json, json_file, indent=4,
                          ensure_ascii=False, default=str)
            print("User profile saved")
            return user_json
        else:
            with open('users/' + userid + '.json', 'r') as file:
                user_json = json.load(file)
            print("User profile exists")
            return user_json

    def get_user_tweets(self, userid, max_tweets=1000):

        if not os.path.exists('twitter_data'):
            os.makedirs('twitter_data')

        tweet_list = []

        for tweet in tweepy.Cursor(self.api.user_timeline, screen_name=userid, include_rts=False, tweet_mode="extended").items(
                max_tweets):
            tweet_list.append([
                tweet.id, tweet.created_at, tweet.favorite_count, tweet.retweet_count, tweet.full_text
            ])

        print("Downloaded {0} tweets".format(len(tweet_list)))

        # load it into a pandas dataframe
        tweet_df = pd.DataFrame(tweet_list, columns=[
            'tweet_id', 'tweet_date', 'like_count', 'retweet_count', 'text'])

        return tweet_df

    def get_user_followers(self, userid):

        if not os.path.exists('twitter_data/followers/' + userid + '.json'):
            follower_list = []
            for follower in tweepy.Cursor(self.api.followers, screen_name=userid).items():
                follower_list.append(follower.screen_name)

            print("Downloaded {0} tweets".format(len(follower_list)))

            with open('twitter_data/followers/' + userid + '.json', 'w') as json_file:
                json.dump(follower_list, json_file)

            print("User's followers saved")
        else:
            print("User's followers already exist")

    def get_top_tweets(self, userid):

        if os.path.exists('twitter_data/' + userid + '.json'):
            tweet_df = pd.read_json('twitter_data/' + userid + '.json')
            df = tweet_df.nlargest(5, 'like_count')[
                ['tweet_id', 'tweet_date', 'like_count', 'retweet_count', 'text']]
            print("Getting top tweets for user: " + userid)

            return df.to_dict(orient='records')
        else:
            print("User data does not exist")
            return None
