MODULES = [
    'applications',
    'recently_added',
    'currently_playing',
    'sabnzbd'
]

SERVER = {
    'hostname': 'localhost',
    'port': '8080',
    'username': 'xbmc',
    'password': ''
}

SABNZBD_URL = 'http://server:port/api?apikey=b72734e6901ef6d69659759974440f21'

NUM_RECENT_EPISODES = 5

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
