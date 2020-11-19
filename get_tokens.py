import string

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from unidecode import unidecode

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

def get_tokens(tweet):
    corpus = tweet.lower()
    corpus = corpus.translate(str.maketrans(punctuations, ' ' * len(punctuations)))
    tokens = tokenizer.tokenize(corpus)
    cleaned_corpus = []
    for token in tokens:
        token = ''.join([i for i in token if not i.isdigit()])
        if (token not in stopset) and (len(token) > 2):
            token = lemmatize(token)
            token = token.translate(str.maketrans('', '', string.punctuation))
            token = unidecode(token)
            cleaned_corpus.append(token)
        else:
            continue
    return cleaned_corpus


def lemmatize(token):
    lemmatized_token1 = lemmatizer.lemmatize(token, pos="v")
    lemmatized_token2 = lemmatizer.lemmatize(lemmatized_token1, pos="n")
    lemmatized_token3 = lemmatizer.lemmatize(lemmatized_token2, pos="a")
    lemmatized_token = lemmatizer.lemmatize(lemmatized_token3, pos="r")
    return lemmatized_token
