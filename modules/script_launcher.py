from flask import Flask, jsonify, render_template, request
import os, platform, ctypes, subprocess, datetime

from maraschino.tools import *
from maraschino import app, logger
from maraschino.database import db_session
from maraschino.models import Script
import maraschino


@app.route('/xhr/script_launcher/') 
@requires_auth
def xhr_script_launcher():
    scripts = []
    scripts_db = Script.query.order_by(Script.id)

    if scripts_db.count() > 0:
        for script_db in scripts_db:
            script = {}
            script['script'] = script_db.script
            script['label'] = script_db.label
            script['status'] = script_db.status
            script['id'] = script_db.id
            scripts.append(script)

    return render_template('script_launcher.html', 
                           scripts = scripts,)

@app.route('/xhr/script_launcher/script_status/<script_id>', methods=['GET', 'POST'])
def xhr_script_status(script_id):

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

    command = os.path.join(maraschino.SCRIPT_DIR,script.script)

    if (script.parameters):
        command = ''.join([command, ' ', script.parameters])

    #Parameters needed for scripts that update
    host = maraschino.HOST
    port = maraschino.PORT
    webroot = maraschino.WEBROOT

    if not webroot:
        webroot = '/'

    file_ext = os.path.splitext(script.script)[1]

    if (file_ext == '.py'):
        if (script.updates == 1):        
            #these are extra parameters to be passed to any scripts ran, so they 
            #can update the status if necessary
            extras = '--i "%s" --p "%s" --s "%s" --w "%s"' % (host, port, script.id, webroot)

            #the command in all its glory
            command = ''.join([command, ' ', extras])
            script.status="Script Started at: %s" % now.strftime("%m-%d-%Y %H:%M")
        else:
            script.status="Last Ran: %s" % now.strftime("%m-%d-%Y %H:%M")

        command =  ''.join(['python ', command])

    elif (file_ext in ['.sh', '.pl', '.cmd']):
        if (script.updates == 1):
            extras = '%s %s %s %s' % (host, port, script.id, webroot)
            #the command in all its glory
            command = ''.join([command, ' ', extras])
            script.status="Script Started at: %s" % now.strftime("%m-%d-%Y %H:%M")
        else:
            script.status="Last Ran: %s" % now.strftime("%m-%d-%Y %H:%M")

        if(file_ext == '.pl'):
            command = ''.join(['perl ', command])

        if(file_ext == '.cmd'):
            command = ''.join([command])


    logger.log('SCRIPT_LAUNCHER :: %s' % command, 'INFO')
    #now run the command
    subprocess.Popen(command, shell=True)

    db_session.add(script)
    db_session.commit()

    return xhr_script_launcher()    

@app.route('/xhr/add_script_dialog')
@requires_auth
def add_script_dialog():
    logger.log('SCRIPT_LAUNCHER :: add_script_dialog', 'DEBUG')
    return add_edit_script_dialog()

@app.route('/xhr/edit_script_dialog/<script_id>')
@requires_auth
def edit_script_dialog(script_id):
    return add_edit_script_dialog(script_id)

def add_edit_script_dialog(script_id=None):
    logger.log('SCRIPT_LAUNCHER :: add_edit_script_dialog', 'DEBUG')
    script = None
    logger.log('SCRIPT_LAUNCHER :: Getting file list', 'DEBUG')
    script_files = get_file_list(
        folder = maraschino.SCRIPT_DIR,
        extensions = ['.py', '.sh', '.pl', '.cmd'],
        prepend_path = False,
        prepend_path_minus_root = True
    )
    logger.log('SCRIPT_LAUNCHER :: Have file list', 'DEBUG')
    if script_id:
        try:
            script = Script.query.filter(Script.id == script_id).first()
        except:
            pass

    logger.log('SCRIPT_LAUNCHER :: Rendering remplate add_edit_script_dialog.html', 'DEBUG')
    return render_template('add_edit_script_dialog.html',
        script = script, script_files = script_files,
    )

@app.route('/xhr/add_edit_script', methods=['POST'])
@requires_auth
def add_edit_script():
    logger.log('SCRIPT_LAUNCHER :: add_edit_script() ', 'DEBUG')
    script = request.form['script_file']
    label = request.form['label']
    parameters = request.form['parameters']
    updates = 0


    try:
        if (request.form['type']):
            updates = 1
    except:
        pass
    #Check that we have the command and label
    if script == '':
        return jsonify({ 'status': 'Command Required' })
    if label == '':
        return jsonify({ 'status': 'Label Required' })

    #figure out if it is a new script or existing script
    if 'script_id' in request.form:
        db_script = Script.query.filter(Script.id == request.form['script_id']).first()
        db_script.script = script
        db_script.label = label
        db_script.parameters = parameters
        db_script.updates = updates

    else:
        db_script = Script(label,script, parameters,updates)

    #save it to the database
    try:
        db_session.add(db_script)
        db_session.commit()
    except Exception, e:
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