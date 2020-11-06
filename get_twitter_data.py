import re
import sys

import pandas as pd
import tweepy

TWITTER_KEY = 'KEY'
TWITTER_SECRET_KEY = 'SECRET KEY'

def get_tweets(userid):
    max_tweets = 1000
    tweet_list = []

    auth = tweepy.AppAuthHandler(TWITTER_KEY, TWITTER_SECRET_KEY)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if not api:
        print("Can't Authenticate")
        sys.exit(-1)

    for tweet in tweepy.Cursor(api.user_timeline, id=userid, include_rts=False, tweet_mode="extended").items(
            max_tweets):
        tweet_list.append([
            tweet.id, tweet.created_at.date(), tweet.user.screen_name, tweet.user.name, tweet.user.id,
            tweet.favorite_count, tweet.retweet_count, tweet.full_text
        ])

    print("Downloaded {0} tweets".format(len(tweet_list)))

    # load it into a pandas dataframe
    tweet_df = pd.DataFrame(tweet_list, columns=['tweet_id', 'tweet_date', 'username', 'name', 'user_id', 'like_count',
                                                 'retweet_count', 'text'])

    # Create a column for hashtags
    tweet_df.insert(loc=7, column='hashtag',
                    value=tweet_df['text'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x)))
    return tweet_df
