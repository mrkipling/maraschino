from flask import Flask, render_template

from maraschino import app
from settings import *
from tools import *

@app.route('/xhr/applications')
@requires_auth
def xhr_applications():
    applications = Application.query.order_by(Application.position)

    return render_template('applications.html',
        applications = applications,
    )

@app.route('/xhr/add_application_dialog')
@requires_auth
def add_application_dialog():
    return add_edit_application_dialog()

@app.route('/xhr/edit_application_dialog/<application>')
@requires_auth
def edit_application_dialog(application):
    return add_edit_application_dialog(application)

def add_edit_application_dialog(application=None):
    return render_template('add_edit_application_dialog.html',
        application = None,
    )
