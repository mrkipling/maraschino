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
sys.path.insert(0, os.path.join(path_base, 'external'))

try:
    from lib.database import *

except:
    print "You need to specify DATABASE in settings.py, and ensure that Flask-SQLAlchemy is installed."
    quit()

init_db()
print "Database successfully initialised."
