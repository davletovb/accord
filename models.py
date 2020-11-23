import numpy as np
import json
import os


class User:
    def __init__(self, userid, username, name, location, bio, profile_picture, verified, protected, url, twitter_created):
        self.userid = userid
        self.username = username
        self.name = name
        self.location = location
        self.bio = bio
        self.profile_picture = profile_picture
        self.verified = verified
        self.protected = protected
        self.url = url
        self.twitter_created = twitter_created
        self.tweets = None
        self.word2vec_vector = np.zeros(shape=(300, 1))
        self.bert_vector = np.zeros(shape=(512, 1))

    @property
    def userid(self):
        return self.userid

    @userid.setter
    def userid(self, userid):
        self.userid = userid

    @property
    def username(self):
        return self.username

    @username.setter
    def username(self, username):
        self.username = username

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, name):
        self.name = name

    @property
    def location(self):
        return self.location

    @location.setter
    def location(self, location):
        self.location = location

    @property
    def bio(self):
        return self.bio

    @bio.setter
    def bio(self, bio):
        self.bio = bio

    @property
    def tweets(self):
        return self.tweets

    @tweets.setter
    def tweets(self, tweets):
        self.tweets = tweets

    @property
    def bert_vector(self):
        return self.bert_vector

    @bert_vector.setter
    def bert_vector(self, bert_vector):
        self.bert_vector = bert_vector

    @property
    def word2vec_vector(self):
        return self.word2vec_vector

    @word2vec_vector.setter
    def word2vec_vector(self, word2vec_vector):
        self.word2vec_vector = word2vec_vector

    def save_user(self):
        if not os.path.exists('users/' + self.userid + '.json'):
            with open('users/' + self.userid + '.json', 'w') as json_file:
                json.dump(self, json_file, indent=4, ensure_ascii=False, default=str)

    def save_tweets(self):
        if not os.path.exists('data/' + self.userid + '.json'):
            with open('data/' + self.userid + '.json', 'w') as json_file:
                json.dump(self.tweets, json_file, indent=4, ensure_ascii=False, default=str)

    def save_word2vec(self):
        if not os.path.exists('vectors/word/' + self.userid + '.npy'):
            np.save('vectors/word/' + self.userid + '.npy', self.word2vec_vector)

    def save_bert_vector(self):
        if not os.path.exists('vectors/sentence/' + self.userid + '.npy'):
            np.save('vectors/sentence/' + self.userid + '.npy', self.bert_vector)

    def __repr__(self):
        return "<User: {}>".format(self.userid)

    def to_json(self):
        return json.dumps(self, default=vars, sort_keys=True, indent=4)


class Tweet:
    def __init__(self, tweetid):
        self.tweetid = tweetid
        self.date = None
        self.text = ""
        self.cleaned_text = ""
        self.tokens = None
        self.like_count = 0
        self.retweet_count = 0

    @property
    def tweetid(self):
        return self.tweetid

    @tweetid.setter
    def tweetid(self, tweetid):
        self.tweetid = tweetid

    @property
    def text(self):
        return self.text

    @text.setter
    def text(self, text):
        self.text = text

    @property
    def cleaned_text(self):
        return self.cleaned_text

    @cleaned_text.setter
    def cleaned_text(self, cleaned_text):
        self.cleaned_text = cleaned_text

    @property
    def tokens(self):
        return self.tokens

    @tokens.setter
    def tokens(self, tokens):
        self.tokens = tokens

    @property
    def like_count(self):
        return self.like_count

    @like_count.setter
    def like_count(self, like_count):
        self.like_count = like_count

    @property
    def retweet_count(self):
        return self.retweet_count

    @retweet_count.setter
    def like_count(self, retweet_count):
        self.retweet_count = retweet_count

    def __repr__(self):
        return "<Tweet: {}>".format(self.tweetid)

    def to_json(self):
        return json.dumps(self, default=vars, sort_keys=True, indent=4)
