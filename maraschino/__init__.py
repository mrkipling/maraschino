import sys, os, subprocess, threading, wsgiserver
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
PORT = None
DATABASE = None
INIT_LOCK = threading.Lock()
__INITIALIZED__ = False
DEVELOPMENT = False
SCHEDULE = Scheduler()

AUTH = {
    'username': None,
    'password': None,
}

CURRENT_COMMIT = None
LATEST_COMMIT = None
COMMITS_BEHIND = 0
COMMITS_COMPARE_URL = ''

def initialize():

    with INIT_LOCK:

        global __INITIALIZED__, app, FULL_PATH, RUNDIR, ARGS, DAEMON, PIDFILE, VERBOSE, LOG_FILE, LOG_DIR, logger, PORT, SERVER, DATABASE, AUTH, \
                CURRENT_COMMIT, LATEST_COMMIT, COMMITS_BEHIND, COMMITS_COMPARE_URL, USE_GIT

        if __INITIALIZED__:
            return False

        # Set up logger
        if not LOG_FILE:
            LOG_FILE = os.path.join(RUNDIR, 'logs', 'maraschino.log')

        FILENAME = os.path.basename(LOG_FILE)
        LOG_DIR = LOG_FILE[:-len(FILENAME)]

        if not os.path.exists(LOG_DIR):
            try:
                os.makedirs(LOG_DIR)
            except OSError:
                if VERBOSE:
                    print 'Unable to create the log directory.'

        logger = maraschinoLogger(LOG_FILE, VERBOSE)

        # check if database exists or create it
        from database import init_db

        try:
            logger.log('Opening database at: %s' %(DATABASE), 'INFO')
            open(DATABASE)

        except IOError, e:
            logger.log('Opening database failed', 'CRITICAL')
            try:
                logger.log('Checking if PATH exists: %s' %(DATABASE), 'WARNING')
                dbpath = os.path.dirname(DATABASE)
                if not os.path.exists(dbpath):
                    try:
                        logger.log('It does not exist, creating it...', 'WARNING')
                        os.makedirs(dbpath)
                    except:
                        logger.log('Could not create %s.'% (DATABASE) , 'CRITICAL')
                        print 'Could not create %s.'% (DATABASE)
                        quit()

            except:
                logger.log('Could not create %s.' % (DATABASE) , 'CRITICAL')
                quit()

            logger.log('Database successfully initialised' , 'INFO')

        init_db()

        # Set up web server
        d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
        SERVER = wsgiserver.CherryPyWSGIServer(('0.0.0.0', PORT), d)

        # Set up AUTH
        from tools import get_setting_value
        username = get_setting_value('maraschino_username')
        password = get_setting_value('maraschino_password')

        if username and password != None:
            AUTH = {
                'username': username,
                'password': password
            }

        # Set up the updater
        from maraschino.updater import checkGithub, gitCurrentVersion

        if os.name == 'nt':
            USE_GIT = False
        else:
            USE_GIT = os.path.isdir(os.path.join(RUNDIR, '.git'))
            if USE_GIT:
                gitCurrentVersion()

        version_file = os.path.join(RUNDIR, 'Version.txt')
        if os.path.isfile(version_file):
            f = open(version_file, 'r')
            CURRENT_COMMIT = f.read()
            f.close()
        else:
            COMMITS_BEHIND = -1

        threading.Thread(target=checkGithub).start()


        __INITIALIZED__ = True
        return True

def start_schedules():
    from maraschino.updater import checkGithub
    SCHEDULE.add_interval_job(checkGithub, hours=6)
    SCHEDULE.start()

def start():
    if __INITIALIZED__:

        start_schedules()

        if not DEVELOPMENT:
            try:
                logger.log('Starting Maraschino on port: %i' % PORT, 'INFO')
                SERVER.start()
                while not True:
                    pass
            except KeyboardInterrupt:
                stop()
        else:
            logger.log('Starting Maraschino development server on port: %i' % PORT, 'INFO')
            app.run(debug=True, port=PORT, host='0.0.0.0')

def stop():
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
    SERVER.stop()
    popen_list = [sys.executable, FULL_PATH]
    popen_list += ARGS
    logger.log('Restarting Maraschino with: %s' % popen_list, 'INFO')
    SCHEDULE.shutdown(wait=False)
    subprocess.Popen(popen_list, cwd=RUNDIR)


def daemonize():
    if threading.activeCount() != 1:
        logger.log('There are %r active threads. Daemonizing may cause strange behavior.' % threading.enumerate(), 'WARNING')

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

    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            logger.log('Forking twice...', 'DEBUG')
            os._exit(0)
    except OSError, e:
        sys.exit('2nd fork failed: %s [%d]' % (e.strerror, e.errno))

    os.chdir('/')
    os.umask(0)
    pid = os.getpid()

    logger.log('Daemonized to PID: %s' % pid, 'INFO')
    if PIDFILE:
        logger.log('Writing PID %s to %s' % (pid, PIDFILE), 'INFO')
        file(PIDFILE, 'w').write("%s\n" % pid)
