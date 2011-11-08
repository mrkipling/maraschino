try:
    from database import *

except:
    print "You need to specify DATABASE in settings.py, and ensure that Flask-SQLAlchemy is installed."
    quit()

init_db()
print "Database successfully initialised."
