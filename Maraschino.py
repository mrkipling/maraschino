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
from modules.recently_added import *
from modules.recommendations import *
from modules.remote import *
from modules.sabnzbd import *
from modules.sickbeard import *
from modules.trakt import *
from modules.transmission import *
from modules.weather import *

@app.route('/')
@requires_auth
def index():
    unorganised_modules = Module.query.order_by(Module.position)
    modules = [[],[],[]]

    for module in unorganised_modules:
        module_info = get_module_info(module.name)
        module.template = '%s.html' % (module.name)
        module.static = module_info['static']
        modules[module.column - 1].append(module)

    applications = []

    try:
        applications = Application.query.order_by(Application.position)

    except:
        pass

    # select random background when not watching media

    background = None

    if get_setting_value('random_backgrounds') == '1':
        try:
            backgrounds = []
            backgrounds.extend(get_file_list('static/images/backgrounds/', ['.jpg', '.png']))
            background = backgrounds[random.randrange(0, len(backgrounds))]

        except:
            background = None

    # show fanart backgrounds when watching media
    fanart_backgrounds = get_setting_value('fanart_backgrounds') == '1'

    return render_template('index.html',
        modules = modules,
        show_currently_playing = True,
        background = background,
        fanart_backgrounds = fanart_backgrounds,
        applications = applications,
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

    init_db()
    logger.log('Database successfully initialised' , 'INFO')
    print "Database successfully initialised."

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host='0.0.0.0')
