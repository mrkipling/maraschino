# -*- coding: utf-8 -*-
"""Maraschino module"""

import sys
import os
import subprocess
import threading
import wsgiserver
import imp
import copy
from Maraschino import app
from Logger import maraschinoLogger
from apscheduler.scheduler import Scheduler

FULL_PATH = None
RUNDIR = None
ARGS = None
DAEMON = False
PIDFILE = None
VERBOSE = True
LOG_FILE = None
LOG_LIST = []
PORT = None
DATABASE = None
INIT_LOCK = threading.Lock()
__INITIALIZED__ = False
DEVELOPMENT = False
SCHEDULE = Scheduler()
WEBROOT = ''
logger = None
SERVER = None
HOST = '0.0.0.0'
KIOSK = False
DATA_DIR = None
SCRIPT_DIR = None
THREADS = []

AUTH = {
    'username': None,
    'password': None,
}

UPDATER = True
CURRENT_COMMIT = None
LATEST_COMMIT = None
COMMITS_BEHIND = 0
COMMITS_COMPARE_URL = ''
FIRST_RUN = 0
MODULES = []
MODULES_CONF = ''


def initialize():
    """Init function for this module"""
    with INIT_LOCK:

        global __INITIALIZED__, app, FULL_PATH, RUNDIR, ARGS, DAEMON, PIDFILE, VERBOSE, LOG_FILE, LOG_DIR, logger, PORT, SERVER, DATABASE, AUTH, \
                UPDATER, CURRENT_COMMIT, LATEST_COMMIT, COMMITS_BEHIND, COMMITS_COMPARE_URL, USE_GIT, WEBROOT, HOST, KIOSK, DATA_DIR, SCRIPT_DIR, \
                THREADS, FIRST_RUN, MODULES, MODULES_CONF

        if __INITIALIZED__:
            return False

        # Set up logger
        if not LOG_FILE:
            LOG_FILE = os.path.join(DATA_DIR, 'logs', 'maraschino.log')

        FILENAME = os.path.basename(LOG_FILE)
        LOG_DIR = LOG_FILE[:-len(FILENAME)]

        if not os.path.exists(LOG_DIR):
            try:
                os.makedirs(LOG_DIR)
            except OSError:
                if VERBOSE:
                    print 'Unable to create the log directory.'

        logger = maraschinoLogger(LOG_FILE, VERBOSE)

        #set up script dir
        if not SCRIPT_DIR:
            SCRIPT_DIR = os.path.join(DATA_DIR, 'scripts')
            if not os.path.exists(SCRIPT_DIR):
                os.makedirs(SCRIPT_DIR)

        # check if database exists or create it
        from database import init_db

        if KIOSK:
            logger.log('Running in KIOSK Mode, settings disabled.', 'INFO')

        try:
            logger.log('Opening database at: %s' % (DATABASE), 'INFO')
            open(DATABASE)
        except IOError:
            logger.log('Opening database failed', 'WARNING')

            #Check if a version file exists. If not assume latest revision.
            version_file = os.path.join(DATA_DIR, 'Version.txt')
            if not os.path.exists(version_file):
                FIRST_RUN = 1

            try:
                logger.log('Checking if PATH exists: %s' % (DATABASE), 'WARNING')
                dbpath = os.path.dirname(DATABASE)
                if not os.path.exists(dbpath):
                    try:
                        logger.log('It does not exist, creating it...', 'WARNING')
                        os.makedirs(dbpath)
                    except:
                        logger.log('Could not create %s.' % (DATABASE), 'CRITICAL')
                        print 'Could not create %s.' % (DATABASE)
                        quit()

            except:
                logger.log('Could not create %s.' % (DATABASE), 'CRITICAL')
                quit()

            logger.log('Database successfully initialised', 'INFO')

        init_db()

        # Web server settings
        from tools import get_setting_value

        if get_setting_value('maraschino_port'):
            port_arg = False
            for arg in ARGS:
                if arg == '--port' or arg == '-p':
                    port_arg = True
            if not port_arg:
                PORT = int(get_setting_value('maraschino_port'))

        # Set up AUTH
        username = get_setting_value('maraschino_username')
        password = get_setting_value('maraschino_password')

        if username and password != None:
            AUTH = {
                'username': username,
                'password': password
            }

        #Modular modules
        module_dir = os.path.join(DATA_DIR, 'modules')
        for path, dirs, files in os.walk(module_dir):
            for name in files:
                if name.endswith('.ini'):
                    MODULES.append(name.replace('.ini', ''))

        for mod in MODULES:
            ini_path = os.path.join(module_dir, "{0}.ini".format(mod))
            if os.path.getsize(ini_path) <= 0:
                pass
            else:
                conf_imp = imp.load_source(mod, ini_path)
                if isinstance(conf_imp.mod_conf, list):
                    try:
                        data
                    except NameError:
                        data = copy.deepcopy(conf_imp.mod_conf)
                    else:
                        data = copy.deepcopy(data) + copy.deepcopy(conf_imp.mod_conf)
                else:
                    pass
                conf_imp = ''
        MODULES_CONF = data

        # Set up web server
        if '--webroot' not in str(ARGS):
            WEBROOT = get_setting_value('maraschino_webroot')
            if WEBROOT is None or DEVELOPMENT:
                WEBROOT = ''

        if WEBROOT:
            if WEBROOT[0] != '/':
                WEBROOT = '/' + WEBROOT
            d = wsgiserver.WSGIPathInfoDispatcher({WEBROOT: app})
        else:
            d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
        SERVER = wsgiserver.CherryPyWSGIServer((HOST, PORT), d)

        __INITIALIZED__ = True
        return True


def init_updater():
    from maraschino.updater import checkGithub, gitCurrentVersion
    global USE_GIT, CURRENT_COMMIT, COMMITS_BEHIND

    if UPDATER:
        if os.name == 'nt':
            USE_GIT = False
        else:
            USE_GIT = os.path.isdir(os.path.join(RUNDIR, '.git'))
            if USE_GIT:
                gitCurrentVersion()

        version_file = os.path.join(DATA_DIR, 'Version.txt')
        if os.path.isfile(version_file):
            f = open(version_file, 'r')
            CURRENT_COMMIT = f.read()
            f.close()
        else:
            COMMITS_BEHIND = -1

        threading.Thread(target=checkGithub).start()


def start_schedules():
    """Add all periodic jobs to the scheduler"""
    if UPDATER:
        # check every 6 hours for a new version
        from maraschino.updater import checkGithub
        SCHEDULE.add_interval_job(checkGithub, hours=6)
    SCHEDULE.start()


def start():
    """Start the actual server"""
    if __INITIALIZED__:

        start_schedules()

        if not DEVELOPMENT:
            try:
                logger.log('Starting Maraschino on %s:%i%s' % (HOST, PORT, WEBROOT), 'INFO')
                SERVER.start()
                while not True:
                    pass
            except KeyboardInterrupt:
                stop()
        else:
            logger.log('Starting Maraschino development server on port: %i' % (PORT), 'INFO')
            logger.log(' ##### IMPORTANT : WEBROOT DOES NOT WORK UNDER THE DEV SERVER #######', 'INFO')
            app.run(debug=True, port=PORT, host=HOST)

def stop():
    """Shutdown Maraschino"""
    logger.log('Shutting down Maraschino...', 'INFO')

    if not DEVELOPMENT:
        SERVER.stop()
    else:
        from flask import request
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    SCHEDULE.shutdown(wait=False)

    if PIDFILE:
        logger.log('Removing pidfile: %s' % str(PIDFILE), 'INFO')
        os.remove(PIDFILE)


def restart():
    """Restart Maraschino"""
    SERVER.stop()
    popen_list = [sys.executable, FULL_PATH]
    popen_list += ARGS
    logger.log('Restarting Maraschino with: %s' % popen_list, 'INFO')
    SCHEDULE.shutdown(wait=False)
    subprocess.Popen(popen_list, cwd=RUNDIR)


def daemonize():
    """Start Maraschino as a daemon"""
    if threading.activeCount() != 1:
        logger.log('There are %s active threads. Daemonizing may cause strange behavior.' % threading.activeCount(), 'WARNING')

    sys.stdout.flush()
    sys.stderr.flush()

    try:
        pid = os.fork()
        if pid == 0:
            pass
        else:
            logger.log('Forking once...', 'DEBUG')
            os._exit(0)
    except OSError, e:
        sys.exit('1st fork failed: %s [%d]' % (e.strerror, e.errno))

    os.chdir('/')
    os.umask(0)
    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            logger.log('Forking twice...', 'DEBUG')
            os._exit(0)
    except OSError, e:
        sys.exit('2nd fork failed: %s [%d]' % (e.strerror, e.errno))

    pid = os.getpid()

    logger.log('Daemonized to PID: %s' % pid, 'INFO')
    if PIDFILE:
        logger.log('Writing PID %s to %s' % (pid, PIDFILE), 'INFO')
        file(PIDFILE, 'w').write("%s\n" % pid)


@app.context_processor
def utility_processor():
    def webroot_url(url=''):
        return WEBROOT + url
    return dict(webroot_url=webroot_url)
