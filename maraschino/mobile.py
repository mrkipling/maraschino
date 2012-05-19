from flask import Flask, render_template
from Maraschino import app

from maraschino.tools import *

@app.route('/mobile')
@requires_auth
def mobile_index():
    return render_template('mobile/index.html')
