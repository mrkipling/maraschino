from maraschino.tools import using_auth, get_setting_value
from maraschino.models import Module, Setting, XbmcServer

def server_settings():
    servers = XbmcServer.query.order_by(XbmcServer.position)

    if servers.count() == 0:
        return {
            'hostname': None,
            'port': None,
            'username': None,
            'password': None,
        }

    active_server = get_setting_value('active_server')

    # if active server is not defined, set it

    if not active_server:
        active_server = Setting('active_server', servers.first().id)
        db_session.add(active_server)
        db_session.commit()

    try:
        server = servers.get(active_server)

    except:
        logger.log('Could not retrieve active server, falling back on first entry' , 'WARNING')
        server = servers.first()

    return {
        'hostname': server.hostname,
        'port': server.port,
        'username': server.username,
        'password': server.password,
        'mac_address': server.mac_address,
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
