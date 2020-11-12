import flask
from flask import request, jsonify
import json
import get_twitter_data

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.
users = [
    {'id': 0,
     'name': 'Vernor Vinge',
     'username': 'dunaha',
     'bio': 'The coldsleep itself was dreamless.',
     'date': '1992'},
    {'id': 1,
     'name': 'Ursula K. Le Guin',
     'username': 'tandaram',
     'bio': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'date': '1973'},
    {'id': 2,
     'name': 'Samuel R. Delany',
     'username': 'dhalgran',
     'bio': 'to wound the autumnal city.',
     'date': '1975'}
]


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/users/all', methods=['GET'])
def api_all():
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

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for user in users:
        if user['id'] == userid:
            results.append(user)
            return jsonify(results)
        else:
            user = get_twitter_data.get_user(userid)
            user_json = user._json
            with open('users/' + userid + '.json', 'w') as json_file:
                json.dump(user_json, json_file, ensure_ascii=False)
            return user_json
    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.


@app.route('/api/v1/resources/users', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    date = query_parameters.get('date')
    name = query_parameters.get('name')

    results = []

    if id:
        for user in users:
            if user['id'] == id:
                results.append(user)
    if date:
        for user in users:
            if user['date'] == date:
                results.append(user)
    if name:
        for user in users:
            if user['name'] == name:
                results.append(user)
    if not (id or date or name):
        return page_not_found(404)

    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()
