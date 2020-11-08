import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.
users = [
    {'id': 0,
     'name': 'A Fire Upon the Deep',
     'username': 'Vernor Vinge',
     'bio': 'The coldsleep itself was dreamless.',
     'date': '1992'},
    {'id': 1,
     'name': 'The Ones Who Walk Away From Omelas',
     'username': 'Ursula K. Le Guin',
     'bio': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'date': '1973'},
    {'id': 2,
     'name': 'Dhalgren',
     'username': 'Samuel R. Delany',
     'bio': 'to wound the autumnal city.',
     'date': '1975'}
]


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/users/all', methods=['GET'])
def api_all():
    return jsonify(users)

app.run()
