import re
import preprocessor as prep
#from nltk.corpus import stopwords

def clean(tweet_df):
    #stopset = stopwords.words('english')
    punctuations = '''!()-=—!→–[]|{};:+`"“”\,<>/@#$%^&*_~'''

    prep.set_options(prep.OPT.URL, prep.OPT.MENTION)

    cleaned = [prep.clean(text) for text in tweet_df['text']]

    tweet_df['cleaned'] = cleaned

    #tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: " ".join(re.sub(r'[^a-zA-Z]',' ',w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]',' ',w).lower() not in stopset))

    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: x.translate(str.maketrans(punctuations, ' '*len(punctuations))))
    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: remove_emojis(x))
    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: x.replace('...',' '))
    tweet_df['cleaned'] = tweet_df.cleaned.apply(lambda x: ' '.join(x.split()))

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
