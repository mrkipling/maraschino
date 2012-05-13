from Maraschino import app, rundir
import sys, os, subprocess, wsgiserver
import logger as logger
from settings import *
from noneditable import requires_auth

d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', CHERRYPY_PORT), d)

def start():
    try:
        server.start()
        while not True:
            return
    except KeyboardInterrupt:
        server.stop()

@app.route('/shutdown')
@requires_auth
def stop():
    server.stop()
    logger.log('Shutting down Maraschino...', 'INFO')
    os._exit(0)

@app.route('/restart')
@requires_auth
def restart():
    server.stop()
    popen_list = [sys.executable, rundir + '/Maraschino.py']
    subprocess.Popen(popen_list)
    logger.log('Restarting Maraschino...', 'INFO')
    os._exit(0)
