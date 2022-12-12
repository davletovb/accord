from flair.models import SequenceTagger
from flair.data import Sentence
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import re
from os import path

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from vectors import VectorIndex, TextVectorizer
from twitter import TwitterAPI

tokenizer = TweetTokenizer()
lemmatizer = WordNetLemmatizer()
punctuations = '''!0123456789()-=—!→–[]{};:+`'"“”\,<>.?/@#$%^&*_~'''
stopset = stopwords.words('english')

abbrevs = {
    'dm': 'direct message',
    'ai': 'artificial intelligence',
    'ar': 'augmented reality',
    'vr': 'virtual reality',
    'ml': 'machine learning',
    'btc': 'bitcoin',
    'eth': 'ethereum'
}


class PreProcessor:
    def __init__(self):

        self.twitter = TwitterAPI()

    def get_tokens(self, tweet):
        corpus = tweet.lower()
        tokens = tokenizer.tokenize(corpus)
        cleaned_corpus = []
        for token in tokens:
            if (token not in stopset) and (len(token) > 2):
                cleaned_corpus.append(token)
            else:
                continue
        return cleaned_corpus

    def lemmatize(self, token):
        lemmatized_token1 = lemmatizer.lemmatize(token, pos="v")
        lemmatized_token2 = lemmatizer.lemmatize(lemmatized_token1, pos="n")
        lemmatized_token3 = lemmatizer.lemmatize(lemmatized_token2, pos="a")
        lemmatized_token = lemmatizer.lemmatize(lemmatized_token3, pos="r")
        return lemmatized_token

    # extract entities, products, books, movies, songs from a text file using hugingface's transformers library

    def get_entities(tweet_df):
        tokenizer = AutoTokenizer.from_pretrained(
            "xlm-roberta-large-finetuned-conll03-english")
        model = AutoModelForTokenClassification.from_pretrained(
            "xlm-roberta-large-finetuned-conll03-english")
        nlp = pipeline("ner", model=model, tokenizer=tokenizer)

        print("Extracting entities from tweets")
        entities = []

        for tweet in tweet_df['text']:
            tweet_entities = []
            for entity in nlp(tweet):
                tweet_entities.append(
                    entity['word'][1:] + "|" + entity['entity'][2:])
            entities.append(tweet_entities)

        #entities = tweet_df['text'].apply(lambda x: nlp(x))

        tweet_df['entities'] = entities
        print("Entities extracted")
        return tweet_df

    def get_all_entities(self, tweet_df):

        print("Extracting entities from tweets")
        entities = []

        # load tagger
        tagger = SequenceTagger.load("flair/ner-english-ontonotes-large")

        for tweet in tweet_df['text']:
            tweet_entities = []
            sentence = Sentence(tweet)
            tagger.predict(sentence)
            # iterate over entities and print
            for entity in sentence.get_spans('ner'):
                tweet_entities.append(entity.text + "|" + entity.tag)
            entities.append(tweet_entities)

        print("Entities extracted")
        tweet_df['entities'] = entities
        return tweet_df

    def pre_process(self, userid):
        if not path.exists('twitter_data/' + userid + '.json'):
            print("Getting tweets for user: " + userid)
            tweet_df = self.twitter.get_user_tweets(userid)
            # tweet_df = self.get_all_entities(tweet_df) # extract entities, for later use
            # Create a column for hashtags
            tweet_df.insert(loc=4, column='hashtag',
                            value=tweet_df['text'].apply(lambda x: re.findall(r'\B#\w*[a-zA-Z]+\w*', x)))
            cleaned_tweet_df = self.get_cleaned_tweets(userid, tweet_df)
            words = cleaned_tweet_df['tokens'].tolist()
            vectorizer = TextVectorizer()
            vectorizer.calculate_vector(userid, words)
            index = VectorIndex()
            # this method should only add the new vector, instead of rebuilding the whole index
            index.add_user()
        else:
            print("User data already exist")

    def get_cleaned_tweets(self, userid, tweet_df):
        print("Cleaning tweets for user: " + userid)
        punctuations = '''!0123456789()-=—!→–[]{};:+`'"“”\,<>.?/@#$%^&*_~'''

        # remove urls and mentions without using preprocessor
        tweet_df['cleaned'] = tweet_df['text'].apply(
            lambda x: re.sub(r'http\S+', '', x))
        tweet_df['cleaned'] = tweet_df['cleaned'].apply(
            lambda x: re.sub(r'@\S+', '', x))
        # remove punctuations
        tweet_df['cleaned'] = tweet_df['cleaned'].apply(
            lambda x: "".join([char for char in x if char not in punctuations]))
        # tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: x.translate(str.maketrans(punctuations, ' ' * len(punctuations))))
        tweet_df['cleaned'] = tweet_df.cleaned.apply(
            lambda x: self.remove_emojis(x))
        tweet_df['cleaned'] = tweet_df.cleaned.apply(
            lambda x: x.replace('...', ' '))
        tweet_df['cleaned'] = tweet_df.cleaned.apply(
            lambda x: ' '.join(x.split()))

        print("Tweets cleaned")
        #tokens = [get_tokens.get_tokens(tweet) for tweet in tweet_df['cleaned']]
        tweet_df['tokens'] = tweet_df['cleaned'].apply(
            lambda x: self.get_tokens(x))

        tweet_df.to_json('twitter_data/' + userid + '.json')
        print('Cleaned tweets saved')

        return tweet_df

    def remove_emojis(self, data):
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
