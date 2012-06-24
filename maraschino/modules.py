try:
    import json
except ImportError:
    import simplejson as json

from flask import Flask, jsonify, render_template, request
from maraschino.database import db_session

import maraschino
import copy

from maraschino import logger

from Maraschino import app
from maraschino.tools import *

from maraschino.database import *
from maraschino.models import Module, XbmcServer

# name, label, description, and static are not user-editable and are taken from here
# poll and delay are user-editable and saved in the database - the values here are the defaults
# settings are also taken from the database - the values here are defaults
# if static = True then poll and delay are ignored

AVAILABLE_MODULES = [
    {
        'name': 'applications',
        'label': 'Applications',
        'description': 'Allows you to link to whatever applications you want (SabNZBd, SickBeard, etc.)',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'app_new_tab',
                'value': '0',
                'description': 'Open application in new tab.',
                'type': 'bool',
            },
        ]
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
        'label': 'Media Library',
        'description': 'Allows you to browse your media library and select items to play in XBMC.',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'library_show_info',
                'value': '0',
                'description': 'Show media information by default',
                'type': 'bool',
            },
            {
                'key': 'library_use_bannerart',
                'value': '0',
                'description': 'Use Bannerart for TV shows',
                'type': 'bool',
            },
            {
                'key': 'library_watched_movies',
                'value': '1',
                'description': 'Show Watched Movies',
                'type': 'bool',
            },
            {
                'key': 'library_watched_tv',
                'value': '1',
                'description': 'Show Watched TV/Episodes',
                'type': 'bool',
            },
            {
                'key': 'library_show_power_buttons',
                'value': '1',
                'description': 'Show Power Controls',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'recently_added',
        'label': 'Recently added episodes',
        'description': 'Shows you TV Episodes recently added to your library.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'num_recent_episodes',
                'value': 3,
                'description': 'Number of episodes to display',
            },
            {
                'key': 'recently_added_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
            {
                'key': 'recently_added_watched_episodes',
                'value': '1',
                'description': 'Show Watched Episodes',
                'type': 'bool',
            },
            {
                'key': 'recently_added_info',
                'value': '0',
                'description': 'View information when selecting episode',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'recently_added_movies',
        'label': 'Recently added movies',
        'description': 'Shows you Movies recently added to your library.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'num_recent_movies',
                'value': 3,
                'description': 'Number of movies to display',
            },
            {
                'key': 'recently_added_movies_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
            {
                'key': 'recently_added_watched_movies',
                'value': '1',
                'description': 'Show Watched Movies',
                'type': 'bool',
            },
            {
                'key': 'recently_added_movies_info',
                'value': '0',
                'description': 'View information when selecting movie',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'recently_added_albums',
        'label': 'Recently added albums',
        'description': 'Shows you Albums recently added to your library.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'num_recent_albums',
                'value': 3,
                'description': 'Number of albums to display',
            },
            {
                'key': 'recently_added_albums_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
            {
                'key': 'recently_added_albums_info',
                'value': '0',
                'description': 'View information when selecting album',
                'type': 'bool',
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
                'key': 'sabnzbd_host',
                'value': '',
                'description': 'Hostname',
            },
            {
                'key': 'sabnzbd_port',
                'value': '',
                'description': 'Port',
            },
            {
                'key': 'sabnzbd_api',
                'value': '',
                'description': 'API Key',
            },
            {
                'key': 'sabnzbd_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
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
        'label': 'trakt.tv Shouts',
        'description': 'Shows you what people are saying about what you are watching and allows you to add your own comments.',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'trakt_api_key',
                'value': '',
                'description': 'Trakt API Key',
                'link': 'http://trakt.tv/settings/api',
            },
            {
                'key': 'trakt_username',
                'value': '',
                'description': 'Trakt Username',
            },
            {
                'key': 'trakt_password',
                'value': '',
                'description': 'Trakt Password',
            },
        ]
    },
    {
        'name': 'traktplus',
        'label': 'trakt.tv',
        'description': 'trakt.tv module',
        'static': False,
        'poll': 0,
        'delay': 10,
        'settings': [
            {
                'key': 'trakt_api_key',
                'value': '',
                'description': 'Trakt API Key',
                'link': 'http://trakt.tv/settings/api',
            },
            {
                'key': 'trakt_username',
                'value': '',
                'description': 'Trakt Username',
            },
            {
                'key': 'trakt_password',
                'value': '',
                'description': 'Trakt Password',
            },
        ]
    },
    {
        'name': 'transmission',
        'label': 'Transmission',
        'description': 'Shows you information about your Transmission downloads.',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
                {
                'key': 'transmission_ip',
                'value': '',
                'description': 'Transmission Hostname',
                },
                {
                'key': 'transmission_port',
                'value': '9091',
                'description': 'Transmission Port',
                },
                {
                'key': 'transmission_user',
                'value': '',
                'description': 'Transmission Username',
                },
                {
                'key': 'transmission_password',
                'value': '',
                'description': 'Transmission Password',
                },
        ]
    },
    {
        'name': 'utorrent',
        'label': 'uTorrent',
        'description': 'Shows information about uTorrent downloads',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
                {
                'key': 'utorrent_ip',
                'value': '',
                'description': 'uTorrent Hostname',
                },
                {
                'key': 'utorrent_port',
                'value': '8080',
                'description': 'uTorrent Port',
                },
                {
                'key': 'utorrent_user',
                'value': '',
                'description': 'uTorrent Username',
                },
                {
                'key': 'utorrent_password',
                'value': '',
                'description': 'uTorrent Password',
                },
        ]
    },
    {
        'name': 'sickbeard',
        'label': 'Sickbeard Manager',
        'description': 'Manage Sickbeard from within Maraschino',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'sickbeard_api',
                'value': '',
                'description': 'Sickbeard API Key',
            },
            {
                'key': 'sickbeard_user',
                'value': '',
                'description': 'Sickbeard Username',
            },
            {
                'key': 'sickbeard_password',
                'value': '',
                'description': 'Sickbeard Password',
            },
            {
                'key': 'sickbeard_ip',
                'value': '',
                'description': 'Sickbeard Hostname',
            },
            {
                'key': 'sickbeard_port',
                'value': '',
                'description': 'Sickbeard Port',
            },
            {
                'key': 'sickbeard_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
            {
                'key': 'sickbeard_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
            {
                'key': 'sickbeard_airdate',
                'value': '0',
                'description': 'Show air date',
                'type': 'bool',
            },         
        ]
    },
    {
        'name': 'weather',
        'label': 'Weather',
        'description': 'Weather details.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'weather_location',
                'value': '',
                'description': 'Location - can be a U.S. zip code or city name, state or city name, country',
            },
            {
                'key': 'weather_use_celcius',
                'value': '0',
                'description': 'Temperature in C',
                'type': 'bool',
            },
            {
                'key': 'weather_use_kilometers',
                'value': '0',
                'description': 'Wind Speed in Km',
                'type': 'bool',
            },
            {
                'key': 'weather_time',
                'value': '0',
                'description': '24 hour time',
                'type': 'bool',
            },
            {
                'key': 'weather_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
        ]
    },
]

MISC_SETTINGS = [
    {
        'key': 'fanart_backgrounds',
        'value': '0',
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
        'key': 'num_columns',
        'value': '3',
        'description': 'Number of columns',
        'type': 'select',
        'options': [
            {'value': '3', 'label': '3'},
            {'value': '4', 'label': '4'},
            {'value': '5', 'label': '5'},
        ]
    },
]

SERVER_SETTINGS = [
    {
        'key': 'maraschino_username',
        'value': '',
        'description': 'Maraschino username',
    },
    {
        'key': 'maraschino_password',
        'value': '',
        'description': 'Maraschino password',
    },
    {
        'key': 'maraschino_port',
        'value': '7000',
        'description': 'Maraschino port',
    },
    {
        'key': 'maraschino_webroot',
        'value': '',
        'description': 'Maraschino webroot',
    },
]

SEARCH_SETTINGS = [
    {
        'key': 'search',
        'value': '0',
        'description': 'Enable search feature',
        'type': 'bool',
    },
    {
        'key': 'nzb_matrix_API',
        'value': '',
        'description': 'NZBMatrix API',
        'link': 'http://nzbmatrix.com/account.php?action=api',
    },
    {
        'key': 'nzb_matrix_user',
        'value': '',
        'description': 'NZBMatrix Username',
    },
    {
        'key': 'nzb_su_API',
        'value': '',
        'description': 'nzb.su API',
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

            if s['name'] == 'maraschino_username':
                maraschino.AUTH['username'] = s['value'] if s['value'] != '' else None

            if s['name'] == 'maraschino_password':
                maraschino.AUTH['password'] = s['value'] if s['value'] != '' else None

    db_session.commit()

    # you can't cancel server settings - instead, return an updated template
    # with 'Settings saved' text on the button

    if name == 'server_settings':
        return extra_settings_dialog(dialog_type='server_settings', updated=True)

    # for everything else, return the rendered module

    return module_settings_cancel(name)

@app.route('/xhr/extra_settings_dialog/<dialog_type>')
@requires_auth
def extra_settings_dialog(dialog_type, updated=False):
    """
    Extra settings dialog (search settings, misc settings, etc).
    """

    dialog_text = None

    if dialog_type == 'search_settings':
        settings = copy.copy(SEARCH_SETTINGS)
        dialog_title = 'Search settings'
        dialog_text = 'N.B. With search enabled, you can press \'ALT-s\' to display the search module.'

    elif dialog_type == 'misc_settings':
        settings = copy.copy(MISC_SETTINGS)
        dialog_title = 'Misc. settings'

    elif dialog_type == 'server_settings':
        settings = copy.copy(SERVER_SETTINGS)
        dialog_title = 'Server settings'

    else:
        return jsonify({ 'status': 'error' })

    for s in settings:
         setting = get_setting(s['key'])

         if setting:
             s['value'] = setting.value

    return render_template('extra_settings_dialog.html',
        dialog_title = dialog_title,
        dialog_text = dialog_text,
        dialog_type = dialog_type,
        settings = settings,
        updated = updated,
    )

@app.route('/xhr/server_settings_dialog/', methods=['GET', 'POST'])
@app.route('/xhr/server_settings_dialog/<server_id>', methods=['GET', 'POST'])
@requires_auth
def server_settings_dialog(server_id=None):
    """
    Server settings dialog.
    If server_id exists then we're editing a server, otherwise we're adding one.
    """

    server = None

    if server_id:
        try:
            server = XbmcServer.query.get(server_id)

        except:
            logger.log('Error retrieving server details for server ID %s' % server_id , 'WARNING')

    # GET

    if request.method == 'GET':
        return render_template('server_settings_dialog.html',
            server = server,
        )

    # POST

    else:
        if not server:
            server = XbmcServer('', 1, '')

        label = request.form['label']
        if not label:
            label = 'XBMC server'

        try:
            server.label = label
            server.position = request.form['position']
            server.hostname = request.form['hostname']
            server.port = request.form['port']
            server.username = request.form['username']
            server.password = request.form['password']
            server.mac_address = request.form['mac_address']

            db_session.add(server)
            db_session.commit()

            active_server = get_setting('active_server')

            if not active_server:
                active_server = Setting('active_server', server.id)
                db_session.add(active_server)
                db_session.commit()

            return render_template('includes/servers.html',
                servers = XbmcServer.query.order_by(XbmcServer.position),
            )

        except:
            logger.log('Error saving XBMC server to database', 'WARNING')
            return jsonify({ 'status': 'error' })

    return jsonify({ 'status': 'error' })

@app.route('/xhr/delete_server/<server_id>', methods=['POST'])
@requires_auth
def delete_server(server_id=None):
    """
    Deletes a server.
    """

    try:
        xbmc_server = XbmcServer.query.get(server_id)
        db_session.delete(xbmc_server)
        db_session.commit()

        return render_template('includes/servers.html',
            servers = XbmcServer.query.order_by(XbmcServer.position),
        )

    except:
        logger.log('Error deleting server ID %s' % server_id , 'WARNING')
        return jsonify({ 'status': 'error' })

@app.route('/xhr/switch_server/<server_id>')
@requires_auth
def switch_server(server_id=None):
    """
    Switches XBMC servers.
    """

    xbmc_server = XbmcServer.query.get(server_id)

    try:
        active_server = get_setting('active_server')
        active_server.value = server_id
        db_session.add(active_server)
        db_session.commit()
        logger.log('Switched active server to ID %s' % server_id , 'INFO')

    except:
        logger.log('Error setting active server to ID %s' % server_id , 'WARNING')
        return jsonify({ 'status': 'error' })

    return jsonify({ 'status': 'success' })

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
