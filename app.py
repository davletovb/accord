from concurrent.futures import ThreadPoolExecutor

import flask
from flask import request, jsonify
import os
import json

import ann_index
import get_twitter_data

executor = ThreadPoolExecutor(max_workers=4)

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to accord API</h1>
<p>A prototype API for text based matching.</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/users/all', methods=['GET'])
def api_all():
    users = []
    with os.scandir('users/') as entries:
        for entry in entries:
            if (entry.name != "index.ann") and (entry.name != "index_map.json"):
                with open('users/' + entry.name, 'r') as file:
                    user_profile = json.load(file)
                users.append(user_profile)
            else:
                pass

    return jsonify(users)


@app.route('/api/v1/resources/users/id', methods=['GET'])
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
    executor.submit(get_twitter_data.pre_process, userid=userid)

    return user


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
