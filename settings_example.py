MODULES = [
    [
        { 'module': 'applications', 'static': True },
        { 'module': 'sabnzbd', 'poll': 5 },
    ],
    [
        { 'module': 'synopsis' },
        { 'module': 'trakt', 'poll': 60, 'delay': 5 },
    ],
    [
        { 'module': 'recently_added', 'poll': 350 },
    ],
]

SHOW_CURRENTLY_PLAYING = True
FANART_BACKGROUNDS = False

SERVER = {
    'hostname': 'localhost',
    'port': '8080',
    'username': 'xbmc',
    'password': ''
}

# required for module 'sabnzbd'
SABNZBD_URL = 'http://server:port/api?apikey=b72734e6901ef6d69659759974440f21'

# required for module 'trakt'
TRAKT_API_KEY = None

# required for module 'recently_added'
NUM_RECENT_EPISODES = 5

# required for module 'applications'
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
