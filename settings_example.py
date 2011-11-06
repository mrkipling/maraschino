DATABASE = '/path/to/maraschino.db'

APPLICATIONS = [
    {
        'image':'/static/images/programs/XBMC.png',
        'name': 'XBMC',
        'url': 'http://server:port/',
        'description': 'Library view'
    },
    {
        'image':'/static/images/programs/SabNZBd.png',
        'name': 'SABnzbd+',
        'url': 'http://server:port/',
        'description': 'Usenet binary client'
    },
]

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
