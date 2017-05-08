import os

import flask
import jinja2

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

app = flask.Flask(__name__, static_url_path='')


@app.route('/')
def root():
    return flask.send_from_directory(os.path.join(staticdir), 'index.html')


@app.route('/scripts/<path:path>')
def send_scripts(path):
    return flask.send_from_directory('scripts', os.path.join('scripts', path))


@app.route('/styles/<path:path>')
def send_styles(path):
    return flask.send_from_directory(staticdir, os.path.join('styles', path))


@app.route('/service/user/<user>/login', methods=['POST', 'GET'])
def login(user):
    return flask.jsonify({
        "user": user,
        "token": "kaflaflibob",
        "role": [
            "o-admin"
        ]
    })


@app.route('/acl', methods=['POST', 'GET'])
def acl():
    return flask.jsonify([])


@app.route('/o')
def list_organisations():
    return flask.jsonify([
        {
            "name": "Aarhus Kommune",
            "user-key": "Aarhus Kommune",
            "uuid": "59141156-ed0b-457c-9535-884447c5220b",
            "valid-from": "05-05-2017"
        },
        {
            "name": "Aarhus Universitet",
            "user-key": "AU",
            "uuid": "9bfa4de4-ac66-40ba-aa65-255749f92dd9",
            "valid-from": "04-05-2017"
        }
    ])
