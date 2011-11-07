from flask import Flask, render_template

from maraschino import app
from settings import *
from tools import *

@app.route('/xhr/applications')
@requires_auth
def xhr_applications():
    return render_template('applications.html',
        applications = APPLICATIONS,
    )
