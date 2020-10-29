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

from os import path

import re
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances

import gensim.downloader as api
from gensim.models.word2vec import Word2Vec

!pip install sentence_transformers
!pip install tweet-preprocessor
!pip install unidecode
!python -m nltk.downloader all

from sentence_transformers import SentenceTransformer, util
import preprocessor as prep

import string
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from unidecode import unidecode
from nltk.stem import WordNetLemmatizer
#from nltk.tokenize import word_tokenize
from nltk.tokenize import TweetTokenizer

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

docs = []

max_tweets = 1000

tweet_list=[]
for tweet in tweepy.Cursor(api.user_timeline, id="nntaleb", include_rts=False, tweet_mode="extended").items(max_tweets):

    tweet_list.append([tweet.created_at.date(), 
                      tweet.id, tweet.user.screen_name, tweet.user.name, tweet.user.id, tweet.full_text, tweet.favorite_count, 
                      ])

print("Downloaded {0} tweets".format(len(tweet_list)))

pd.set_option('display.max_colwidth', -1)

# load it into a pandas dataframe
tweet_df = pd.DataFrame(tweet_list, columns=['tweet_date', 'tweet_id', 'username', 'name', 'user_id', 'tweet', 'like_count'])
tweet_df.head()

#Create a column for hashtags
tweet_df['hashtag'] = tweet_df['tweet'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x))
tweet_df.head(10)

stopset = stopwords.words('english')

prep.set_options(prep.OPT.URL, prep.OPT.MENTION)

cleaned = [prep.clean(text) for text in tweet_df['tweet']]

print(cleaned)

tweet_df['cleaned'] = cleaned

tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: " ".join(re.sub(r'[^a-zA-Z]',' ',w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]',' ',w).lower() not in stopset))

tweet_df.head(10)

doc = ""

for item in cleaned:
  doc = doc + " " + item 

docs.append([tweet_list[0][2], tweet_list[0][4], doc])

print(docs)

doc = pd.DataFrame(docs, columns=["username", "userid","tweets"])

doc.head(5)

tokenizer = TweetTokenizer()
lemmatizer = WordNetLemmatizer()
punctuations = '''!()-=![]{};:+`'"\,<>./?@#$%^&*_~'''
stopset = stopwords.words('english')

abbrevs = {
    'dm': 'direct message',
    'ai':'artificial intelligence',
    'ar':'augmented reality',
    'vr':'virtual reality',
    'ml':'machine learning',
    'btc':'bitcoin',
    'eth':'ethereum'
}

def lemmatize(token):
    lemmatized_token1=lemmatizer.lemmatize(token, pos="v")
    lemmatized_token2=lemmatizer.lemmatize(lemmatized_token1, pos="n")
    lemmatized_token3=lemmatizer.lemmatize(lemmatized_token2, pos="a")
    lemmatized_token=lemmatizer.lemmatize(lemmatized_token3, pos="r")
    return lemmatized_token

def pre_process(corpus):
    corpus = corpus.lower()
    corpus = corpus.translate(str.maketrans(punctuations, ' '*len(punctuations)))
    tokens = tokenizer.tokenize(corpus)
    cleaned_corpus=[]
    for token in tokens:
      token = ''.join([i for i in token if not i.isdigit()])
      if ((token not in stopset) and (len(token)>2)):
        token = lemmatize(token)
        token = token.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
        token = unidecode(token)
        cleaned_corpus.append(token)
      else:
        continue
    return cleaned_corpus

pre_processed = [pre_process(tweet) for tweet in cleaned]

print(pre_processed)

#Add cleaned text as new column
punctuations = '''0123456789!()-=![]{};:+`'“”"\,<>./?@#$%^&*_~'''
cleaned = [text.lower().translate(str.maketrans(punctuations, ' '*len(punctuations))) for text in cleaned]

tweet_df['cleaned'] = cleaned
tweet_df['tokens'] = pre_processed

tweet_new = tweet_df[tweet_df['cleaned'].str.split().str.len()>1]

tweet_new.head(10)

tweet_new.to_csv('tweets.csv')
!cp tweets.csv "/content/gdrive/My Drive/"

info = api.info()

model = api.load("glove-twitter-200")

cat=model.word_vec("cat")
avg=numpy.zeros(len(cat))

tokens = [item for sublist in pre_processed for item in sublist]
doc = [" ".join(item) for item in pre_processed]
print(doc)

count = 1
for word in tokens:
  try:
    avg = avg + numpy.array(model.word_vec(word))
    count = count + 1
  except KeyError: pass
avg /= count 
i=200
model.most_similar("startup")
#model.similar_by_vector(avg, topn=1000)[i:i+100]

doc['tweets'] = doc.tweets.apply(lambda x: " ".join(re.sub(r'[^a-zA-Z]',' ',w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]',' ',w).lower() not in stopset))

doc.head(5)

tfidfvectoriser=TfidfVectorizer(max_features=64)
tfidfvectoriser.fit(doc.tweets)
tfidf_vectors=tfidfvectoriser.transform(doc.tweets)

tfidf_vectors.shape

tfidf_vectors=tfidf_vectors.toarray()
print (tfidf_vectors[0])

pairwise_similarities=np.dot(tfidf_vectors,tfidf_vectors.T)
pairwise_differences=euclidean_distances(tfidf_vectors)

print(tfidf_vectors[0])
print(pairwise_similarities.shape)
print(pairwise_similarities[0][:])

def most_similar(doc_id,similarity_matrix,matrix):
    print (f'Document: {doc.iloc[doc_id]["tweets"]}')
    print ('\n')
    print (f'Similar Documents using {matrix}:')
    if matrix=='Cosine Similarity':
        similar_ix=np.argsort(similarity_matrix[doc_id])[::-1]
    elif matrix=='Euclidean Distance':
        similar_ix=np.argsort(similarity_matrix[doc_id])
    for ix in similar_ix:
        if ix==doc_id:
            continue
        print('\n')
        print (f'Document: {doc.iloc[ix]["tweets"]}')
        print (f'{matrix} : {similarity_matrix[doc_id][ix]}')

most_similar(1,pairwise_similarities,'Cosine Similarity')

most_similar(1,pairwise_differences,'Euclidean Distance')

#!pip install sentence_transformers
from sentence_transformers import SentenceTransformer

sbert_model = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')

document_embeddings = sbert_model.encode(doc['tweets'])

pairwise_similarities=cosine_similarity(document_embeddings)
pairwise_differences=euclidean_distances(document_embeddings)

most_similar(1,pairwise_similarities,'Cosine Similarity')

most_similar(1,pairwise_differences,'Euclidean Distance')
