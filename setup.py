try:
    from database import *

except:
    print "You need to specify DATABASE in settings.py"
    quit()

init_db()
print "Database successfully initialised."
