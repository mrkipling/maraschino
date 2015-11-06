#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the main executable of Maraschino. It parses the command line arguments, does init and calls the start function of Maraschino."""

import sys
import os


# Check if frozen by py2exe
def check_frozen():
    return hasattr(sys, 'frozen')


def get_rundir():
    if check_frozen():
        return os.path.abspath(unicode(sys.executable, sys.getfilesystemencoding( )))

    return os.path.abspath(__file__)[:-13]

# Set the rundir
rundir = get_rundir()

# Include paths
sys.path.insert(0, rundir)
sys.path.insert(0, os.path.join(rundir, 'lib'))

# Create Flask instance
from flask import Flask
app = Flask(__name__)

# If frozen, we need define static and template paths
if check_frozen():
    app.root_path = rundir
    app.static_path = '/static'
    app.add_url_rule(
        app.static_path + '/<path:filename>',
        endpoint='static',
        view_func=app.send_static_file
    )

    from jinja2 import FileSystemLoader
    app.jinja_loader = FileSystemLoader(os.path.join(rundir, 'templates'))


def import_modules():
    for mod in maraschino.MODULES:
        module = 'modules.{0}'.format(mod)
        try:
            __import__(module)
        except ImportError:
            pass
    """All modules that are available in Maraschino are at this point imported."""
    import mobile
    import xbmcmm


@app.teardown_request
def shutdown_session(exception=None):
    """This function is called as soon as a session is shutdown and makes sure, that the db session is also removed."""
    from maraschino.database import db_session
    db_session.remove()

import maraschino


def main():
    """Main function that is called at the startup of Maraschino."""
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
    p.add_option('--noupdate',
                 action="store_true",
                 dest='noupdate',
                 help='Disable the internal updater')

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
        DATABASE = os.path.join(data_dir, 'maraschino.db')

    if options.webroot:
        maraschino.WEBROOT = options.webroot

    if options.host:
        maraschino.HOST = options.host

    if options.kiosk:
        maraschino.KIOSK = True

    if options.noupdate:
        maraschino.UPDATER = False

    maraschino.RUNDIR = rundir
    maraschino.DATA_DIR = data_dir
    maraschino.FULL_PATH = os.path.join(rundir, 'Maraschino.py')
    maraschino.ARGS = sys.argv[1:]
    maraschino.PORT = PORT
    maraschino.DATABASE = DATABASE

    maraschino.initialize()

    if maraschino.PIDFILE or maraschino.DAEMON:
        maraschino.daemonize()

    import_modules()
    maraschino.init_updater()

    maraschino.start()


if __name__ == '__main__':
    main()
