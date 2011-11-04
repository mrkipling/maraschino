from flask import Flask, jsonify, render_template, request
from database import db_session
import hashlib, json, jsonrpclib, urllib

from htpcfrontend import app
from settings import *
from tools import *

AVAILABLE_MODULES = [
    {
        'id': 'applications',
        'label': 'Applications',
        'description': 'Allows you to link to whatever applications you want (SABnzbd, SickBeard, etc.)',
        'mandatory_static': False,
        'defaults': {
            'static': True,
            'poll': 0,
            'delay': 0,
        },
    },
    {
        'id': 'recently_added',
        'label': 'Recently added',
        'description': 'Shows you episodes recently added to your library.',
        'mandatory_static': False,
        'defaults': {
            'static': False,
            'poll': 350,
            'delay': 0,
        },
    },
]

@app.route('/xhr/add_module_dialog')
@requires_auth
def add_module_dialog():
    return render_template('add_module_dialog.html',
        available_modules = AVAILABLE_MODULES,
    )
