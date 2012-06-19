import sys
from flask import Flask, jsonify, render_template

from maraschino import app, RUNDIR
from maraschino.tools import *
from maraschino.models import Application
from maraschino.database import db_session

@app.route('/xhr/applications')
@requires_auth
def xhr_applications():
    applications = Application.query.order_by(Application.position)
    new_tab = get_setting_value('app_new_tab') == '1'

    return render_template('applications.html',
        applications = applications,
        new_tab = new_tab,
    )

@app.route('/xhr/add_application_dialog')
@requires_auth
def add_application_dialog():
    return add_edit_application_dialog()

@app.route('/xhr/edit_application_dialog/<application_id>')
@requires_auth
def edit_application_dialog(application_id):
    return add_edit_application_dialog(application_id)

def add_edit_application_dialog(application_id=None):
    application = None

    dir = RUNDIR + '/static/images/applications'

    icons = get_file_list(
        folder = dir,
        extensions = ['.png', '.jpg'],
        prepend_path = False,
    )

    if application_id:
        try:
            application = Application.query.filter(Application.id == application_id).first()

        except:
            pass

    return render_template('add_edit_application_dialog.html',
        application = application,
        icons = icons,
    )

@app.route('/xhr/add_edit_application', methods=['POST'])
@requires_auth
def add_edit_application():
    name = request.form['name']
    url = request.form['url']
    description = request.form['description']
    image = request.form['image']
    position = request.form['position']

    if name == '' or url == '':
        return jsonify({ 'status': 'error' })

    if position == '':
        position = None

    if 'application_id' in request.form:
        application = Application.query.filter(Application.id == request.form['application_id']).first()
        application.name = name
        application.url = url
        application.description = description
        application.image = image
        application.position = position

    else:
        application = Application(
            name,
            url,
            description,
            image,
            position,
        )

    db_session.add(application)
    db_session.commit()

    return xhr_applications()

@app.route('/xhr/delete_application/<application_id>', methods=['POST'])
@requires_auth
def delete_application(application_id):
    try:
        application = Application.query.filter(Application.id == application_id).first()
        db_session.delete(application)
        db_session.commit()

    except:
        return jsonify({ 'status': 'error' })

    return xhr_applications()

@app.route('/xhr/show_application/<application_id>')
@requires_auth
def show_application(application_id):
    application = None
    message = None
    
    try:
        application = Application.query.filter(Application.id == application_id).first()
    
    except:
        message = 'Could not display application page'
        
    return render_template('application_window.html',
        message = message,
        application = application,
    )
