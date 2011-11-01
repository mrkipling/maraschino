from settings import *
from tools import *

# construct a username/password, server address and API address

SERVER['username_password'] = ''
if SERVER['username'] != None:
    SERVER['username_password'] = SERVER['username']
    if SERVER['password'] != None:
        SERVER['username_password'] += ':' + SERVER['password']
    SERVER['username_password'] += '@'

SERVER_ADDRESS = 'http://%s%s:%s' % (SERVER['username_password'], SERVER['hostname'], SERVER['port'])
SERVER_API_ADDRESS = '%s/jsonrpc' % (SERVER_ADDRESS)

SAFE_SERVER_ADDRESS = 'http://%s:%s' % (SERVER['hostname'], SERVER['port'])

if using_auth():
    SAFE_SERVER_ADDRESS = SERVER_ADDRESS

# modules that HAVE to be static
# e.g. synopsis as it is linked to currently playing data

MANDATORY_STATIC_MODULES = ['synopsis', 'trakt', 'library']

for column in MODULES:
    for module in column:

        # static modules need a template
        module['template'] = '%s.html' % (module['module'])

        if module['module'] in MANDATORY_STATIC_MODULES:
            module['static'] = True
