MODULES = [
    [
        { 'module': 'applications', 'poll': None },
    ],
    [
        { 'module': 'sabnzbd', 'poll': 5 },
    ],
    [
        { 'module': 'recently_added', 'poll': 350 },
    ],
]

SHOW_CURRENTLY_PLAYING = True

SERVER = {
    'hostname': 'localhost',
    'port': '8080',
    'username': 'xbmc',
    'password': ''
}

# required for module 'sabnzbd'
SABNZBD_URL = 'http://server:port/api?apikey=b72734e6901ef6d69659759974440f21'

# both required for module 'trakt'
TRAKT_API_KEY = None
TRAKT_USERNAME = None

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
