import numpy
import json


class User:
    def __init__(self, userid):
        self.userid = userid
        self.username = ""
        self.name = ""
        self.location = ""
        self.gender = ""
        self.bio = ""
        self.tweets = []
        self.cleaned_tweets = []
        self.tokens = []
        self.tfidf_vector = numpy.zeros(shape=(300, 1))
        self.transformer_vector = numpy.zeros(shape=(512, 1))

    def set_username(self, username):
        self.username = username

    def set_name(self, name):
        self.name = name

    def set_location(self, location):
        self.location = location

    def set_bio(self, bio):
        self.bio = bio

    def set_gender(self, gender):
        self.gender = gender

    def add_tweets(self, tweets):
        self.tweets = tweets

    def add_cleaned_tweets(self, cleaned_tweets):
        self.cleaned_tweets = cleaned_tweets

    def add_tokens(self, tokens):
        self.tokens = tokens

    def set_transformer_vector(self, transformer_vector):
        self.transformer_vector = transformer_vector

    def set_tfidf_vector(self, tfidf_vector):
        self.tfidf_vector = tfidf_vector

    def to_json(self):
        return json.dumps(self, default=vars, sort_keys=True, indent=4)
