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

from cherrypy import wsgiserver
from Maraschino import app
from settings import *

d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', CHERRYPY_PORT), d)

if __name__ == '__main__':
   try:
      server.start()

   except KeyboardInterrupt:
      server.stop()
