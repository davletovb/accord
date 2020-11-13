import re
import sys

import pandas as pd
import tweepy

from multiprocessing.pool import ThreadPool

pool = ThreadPool(processes=2)

TWITTER_KEY = 'KEY'
TWITTER_SECRET_KEY = 'KEY'

auth = tweepy.AppAuthHandler(TWITTER_KEY, TWITTER_SECRET_KEY)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if not api:
    print("Can't Authenticate")
    sys.exit(-1)


def get_tweets(userid, max_tweets=1000):
    tweet_list = []

    for tweet in tweepy.Cursor(api.user_timeline, id=userid, include_rts=False, tweet_mode="extended").items(
            max_tweets):
        tweet_list.append([
            tweet.id, tweet.created_at.date(), tweet.favorite_count, tweet.retweet_count, tweet.full_text
        ])

    print("Downloaded {0} tweets".format(len(tweet_list)))

    # load it into a pandas dataframe
    tweet_df = pd.DataFrame(tweet_list, columns=['tweet_id', 'tweet_date', 'like_count', 'retweet_count', 'text'])

    # Create a column for hashtags
    tweet_df.insert(loc=4, column='hashtag',
                    value=tweet_df['text'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x)))
    tweet_df.to_json('data/' + userid + '.json')

    return tweet_df


def get_user(userid):
    #user = api.get_user(userid)

    async_result = pool.apply_async(api.get_user, (userid,))
    async_result2 = pool.apply_async(get_tweets, (userid,))


    return async_result.get()
