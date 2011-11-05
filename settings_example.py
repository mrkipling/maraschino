MODULES = [
    [
        { 'module': 'applications', 'static': True },
        { 'module': 'library' },
    ],
    [
        { 'module': 'synopsis' },
        { 'module': 'trakt' },
    ],
    [
        { 'module': 'recently_added', 'poll': 350 },
        { 'module': 'sabnzbd', 'poll': 10 },
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

# required to enable shout posting for module 'trakt'
TRAKT_USERNAME = None
TRAKT_PASSWORD = None

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

# if you are using the dev server and want to run Maraschino on a different port
# then enable this setting

#PORT = 5000
