from flask import Flask, jsonify, render_template, request
from database import db_session
import hashlib, json, jsonrpclib, urllib

app = Flask(__name__)

from settings import *
from noneditable import *
from tools import *

from applications import *
from controls import *
from currently_playing import *
from library import *
from recently_added import *
from sabnzbd import *
from trakt import *

@app.route('/')
@requires_auth
def index():
    return render_template('index.html',
        modules = MODULES,
        show_currently_playing = SHOW_CURRENTLY_PLAYING,
        fanart_backgrounds = FANART_BACKGROUNDS,
        applications = APPLICATIONS,
    )

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
