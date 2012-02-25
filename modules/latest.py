from flask import Flask, jsonify, render_template

from Maraschino import app
from settings import *
from maraschino.tools import *

@app.route('/xhr/latest')
@requires_auth
def xhr_latest():
    return render_template('latest.html',
    )