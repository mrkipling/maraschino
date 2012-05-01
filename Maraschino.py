import sys
import os

rundir = os.path.dirname(os.path.abspath(__file__))

try:
    frozen = sys.frozen

except AttributeError:
    frozen = False

# Define path based on frozen state

if frozen:
    path_base = os.environ['_MEIPASS2']
    rundir = os.path.dirname(sys.executable)

else:
    path_base = rundir

# Include paths

sys.path.insert(0, path_base)
sys.path.insert(0, os.path.join(path_base, 'lib'))

from flask import Flask, jsonify, render_template, request
from maraschino.database import db_session
import maraschino.logger as logger

try:
    import json
except ImportError:
    import simplejson as json
import hashlib, jsonrpclib, random, urllib, os, sys

app = Flask(__name__)

from settings import *

from maraschino.noneditable import *
from maraschino.tools import *
from maraschino.modules import *
from maraschino.models import Module, Setting

from modules.applications import *
from modules.controls import *
from modules.currently_playing import *
from modules.diskspace import *
from modules.library import *
from modules.log import *
from modules.recently_added import *
from modules.remote import *
from modules.sabnzbd import *
from modules.search import *
from modules.sickbeard import *
from modules.trakt import *
from modules.traktplus import *
from modules.transmission import *
from modules.utorrent import *
from modules.weather import *

@app.route('/')
@requires_auth
def index():
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

    return render_template('index.html',
        modules = modules,
        num_columns = num_columns,
        servers = servers,
        active_server = active_server,
        show_currently_playing = True,
        search_enabled = get_setting_value('search') == '1',
        background = background,
        fanart_backgrounds = fanart_backgrounds,
        applications = applications,
        library_show_power_buttons = library_show_power_buttons,
        show_tutorial = unorganised_modules.count() == 0,
    )

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

# check if database exists or create it

try:
    logger.log('Opening database at: %s' %(DATABASE), 'INFO')
    open(DATABASE)

except IOError, e:
    logger.log('Opening database failed', 'CRITICAL')
    try:
        logger.log('Checking if PATH exists: %s' %(DATABASE), 'WARNING')
        # check if path exists
        dbpath = os.path.dirname(DATABASE)
        if not os.path.exists(dbpath):
            try:
                logger.log('It does not exist, creating it...', 'WARNING')
                os.makedirs(dbpath)
            except:
                logger.log('Could not create %s, check settings.py.'% (DATABASE) , 'CRITICAL')
                print 'Could not create %s, check settings.py.'% (DATABASE)
                quit()

        # create db
        from maraschino.database import *

    except:
        logger.log('You need to specify a database in settings.py' , 'CRITICAL')
        print 'You need to specify a database in settings.py.'
        quit()

    logger.log('Database successfully initialised' , 'INFO')
    print "Database successfully initialised."

init_db()

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host='0.0.0.0')
