from flask import Flask, jsonify, render_template, request
import hashlib, random, urllib
from maraschino.noneditable import *
from maraschino.modules import *
from maraschino.tools import requires_auth, get_setting_value
import maraschino
from maraschino import logger

@app.route('/')
@requires_auth
def index():
    from maraschino.models import Module, Setting, Application, XbmcServer
    from maraschino.database import db_session

    unorganised_modules = Module.query.order_by(Module.position)

    num_columns = get_setting_value('num_columns')

    try:
        num_columns = int(num_columns)

    except:
        logger.log('Could not retrieve number of columns settings. Defaulting to 3.' , 'WARNING')
        num_columns = 3

    modules = []

    for i in range(num_columns):
        modules.append([])

    for module in unorganised_modules:
        module_info = get_module_info(module.name)
        module.template = '%s.html' % (module.name)
        module.static = module_info['static']

        if module.column <= num_columns:
            modules[module.column - 1].append(module)

        else:
            modules[num_columns - 1].append(module) # if in a column out of range, place in last column

    applications = []

    try:
        applications = Application.query.order_by(Application.position)

    except:
        pass
    
    new_tab = get_setting_value('app_new_tab') == '1'

    # display random background when not watching media (if setting enabled)
    # only changes on page refresh

    background = None

    if get_setting_value('random_backgrounds') == '1':
        try:
            backgrounds = []
            custom_dir = 'static/images/backgrounds/custom/'

            if os.path.exists(os.path.dirname(custom_dir)):
                # use user-defined custom background
                backgrounds.extend(get_file_list(custom_dir, ['.jpg', '.png']))

                # if no images in directory, use default background that is set in stylesheet
                if len(backgrounds) == 0:
                    backgrounds = None

            else:
                # use backgrounds bundled with Maraschino
                backgrounds.extend(get_file_list('static/images/backgrounds/', ['.jpg', '.png']))

            # select random background
            background = backgrounds[random.randrange(0, len(backgrounds))]
            if maraschino.WEBROOT:
                background = maraschino.WEBROOT + '/' + background

        except:
            background = None

    # show fanart backgrounds when watching media
    fanart_backgrounds = get_setting_value('fanart_backgrounds') == '1'

    # get list of servers

    servers = XbmcServer.query.order_by(XbmcServer.position)

    if servers.count() == 0:
        # check if old server settings value is set
        old_server_hostname = get_setting_value('server_hostname')

        # create an XbmcServer entry using the legacy settings
        if old_server_hostname:
            xbmc_server = XbmcServer(
                'XBMC server 1',
                1,
                old_server_hostname,
                get_setting_value('server_port'),
                get_setting_value('server_username'),
                get_setting_value('server_password'),
                get_setting_value('server_macaddress'),
            )

            try:
                db_session.add(xbmc_server)
                db_session.commit()
                servers = XbmcServer.query.order_by(XbmcServer.position)

            except:
                logger.log('Could not create new XbmcServer based on legacy settings' , 'WARNING')

    active_server = get_setting_value('active_server')

    if active_server:
        active_server = int(active_server)

    # show power buttons in library?
    library_show_power_buttons = get_setting_value('library_show_power_buttons', '1') == '1'

    # show currently playing bar?
    if get_setting_value('show_currently_playing') == None:
        show_currently_playing = True
    else:
        show_currently_playing = get_setting_value('show_currently_playing') == '1'

    return render_template('index.html',
        modules = modules,
        num_columns = num_columns,
        servers = servers,
        active_server = active_server,
        show_currently_playing=show_currently_playing,
        search_enabled = get_setting_value('search') == '1',
        background = background,
        fanart_backgrounds = fanart_backgrounds,
        applications = applications,
        library_show_power_buttons = library_show_power_buttons,
        show_music=get_setting_value('library_show_music') == '1',
        show_files=get_setting_value('library_show_files') == '1',
        show_tutorial = unorganised_modules.count() == 0,
        webroot = maraschino.WEBROOT,
        kiosk = maraschino.KIOSK,
        new_tab = new_tab,
        title_color=get_setting_value('title_color')
    )

@app.route('/xhr/shutdown')
@requires_auth
def maraschino_shutdown():
    maraschino.stop()
    return jsonify(shutdown_complete=True)

@app.route('/xhr/restart')
@requires_auth
def xhr_restart():
    maraschino.restart()
    return jsonify(restart_complete=True)

@app.route('/shutdown')
@requires_auth
def shutdown_url():
    return render_template('power.html', shutdown=True)

@app.route('/restart')
@requires_auth
def restart_url():
    return render_template('power.html', restart=True)
