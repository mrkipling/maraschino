# this is where you database is going to be stored
# make sure that you have write access to the directory

DATABASE = '/path/to/maraschino.db'

# if serving using CherryPy (maraschino-cherrypy.py)
# you can set the port here

CHERRYPY_PORT = 7000

# include AUTH if you want to use HTTP basic authentication
# if serving using Apache and mod_wsgi, make sure to enable auth forwarding:
# http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIPassAuthorization

#AUTH = {
#    'username': 'username',
#    'password': 'password'
#}

# if you are using the dev server and want to run Maraschino on a different port
# then enable this setting

#PORT = 5000
