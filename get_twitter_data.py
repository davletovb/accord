# -*- coding: utf-8 -*-
"""Twitter.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sQ-TNsOoIyabl4bhst0A9SSv1YfleY0X
"""

# import lots of stuff
import sys
import os
import re
import tweepy
from tweepy import OAuthHandler

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

from google.colab import drive
drive.mount('/content/gdrive')

#@title Enter Twitter Credentials
TWITTER_KEY = 'rxZKr5xZ9S1b6bG4jIVXVkZqu' #@param {type:"string"}
TWITTER_SECRET_KEY = 'fX1wkeXC9x7y9TcrZyBZx9b6LbVjh0500geu81ysMKpNSDkW2k' #@param {type:"string"}

auth = tweepy.AppAuthHandler(TWITTER_KEY, TWITTER_SECRET_KEY)

api = tweepy.API(auth, wait_on_rate_limit=True,
				   wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

maxTweets = 1000 #@param {type:"slider", min:0, max:45000, step:100}
Filter_Retweets = True #@param {type:"boolean"}

tweet_list=[]
for tweet in tweepy.Cursor(api.user_timeline, id="jack", include_rts=False, tweet_mode="extended").items(maxTweets):
    #print(tweet.text)
    tweet_list.append([tweet.created_at.date(), 
                      tweet.id, tweet.user.screen_name, tweet.user.name, tweet.user.id, tweet.full_text, tweet.favorite_count, 
                      ])
    
#clear_output()
print("Downloaded {0} tweets".format(len(tweet_list)))

pd.set_option('display.max_colwidth', -1)

# load it into a pandas dataframe
tweet_df = pd.DataFrame(tweet_list, columns=['tweet_date', 'tweet_id', 'username', 'name', 'user_id', 'tweet', 'like_count'])
tweet_df.head()

#Create a column for hashtags
tweet_df['hashtag'] = tweet_df['tweet'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x))
tweet_df.head(20)

#!pip install tweet-preprocessor

import preprocessor as prep

prep.set_options(prep.OPT.URL, prep.OPT.EMOJI, prep.OPT.MENTION, prep.OPT.SMILEY, prep.OPT.RESERVED)

cleaned = [prep.clean(text) for text in tweet_df['tweet']]

print(cleaned)

#Remove punctuations
import string
punctuations = '''!()-=![]{};:+'"\,<>./?@#$%^&*_~'''

regex = re.compile('[%s]' % re.escape(punctuations))

preprocessed = [' '.join(regex.sub(u'', text).split()) for text in cleaned]

print(preprocessed)

#Remove numbers

final = [''.join(re.sub(r'\d', '', text)) for text in preprocessed]

print(final)

#Add cleaned text as new column

tweet_df['cleaned'] = final

tweet_df['cleaned'] = tweet_df['cleaned'].str.lower()

tweet_new = tweet_df[tweet_df['cleaned'].str.split().str.len()>1]

tweet_new.head(10)

tweet_new.to_csv('tweets.csv')
!cp tweets.csv "/content/gdrive/My Drive/"
