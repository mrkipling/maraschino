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
    #path_base = os.path.dirname(sys.executable)
else:
    path_base = rundir

# Include paths
sys.path.insert(0, path_base)
sys.path.insert(0, os.path.join(path_base, 'plugins'))
sys.path.insert(0, os.path.join(path_base, 'external'))

from flask import Flask, jsonify, render_template, request
from lib.database import db_session
import hashlib, json, jsonrpclib, random, urllib

app = Flask(__name__)

from settings import *
from lib.noneditable import *
from lib.tools import *

from plugins.applications import *
from plugins.controls import *
from plugins.currently_playing import *
from plugins.diskspace import *
from plugins.library import *
from plugins.recently_added import *
from plugins.recommendations import *
from plugins.sabnzbd import *
from plugins.sickbeard import *
from plugins.trakt import *
from plugins.transmission import *

from lib.modules import *
from lib.models import Module, Setting

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
            backgrounds.extend(get_file_list('static/images/backgrounds', ['.jpg', '.png']))
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

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host='0.0.0.0')
