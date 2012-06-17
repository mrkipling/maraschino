import sys, os

rundir = os.getcwd()

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

from flask import Flask
app = Flask(__name__)

def import_modules():
    import modules.applications
    import modules.controls
    import modules.currently_playing
    import modules.diskspace
    import modules.index
    import modules.library
    import modules.log
    import modules.recently_added
    import modules.remote
    import modules.sabnzbd
    import modules.search
    import modules.sickbeard
    import modules.trakt
    import modules.traktplus
    import modules.transmission
    import modules.updater
    import modules.utorrent
    import modules.weather
    import modules.xbmc_notify
    import mobile

@app.teardown_request
def shutdown_session(exception=None):
    from maraschino.database import db_session
    db_session.remove()

import maraschino

def main():
    from optparse import OptionParser
    p = OptionParser()

    p.add_option('-p', '--port',
                 dest = 'port', default = None,
                 help = "Force webinterface to listen on this port")
    p.add_option('-d', '--daemon',
                 dest = 'daemon',
                 action='store_true',
                 help='Run as a daemon')
    p.add_option('--pidfile',
                 dest = 'pidfile',
                 help='Create a pid file (only relevant when running as a daemon)')
    p.add_option('--log',
                 dest = 'log',
                 help='Create a log file at a desired location')
    p.add_option('-v', '--verbose',
                 dest = 'verbose',
                 action='store_true',
                 help='Silence the logger')
    p.add_option('--develop', action = "store_true",
                 dest = 'develop',
                 help="Start instance of development server")
    p.add_option('--database',
                 dest = 'database',
                 help='Custom database file location')
    p.add_option('--webroot',
                 dest = 'webroot',
                 help='web root for Maraschino')

    options, args = p.parse_args()

    if options.daemon:
        maraschino.DAEMON = True
        maraschino.VERBOSE = False

    if options.pidfile:
        maraschino.PIDFILE = options.pidfile
        maraschino.VERBOSE = False

    if options.port:
        PORT = int(options.port)
    else:
        PORT = 7000

    if options.log:
        maraschino.LOG_FILE = options.log

    if options.verbose:
        maraschino.VERBOSE = True

    if options.develop:
        maraschino.DEVELOPMENT = True

    if options.database:
        DATABASE = options.database
    else:
        DATABASE = os.path.join(rundir, 'maraschino.db')

    if options.webroot:
        maraschino.WEBROOT = options.webroot

    maraschino.RUNDIR = rundir
    maraschino.FULL_PATH = os.path.join(rundir, 'Maraschino.py')
    maraschino.ARGS = sys.argv[1:]
    maraschino.PORT = PORT
    maraschino.DATABASE = DATABASE

    maraschino.initialize()

    import_modules()

    if maraschino.PIDFILE or maraschino.DAEMON:
        maraschino.daemonize()

    maraschino.start()


if __name__ == '__main__':
    main()
