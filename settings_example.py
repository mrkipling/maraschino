DATABASE = '/path/to/maraschino.db'

SHOW_CURRENTLY_PLAYING = True
FANART_BACKGROUNDS = False

SERVER = {
    'hostname': 'localhost',
    'port': '8080',
    'username': 'xbmc',
    'password': ''
}

APPLICATIONS = [
    {
        'name': 'XBMC',
        'url': 'http://server:port/',
        'description': 'Library view'
    },
    {
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
