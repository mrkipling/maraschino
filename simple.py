# -*- coding: utf-8 -*-
"""Simple mode"""

import jsonrpclib

from flask import render_template
from maraschino import app, logger

from maraschino.tools import *
from maraschino.noneditable import *

@app.route('/simple/')
@requires_auth
def simple_index():
    return render_template('simple/index.html')
