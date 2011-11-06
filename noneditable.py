from settings import *
from tools import *

from models import Module, Setting

def server_settings():
    return {
        'hostname': get_setting('server_hostname').value,
        'port': get_setting('server_port').value,
        'username': get_setting('server_username').value,
        'password': get_setting('server_password').value,
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
    return 'http://%s%s:%s' % (server_username_password(), server['hostname'], server['port'])

def server_api_address():
    return '%s/jsonrpc' % (server_address())

def safe_server_address():
    if using_auth():
        return server_address()

    server = server_settings()
    return 'http://%s:%s' % (server['hostname'], server['port'])

try:
    if PORT:
        pass

except:
    PORT = 5000
