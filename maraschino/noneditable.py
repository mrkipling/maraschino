# -*- coding: utf-8 -*-
"""Util funtions for XBMC server settings."""

from maraschino.tools import using_auth, get_setting_value
from maraschino.models import Module, Setting, XbmcServer

def server_settings():
    """Get settings for active XBMC server instance"""

    # query all configured XBMC servers from the db
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
    """Convert username and password for active XBMC server to: username:password@"""
    username_password = ''
    server = server_settings()

    if server['username'] != None:
        username_password = server['username']
        if server['password'] != None:
            username_password += ':' + server['password']
        username_password += '@'

    return username_password

def server_address():
    """Get server address with username, password, hostname and port.
    The format is as following: http://username:password@hostname:port
    """
    server = server_settings()

    if not server['hostname'] and not server['port']:
        return None

    return 'http://%s%s:%s' % (server_username_password(), server['hostname'], server['port'])

def server_api_address():
    """Get address to json rpc api for active XBMC server"""
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
