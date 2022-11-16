from concurrent.futures import ThreadPoolExecutor

import flask
from flask import request, jsonify

import ann_index
import get_twitter_data
import pandas as pd

executor = ThreadPoolExecutor(max_workers=4)

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    html = """
    <h1>Accord</h1>
    <p>Accord is a web app that helps you find people on Twitter who share your interests.</p>
    <p>Enter a Twitter username to get started.</p>
    <form action="/search" method="get">
        <input type="text" name="userid" placeholder="Twitter username">
        <input type="submit" value="Search">
    </form>
    """
    return html


@app.route('/search', methods=['GET'])
def search():
    # use executor to run get_user, get_top_tweets, and pre_process in parallel
    userid = request.args.get('userid')
    user = executor.submit(get_twitter_data.get_user, userid=userid).result()
    executor.submit(get_twitter_data.pre_process, userid=userid).result()
    top_tweets = executor.submit(get_twitter_data.get_top_tweets, userid=userid).result()
    top_tweets = pd.DataFrame(top_tweets)[['text','like_count','retweet_count','tweet_date']].to_html(index=False)

    # get similar users from ann_index using executor to run in parallel
    similar_users = executor.submit(ann_index.search_index, userid=userid).result()
    similar_users = pd.DataFrame(similar_users)[['username','name','bio','location','followers_count']].to_html(index=False)

    # show results in html
    html = """
        <h1>Accord</h1>
        <p>Accord is a web app that helps you find people on Twitter who share your interests.</p>
        <p>Enter a Twitter username to get started.</p>
        <form action="/search" method="get">
            <input type="text" name="userid" placeholder="Twitter username">
            <input type="submit" value="Search">
        </form>
        <h2>Results</h2>
        <h3> User Profile </h3>
        <p><img src="{profile_picture}" alt="Profile image" height="150"></p>
        <p>Username: {username}</p>
        <p>Name: {name}</p>
        <p>Location: {location}</p>
        <p>Bio: {bio}</p>
        <p>Followers: {followers_count}</p>
        <p>Profile created: {twitter_created_at}</p>
        <h3> Top Tweets </h3>
        <table>
            {top_tweets}
        </table>
        <h3> Similar Users </h3>
        <table>
            {similar_users}
        </table>
    """.format(
        profile_picture=user['profile_picture'],
        username=user['username'],
        name=user['name'],
        location=user['location'],
        bio=user['bio'],
        followers_count=user['followers_count'],
        twitter_created_at=user['twitter_created_at'],
        top_tweets=top_tweets,
        similar_users=similar_users
    )
    return html

@app.route('/api/v1/resources/users', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'userid' in request.args:
        userid = request.args['userid']
    else:
        return page_not_found(404)

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    user = executor.submit(get_twitter_data.get_user, userid=userid).result()
    #executor.submit(get_twitter_data.get_followers, userid=userid)
    executor.submit(get_twitter_data.pre_process, userid=userid)

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

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    user = get_twitter_data.get_user(userid)

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

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    tweets = get_twitter_data.get_top_tweets(userid)

    return jsonify(tweets)


@app.route('/api/v1/resources/users/neighbors', methods=['GET'])
def api_neighbors():
    if 'userid' in request.args:
        userid = request.args['userid']
    else:
        return page_not_found(404)

    results = ann_index.search_index(userid, 'word')

    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run()
