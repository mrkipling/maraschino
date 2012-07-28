from flask import Flask, jsonify, render_template, request
import os, platform, ctypes, subprocess, datetime

from Maraschino import app
from maraschino.noneditable import *
from maraschino.tools import *
from maraschino import logger as logger
from maraschino.database import db_session

from maraschino.models import Script



@app.route('/xhr/script_launcher/') 
@requires_auth
def xhr_script_launcher():
    scripts = []
    scripts_db = Script.query.order_by(Script.id)

    if scripts_db.count() > 0:
        for script_db in scripts_db:
            script = {}
            script['command'] = script_db.command
            script['label'] = script_db.label
            script['status'] = script_db.status
            script['id'] = script_db.id
            scripts.append(script)

    return render_template('script_launcher.html', 
                           scripts = scripts,)

@app.route('/xhr/script_launcher/script_status/<script_id>', methods=['GET', 'POST'])
def xhr_script_status(script_id):
    logger.log('SCRIPT_LAUNCHER :: xhr_script_status()', 'DEBUG')
    status = request.form['status']
    
    if status == '':
        return jsonify({ 'status': 'error: there was no status passed in' })

    script = Script.query.filter(Script.id == script_id).first()
    script.status = status

    try:
        db_session.add(script)
        db_session.commit()

    except:
        logger.log('SCRIPT_LAUNCHER :: Add Failed', 'ERROR')
        return jsonify({ 'status': 'error' })
    
    return xhr_script_launcher()


@app.route('/xhr/script_launcher/start_script/<script_id>')
@requires_auth
def xhr_start_script(script_id):
    
     #first get the script we want
    script = None
    message = None
    script = Script.query.filter(Script.id == script_id).first()
    now = datetime.datetime.now()
    
    command = None
    if (script.updates == 1):        
        #these are extra parameters to be passed to any scripts ran, so they 
        #can update the status if necessary
        host = maraschino.HOST
        port = maraschino.PORT
        webroot = maraschino.WEBROOT
        if webroot:
            extras = '--i "%s" --p "%s" --w "%s" --s "%s"' % (host, port, webroot, script.id)
        else:
            extras = '--i "%s" --p "%s" --s "%s"' % (host, port, script.id)
        #the command in all its glory
        command = '%s %s' % (script.command, extras)
        script.status="Script Started at: %s" % now.strftime("%m-%d-%Y %H:%M")
    else:
        command = script.command
        script.status="Last Ran: %s" % now.strftime("%m-%d-%Y %H:%M")
    
    logger.log('SCRIPT_LAUNCHER :: %s' % command, 'ERROR')
    #now run the command
    subprocess.Popen(command, shell=True)
    
    db_session.add(script)
    db_session.commit()
    
    return xhr_script_launcher()    

@app.route('/xhr/add_script_dialog')
@requires_auth
def add_script_dialog():
    return add_edit_script_dialog()

@app.route('/xhr/edit_script_dialog/<script_id>')
@requires_auth
def edit_script_dialog(script_id):
    return add_edit_script_dialog(script_id)

def add_edit_script_dialog(script_id=None):
    script = None

    if script_id:
        try:
            script = Script.query.filter(Script.id == script_id).first()
        except:
            pass

    return render_template('add_edit_script_dialog.html',
        script = script,
    )

@app.route('/xhr/add_edit_script', methods=['POST'])
@requires_auth
def add_edit_script():
    logger.log('SCRIPT_LAUNCHER :: add_edit_script() ', 'DEBUG')
    print request.form
    command = request.form['command']
    print command
    label = request.form['label']
    print label
    updates = 0
    try:
        print request.form['type']
        if (request.form['type']):
            updates = 1
    except:
        pass
    print "here"    
    #Check that we have the command and label
    if command == '':
        return jsonify({ 'status': 'Command Required' })
    if label == '':
        return jsonify({ 'status': 'Label Required' })
    
    #figure out if it is a new script or existing script
    if 'script_id' in request.form:
        script = Script.query.filter(Script.id == request.form['script_id']).first()
        script.command = command
        script.label = label
        script.updates = updates
    else:
        script = Script(label,command, updates)
        
    #save it to the database
    try:
        db_session.add(script)
        db_session.commit()
    except Exception, e:
        print e
        logger.log('SCRIPT_LAUNCHER :: Add Failed', 'ERROR')
        return jsonify({ 'status': 'Add Failed' })
    
    return xhr_script_launcher()


@app.route('/xhr/delete_script/<script_id>', methods=['POST'])
@requires_auth
def delete_script(script_id):
    try:
        script = Script.query.filter(Script.id == script_id).first()
        db_session.delete(script)
        db_session.commit()

    except:
        logger.log('SCRIPT_LAUNCHER :: Delete Failed', 'ERROR')
        return jsonify({ 'status': 'Delete Failed' })
    
    return xhr_script_launcher()