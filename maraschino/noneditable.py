from settings import *
from maraschino.tools import *

from maraschino.models import Module, Setting, XbmcServer

def server_settings():
    servers = XbmcServer.query.order_by(XbmcServer.position)

    if servers.count() == 0:
        # check if old server settings value is set
        old_server_hostname = get_setting_value('server_hostname')

        # create an XbmcServer entry using the legacy settings
        if old_server_hostname:
            xbmc_server = XbmcServer(
                'XBMC server 1',
                1,
                old_server_hostname,
                get_setting_value('server_port'),
                get_setting_value('server_username'),
                get_setting_value('server_password'),
                get_setting_value('server_macaddress'),
            )

            try:
                db_session.add(xbmc_server)
                db_session.commit()
                servers = XbmcServer.query.order_by(XbmcServer.position)

            except:
                logger.log('Could not create new XbmcServer based on legacy settings' , 'WARNING')

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
