import json
import re
import sys
from os import path

import pandas as pd
import preprocessor as prep
import tweepy

import ann_index
import get_tokens
import get_vector

TWITTER_KEY = 'rxZKr5xZ9S1b6bG4jIVXVkZqu'
TWITTER_SECRET_KEY = 'fX1wkeXC9x7y9TcrZyBZx9b6LbVjh0500geu81ysMKpNSDkW2k'

auth = tweepy.AppAuthHandler(TWITTER_KEY, TWITTER_SECRET_KEY)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if not api:
    print("Can't Authenticate")
    sys.exit(-1)


def get_user(userid):
    if not path.exists('users/' + userid + '.json'):
        user = api.get_user(userid)
        user_json = user._json
        with open('users/' + userid + '.json', 'w') as json_file:
            json.dump(user_json, json_file, ensure_ascii=False)
        print("User profile saved")
        return user_json
    else:
        with open('users/' + userid + '.json', 'r') as file:
            user_json = json.load(file)
        print("User profile exists")
        return user_json


def pre_process(userid):
    if not path.exists('data/' + userid + '.json'):
        tweet_df = get_tweets(userid)
        cleaned_tweet_df = get_cleaned_tweets(userid, tweet_df)
        # tweets = cleaned_tweet_df['cleaned'].tolist()
        # get_vector.get_bert(userid, tweets)
        words = cleaned_tweet_df['tokens'].tolist()
        get_vector.mean_tfidf(userid, words)
        ann_index.build_index('word')
    else:
        print("User data already exist")
        cleaned_tweet_df = pd.read_json('data/' + userid + '.json')
        words = cleaned_tweet_df['tokens'].tolist()
        get_vector.mean_tfidf(userid, words)
        ann_index.build_index('word')


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

    return tweet_df


def get_cleaned_tweets(userid, tweet_df):
    punctuations = '''!()-=—!→–[]|{};:+`"“”\,<>/@#$%^&*_~'''

    prep.set_options(prep.OPT.URL, prep.OPT.MENTION)

    cleaned = [prep.clean(text) for text in tweet_df['text']]

    tweet_df['cleaned'] = cleaned
    tweet_df['cleaned'] = tweet_df.cleaned.apply(
        lambda x: x.translate(str.maketrans(punctuations, ' ' * len(punctuations))))
    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: remove_emojis(x))
    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: x.replace('...', ' '))
    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: ' '.join(x.split()))

    print("Tweets cleaned")
    tokens = [get_tokens.get_tokens(tweet) for tweet in tweet_df['cleaned']]
    tweet_df['tokens'] = tokens

    tweet_df.to_json('data/' + userid + '.json')
    print('Cleaned tweets saved')

    return tweet_df


def remove_emojis(data):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)
