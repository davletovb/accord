from concurrent.futures import ThreadPoolExecutor

import flask
from flask import request, jsonify, render_template

from vectors import VectorIndex
from twitter import TwitterAPI
from preprocess import PreProcessor

executor = ThreadPoolExecutor(max_workers=4)

app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    # Return the HTML template for the home page
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():

    userid = request.form['userid']

    # use executor to run get_user, get_top_tweets, and pre_process in parallel
    twitter = TwitterAPI()
    user = executor.submit(twitter.get_user_profile, userid=userid).result()

    # preprocess user's tweets if they don't exist
    preprocessor = PreProcessor()
    executor.submit(preprocessor.pre_process, userid=userid).result()

    # get top tweets from user
    top_tweets = executor.submit(
        twitter.get_top_tweets, userid=userid).result()

    # get similar users from ann_index using executor to run in parallel
    index = VectorIndex()
    similar_users = executor.submit(
        index.search, userid=userid).result()

    return render_template('search.html', profile_picture=user['profile_picture'], username=user['username'], name=user['name'], location=user['location'], bio=user['bio'],
                           followers_count=user['followers_count'], twitter_created_at=user['twitter_created_at'], top_tweets=top_tweets, similar_users=similar_users)


@app.route('/api/v1/resources/users', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'userid' in request.args:
        userid = request.args['userid']
    else:
        return page_not_found(404)

    twitter = TwitterAPI()
    preprocessor = PreProcessor()
    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    user = executor.submit(twitter.get_user_profile, userid=userid).result()
    #executor.submit(get_twitter_data.get_followers, userid=userid)
    executor.submit(preprocessor.pre_process, userid=userid)

    return jsonify(user)


@app.route('/api/v1/resources/users/profile', methods=['GET'])
def api_user_profile():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'userid' in request.args:
        userid = request.args['userid']
    else:
        return page_not_found(404)

    twitter = TwitterAPI()
    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    user = twitter.get_user_profile(userid)

    return jsonify(user)


@app.route('/api/v1/resources/users/tweets', methods=['GET'])
def api_top_tweets():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'userid' in request.args:
        userid = request.args['userid']
    else:
        return page_not_found(404)

    twitter = TwitterAPI()
    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    tweets = twitter.get_top_tweets(userid)

    return jsonify(tweets)


@app.route('/api/v1/resources/users/neighbors', methods=['GET'])
def api_neighbors():
    if 'userid' in request.args:
        userid = request.args['userid']
    else:
        return page_not_found(404)

    index = VectorIndex()
    results = index.search(userid, 'word')

    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run()
