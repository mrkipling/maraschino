from flask import Flask, jsonify, render_template

from maraschino import app
from settings import *
from tools import *

from models import Application

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

@app.route('/xhr/add_application', methods=['POST'])
@requires_auth
def add_application():
    return add_edit_application()

@app.route('/xhr/edit_application/<application>', methods=['POST'])
@requires_auth
def edit_application():
    return add_edit_application(application)

def add_edit_application(application=None):
    name = request.form['name']
    url = request.form['url']
    description = request.form['description']
    image = request.form['image']

    if name == '' or url == '':
        return jsonify({ 'status': 'error' })

    application = Application(
        name,
        url,
        description,
        image,
    )

    db_session.add(application)
    db_session.commit()

    return xhr_applications()
