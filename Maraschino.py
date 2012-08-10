#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the main executable of Maraschino. It parses the command line arguments, does init and calls the start function of Maraschino."""

import sys
import os

# Determine Maraschino run dir
rundir = os.path.dirname(os.path.abspath(__file__))

# Var sys.frozen is set by py2exe and is needed to define the rundir
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

# Create Flask instance
from flask import Flask
app = Flask(__name__)


def import_modules():
    """All modules that are available in Maraschino are at this point imported."""
    import modules.applications
    import modules.controls
    import modules.couchpotato
    import modules.currently_playing
    import modules.diskspace
    import modules.headphones
    import modules.index
    import modules.library
    import modules.log
    import modules.nzbget
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
    """This function is called as soon as a session is shutdown and makes sure, that the db session is also removed."""
    from maraschino.database import db_session
    db_session.remove()


def main():
    """Main function that is called at the startup of Maraschino."""
    import maraschino
    from optparse import OptionParser

    p = OptionParser()

    # define command line options
    p.add_option('-p', '--port',
                 dest='port',
                 default=None,
                 help="Force webinterface to listen on this port")
    p.add_option('-d', '--daemon',
                 dest='daemon',
                 action='store_true',
                 help='Run as a daemon')
    p.add_option('--pidfile',
                 dest='pidfile',
                 help='Create a pid file (only relevant when running as a daemon)')
    p.add_option('--log',
                 dest='log',
                 help='Create a log file at a desired location')
    p.add_option('-v', '--verbose',
                 dest='verbose',
                 action='store_true',
                 help='Silence the logger')
    p.add_option('--develop',
                 action="store_true",
                 dest='develop',
                 help="Start instance of development server")
    p.add_option('--database',
                 dest='database',
                 help='Custom database file location')
    p.add_option('--webroot',
                 dest='webroot',
                 help='Web root for Maraschino')
    p.add_option('--host',
                 dest='host',
                 help='Web host for Maraschino')
    p.add_option('--kiosk',
                 dest='kiosk',
                 action='store_true',
                 help='Disable settings in the UI')
    p.add_option('--datadir',
                 dest='datadir',
                 help='Write program data to custom location')

    # parse command line for defined options
    options, args = p.parse_args()

    if options.datadir:
        data_dir = options.datadir
    else:
        data_dir = rundir

    if options.daemon:
        maraschino.DAEMON = True
        maraschino.VERBOSE = False

    if options.pidfile:
        maraschino.PIDFILE = options.pidfile
        maraschino.VERBOSE = False

    # check if port argument is valid (integer between 0 and 65535)
    # since the logger is not yet initialized the error state is stored in this variable
    porterror = False
    # default port:
    PORT = 7000
    if options.port:
        try:
            PORT = int(options.port)
            if PORT < 0 or PORT > 65535:
                raise ValueError
        except ValueError:
            porterror = True

    if options.log:
        maraschino.LOG_FILE = options.log

    if options.verbose:
        maraschino.VERBOSE = True

    if options.develop:
        maraschino.DEVELOPMENT = True

    if options.database:
        DATABASE = options.database
    else:
        DATABASE = os.path.join(data_dir, 'maraschino.db')

    if options.webroot:
        maraschino.WEBROOT = options.webroot

    if options.host:
        maraschino.HOST = options.host

    if options.kiosk:
        maraschino.KIOSK = True

    maraschino.RUNDIR = rundir
    maraschino.DATA_DIR = data_dir
    maraschino.FULL_PATH = os.path.join(rundir, 'Maraschino.py')
    maraschino.ARGS = sys.argv[1:]
    maraschino.PORT = PORT
    maraschino.DATABASE = DATABASE

    maraschino.initialize()

    # check if defined port was valid. If not quit.
    if porterror:
        maraschino.logger.log('The specifed port is not valid. Please choose an integer between 0 and 65535.', 'CRITICAL')
        quit()

    import_modules()

    if maraschino.PIDFILE or maraschino.DAEMON:
        maraschino.daemonize()

    maraschino.start()


if __name__ == '__main__':
    main()
