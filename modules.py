from flask import Flask, jsonify, render_template, request
from database import db_session
import copy, json

from maraschino import app
from settings import *
from tools import *

from database import *
from models import Module

# name, label, description, and static are not user-editable and are taken from here
# poll and delay are user-editable and saved in the database - the values here are the defaults
# settings are also taken from the database - the values here are defaults
# if static = True then poll and delay are ignored

AVAILABLE_MODULES = [
    {
        'name': 'applications',
        'label': 'Applications',
        'description': 'Allows you to link to whatever applications you want (SABnzbd, SickBeard, etc.)',
        'static': True,
        'poll': 0,
        'delay': 0,
    },
    {
        'name': 'diskspace',
        'label': 'Disk space',
        'description': 'Shows you available disk space on your various drives.',
        'static': False,
        'poll': 350,
        'delay': 0,
    },
    {
        'name': 'library',
        'label': 'Media library',
        'description': 'Allows you to browse your media library and select items to play in XBMC.',
        'static': True,
        'poll': 0,
        'delay': 0,
    },
    {
        'name': 'recently_added',
        'label': 'Recently added',
        'description': 'Shows you episodes recently added to your library.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'num_recent_videos',
                'value': 2,
                'description': 'Number of videos of each type to display',
            },
        ]
    },
    {
        'name': 'sabnzbd',
        'label': 'SABnzbd+',
        'description': 'Shows you information about your SABnzbd+ downloads.',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
            {
                'key': 'sabnzbd_url',
                'value': 'http://<hostname>:<port>/api?apikey=<apikeygoeshere>',
                'description': 'SABnzbd URL',
            },
            {
                'key': 'num_queue_items',
                'value': 5,
                'description': 'Number of queue items to show',
            },
        ]
    },
    {
        'name': 'synopsis',
        'label': 'Synopsis',
        'description': 'Shows you a plot synopsis of what you are currently watching.',
        'static': True,
        'poll': 0,
        'delay': 0,
    },
    {
        'name': 'trakt',
        'label': 'trakt.tv',
        'description': 'Shows you what people are saying about what you are watching and allows you to add your own comments.',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'trakt_api_key',
                'value': '',
                'description': 'Trakt API key',
            },
            {
                'key': 'trakt_username',
                'value': '',
                'description': 'Trakt username',
            },
            {
                'key': 'trakt_password',
                'value': '',
                'description': 'Trakt password',
            },
        ]
    },
]

SERVER_SETTINGS = [
    {
        'key': 'server_hostname',
        'value': 'localhost',
        'description': 'XBMC hostname/IP',
    },
    {
        'key': 'server_port',
        'value': '8080',
        'description': 'XBMC port ',
    },
    {
        'key': 'server_username',
        'value': '',
        'description': 'XBMC username',
    },
    {
        'key': 'server_password',
        'value': '',
        'description': 'XBMC password',
    },
#     {
#         'key': 'global_auth',
#         'value': '0',
#         'description': 'Use the same username/password throughout the app.',
#         'type': 'bool',
#     },
    {
        'key': 'fanart_backgrounds',
        'value': '1',
        'description': 'Show fanart backgrounds when watching media',
        'type': 'bool',
    },
    {
        'key': 'random_backgrounds',
        'value': '0',
        'description': 'Use a random background when not watching media',
        'type': 'bool',
    },
    {
        'key': 'server_macaddress',
        'value': '',
        'description': 'XBMC mac address',
    },
]

@app.route('/xhr/add_module_dialog')
@requires_auth
def add_module_dialog():
    modules_on_page = Module.query.all()
    available_modules = copy.copy(AVAILABLE_MODULES)

    for module_on_page in modules_on_page:
        for available_module in available_modules:
            if module_on_page.name == available_module['name']:
                available_modules.remove(available_module)
                break

    return render_template('add_module_dialog.html',
        available_modules = available_modules,
    )

@app.route('/xhr/add_module', methods=['POST'])
@requires_auth
def add_module():
    try:
        module_id = request.form['module_id']
        column = request.form['column']
        position = request.form['position']

        # make sure that it's a valid module

        module_info = get_module_info(module_id)

        if not module_info:
            raise Exception

    except:
        return jsonify({ 'status': 'error' })

    module = Module(
        module_info['name'],
        column,
        position,
        module_info['poll'],
        module_info['delay'],
    )

    db_session.add(module)

    # if module template has extra settings then create them in the database
    # with default values if they don't already exist

    if 'settings' in module_info:
        for s in module_info['settings']:
            setting = get_setting(s['key'])

            if not setting:
                setting = Setting(s['key'], s['value'])
                db_session.add(setting)

    db_session.commit()

    module_info['template'] = '%s.html' % (module_info['name'])

    # if the module is static and doesn't have any extra settings, return
    # the rendered module

    if module_info['static'] and not 'settings' in module_info:
        return render_template('placeholder_template.html',
            module = module_info
        )

    # otherwise return the rendered module settings dialog

    else:
        return module_settings_dialog(module_info['name'])

@app.route('/xhr/rearrange_modules', methods=['POST'])
@requires_auth
def rearrange_modules():
    try:
        modules = json.JSONDecoder().decode(request.form['modules'])

    except:
        return jsonify({ 'status': 'error' })

    for module in modules:
        try:
            m = Module.query.filter(Module.name == module['name']).first()
            m.column = module['column']
            m.position = module['position']
            db_session.add(m)

        except:
            pass

    db_session.commit()

    return jsonify({ 'status': 'success' })

@app.route('/xhr/remove_module/<name>', methods=['POST'])
@requires_auth
def remove_module(name):
    module = Module.query.filter(Module.name == name).first()
    db_session.delete(module)
    db_session.commit()

    return jsonify({ 'status': 'success' })

@app.route('/xhr/module_settings_dialog/<name>')
@requires_auth
def module_settings_dialog(name):
    module_info = get_module_info(name)
    module_db = get_module(name)

    if module_info and module_db:

        # look at the module template so we know what settings to look up

        module = copy.copy(module_info)

        # look up poll and delay from the database

        module['poll'] = module_db.poll
        module['delay'] = module_db.delay

        # iterate through possible settings and get values from database

        if 'settings' in module:
            for s in module['settings']:
                setting = get_setting(s['key'])

                if setting:
                    s['value'] = setting.value

        return render_template('module_settings_dialog.html',
            module = module,
        )

    return jsonify({ 'status': 'error' })

@app.route('/xhr/module_settings_cancel/<name>')
@requires_auth
def module_settings_cancel(name):
    module = get_module_info(name)

    if module:
        module['template'] = '%s.html' % (module['name'])

        return render_template('placeholder_template.html',
            module = module,
        )

    return jsonify({ 'status': 'error' })

@app.route('/xhr/module_settings_save/<name>', methods=['POST'])
@requires_auth
def module_settings_save(name):
    try:
        settings = json.JSONDecoder().decode(request.form['settings'])

    except:
        return jsonify({ 'status': 'error' })

    for s in settings:

        # poll and delay are stored in the modules tables

        if s['name'] == 'poll' or s['name'] == 'delay':
            module = get_module(name)

            if s['name'] == 'poll':
                module.poll = int(s['value'])

            if s['name'] == 'delay':
                module.delay = int(s['value'])

            db_session.add(module)

        # other settings are stored in the settings table

        else:
            setting = get_setting(s['name'])

            if not setting:
                setting = Setting(s['name'])

            setting.value = s['value']
            db_session.add(setting)

    db_session.commit()

    # you can't cancel server settings - instead, return an updated template
    # with 'Settings saved' text on the button

    if name == 'server_settings':
        return server_settings_dialog(updated=True)

    # for everything else, return the rendered module

    return module_settings_cancel(name)

@app.route('/xhr/server_settings_dialog')
@requires_auth
def server_settings_dialog(updated=False):
    settings = copy.copy(SERVER_SETTINGS)

    for s in settings:
         setting = get_setting(s['key'])

         if setting:
             s['value'] = setting.value

    return render_template('server_settings_dialog.html',
        server_settings = settings,
        updated = updated,
    )

# helper method which returns a module record from the database

def get_module(name):
    try:
        return Module.query.filter(Module.name == name).first()

    except:
        return None

# helper method which returns a module template

def get_module_info(name):
    for available_module in AVAILABLE_MODULES:
        if name == available_module['name']:
            return available_module

    return None
