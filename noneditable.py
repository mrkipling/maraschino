from settings import *
from tools import *

from models import Module, Setting

def server_settings():
    return {
        'hostname': get_setting_value('server_hostname'),
        'port': get_setting_value('server_port'),
        'username': get_setting_value('server_username'),
        'password': get_setting_value('server_password'),
    }

def server_username_password():
    username_password = ''
    server = server_settings()

    if server['username'] != None:
        username_password = server['username']
        if server['password'] != None:
            username_password += ':' + server['password']
        username_password += '@'

    return username_password

def server_address():
    server = server_settings()

    if not server['hostname'] and not server['port']:
        return None

    return 'http://%s%s:%s' % (server_username_password(), server['hostname'], server['port'])

def server_api_address():
    address = server_address()

    if not address:
        return None

    return '%s/jsonrpc' % (address)

def safe_server_address():
    if using_auth():
        return server_address()

    server = server_settings()

    if not server['hostname'] and not server['port']:
        return None

    return 'http://%s:%s' % (server['hostname'], server['port'])

try:
    if PORT:
        pass

except:
    PORT = 5000
