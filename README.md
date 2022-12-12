# Accord

## Overview

Accord is a matching algorithm that uses natural language processing and machine learning techniques to analyze the content of tweets and identify users who have similar interests or opinions. By comparing the words and phrases used in tweets, the algorithm can determine which users are likely to have similar interests and can recommend connections between them. Accord is a tool for identifying connections between Twitter users and understanding the conversation around certain topics. Its ability to analyze text-based data makes it a valuable resource for businesses, individuals, and researchers interested in understanding how people use Twitter.

## Applications

* One potential application of Accord is to help businesses identify potential customers who are interested in their products or services. By analyzing the tweets of users who are already customers, the algorithm can identify other users who are likely to be interested in the same products or services. This can help businesses target their marketing efforts more effectively and increase their chances of making successful sales.

* Another potential application of Accord is to help individuals find other users who are interested in the same topics or who share similar opinions. This can be useful for building networks of like-minded individuals, mentors and mentees, finding like-minded users to follow on Twitter, or simply for finding others who are interested in the same things.

* Accord can also be used as a text-based matchmaking tool. By analyzing the content of tweets (text) and extracting entities such as interests, hobbies, and opinions, the algorithm can identify users who are likely to be compatible with each other. By using Accord, users can find potential matches based on the content of their tweets.

## Usage

* Clone Repo:
```
git clone https://github.com/davletovb/accord.git
```

* Setup a virtual environment: 
```
virtualenv .virtualenv/accord
```

* Activate virtual environment:
```
source .virtualenv/accord
```

* Install all requirements using pip:
```
pip install -r requirements.txt
```

* Download this pre-trained vectors for this project:

```
wget https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2019_lg.tar.gz.001
wget https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2019_lg.tar.gz.002
wget https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2019_lg.tar.gz.003
```

You may run the following to merge the multi-part archives:

```
cat s2v_reddit_2019_lg.tar.gz.* > s2v_reddit_2019_lg.tar.gz
```

* After installing everything, download the models for spacy:

```
python -m spacy download en_core_web_lg
```

* Set environment variables:
```
export TWITTER_KEY = "TWITTER_KEY"
export TWITTER_SECRET_KEY = "TWITTER_SECRET_KEY"
```
These API keys for Twitter can be obtained at: https://developer.twitter.com/en/portal/dashboard

## Milestones

* User profile vectorization and clustering based on vectors done by taking weighted average of the tokens.

* Implemented the Annoy library, which was open-sourced by Spotify, to index the vectors and make the matching process faster and more efficient. It works extremely fast and gave better results than FAISS by Facebook.

* Next step is to extract named entities from tweets, such as products and works of art (music, movie, books, etc). This will enable us to match users based on their specific interests and provide even more accurate recommendations.

* Also, developing a web application where users can login and give permission to access their tweets and see other similar Twitter accounts.
