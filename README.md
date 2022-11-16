# About

Accord is a matching algorithm for tweets. It was designed to find similar users and connections between them. Also as a text-based match-making. This can be also useful for understanding the conversation around a certain topic, or for identifying potential customers who have similar interests.

# Steps
1. Downloads 1000 tweets of a user and then cleans for token vectorization.

2. Data cleaning
Remove URLs, EMOJIs, MENTIONs, SMILEYs
Tokenization
Lemmatization
Remove stop words
Remove punctuations
Remove digits

3. User profile vectorization, and clustering based on vectors by taking weighted average of the tokens.

4. Used Annoy open sourced by Spotify for indexing the vectors.

5. Next step is extracting named entities from tweets, such as products and work of arts.

# Requirements

To install the requirements, first run this:

pip install -r requirements.txt

After installing everything, download the models for spacy:

python -m spacy download en_core_web_lg

Also, manually download the sense2vec pretrained vectors from https://github.com/explosion/sense2vec (4GB)
