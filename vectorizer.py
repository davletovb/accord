import tensorflow_hub as hub

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")

tweets = tweet_df['cleaned'].tolist()

meanvec = np.mean([embed([tweet]) for tweet in tweets], axis=0)

print(meanvec)
