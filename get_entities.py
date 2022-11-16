# extract entities, books, movies, songs from a text file using hugingface's transformers library


def get_entities(tweet_df):
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

    tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
    model = AutoModelForTokenClassification.from_pretrained("xlm-roberta-large-finetuned-conll03-english")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)

    print("Extracting entities from tweets")
    entities = []

    for tweet in tweet_df['text']:
        tweet_entities = []
        for entity in nlp(tweet):
            tweet_entities.append(entity['word'][1:] + "|" + entity['entity'][2:])
        entities.append(tweet_entities)

    #entities = tweet_df['text'].apply(lambda x: nlp(x))

    tweet_df['entities'] = entities
    print("Entities extracted")
    return tweet_df

def get_all(tweet_df):
    from flair.data import Sentence
    from flair.models import SequenceTagger
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
        

