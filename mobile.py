import jsonrpclib
import maraschino.logger as logger

from flask import Flask, render_template
from Maraschino import app

from maraschino.tools import *
from maraschino.noneditable import *
from modules.recently_added import get_recently_added_episodes

@app.route('/mobile/temp_index_url')
@requires_auth
def mobile_index():
    return render_template('mobile/index.html')

@app.route('/mobile')
@requires_auth
def recently_added_episodes():
    return render_template('mobile/recent_episodes.html')
