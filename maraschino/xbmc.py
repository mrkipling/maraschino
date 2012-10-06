# -*- coding: utf-8 -*-
"""XBMC tools and handlers"""

from flask import json, send_file, request
from maraschino.tools import get_setting_value
from maraschino.models import Setting, XbmcServer
from maraschino.database import db_session
from maraschino import app, logger, WEBROOT
from jinja2.filters import FILTERS
import urllib2, base64, StringIO


def server_settings():
    """Get settings for active XBMC server instance"""

    # Query all configured XBMC servers from the db
    servers = XbmcServer.query.order_by(XbmcServer.position)

    if servers.count() == 0:
        return {
            'hostname': None,
            'port': None,
            'username': None,
            'password': None,
            'label': None
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
        'label': server.label
    }


def server_username_password():
    """Convert username and password for active XBMC server to: username:password@"""
    username_password = ''
    server = server_settings()

    if server['username'] and server['password']:
        username_password = '%s:%s@' % (server['username'], server['password'])

    return username_password

def server_address():
    """
    Get server address with username, password, hostname and port.
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


def legacy_xbmc_check():
    """
    Legacy XBMC server check
    """
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
            except:
                logger.log('Could not create new XbmcServer based on legacy settings' , 'WARNING')

    return


def xbmc_image(url, label='default'):
    """Build xbmc image url"""
    if url.startswith('special://'): #eden
        return '%s/xhr/xbmc_image/%s/eden/?path=%s' % (WEBROOT, label, url[10:])

    elif url.startswith('image://'): #frodo
        url = url[8:]
        url = urllib2.quote(url.encode('utf-8'), '')

        return '%s/xhr/xbmc_image/%s/frodo/?path=%s' % (WEBROOT, label, url)
    else:
        return url

FILTERS['xbmc_image'] = xbmc_image

@app.route('/xhr/xbmc_image/<label>/<version>/')
def xbmc_proxy(version, label):
    """Proxy XBMC image to make it accessible from external networks."""

    url = request.args['path']

    if label != 'default': #check for XBMC server other than default
        server = XbmcServer.query.filter(XbmcServer.label == label).first()
        xbmc_url = 'http://'

        if server.username and server.password:
            xbmc_url += '%s:%s@' % (server.username, server.password)

        xbmc_url += '%s:%s' % (server.hostname, server.port)

    else:
        xbmc_url = server_address()

    if version == 'eden':
        url = '%s/vfs/special://%s' % (xbmc_url, url)
    elif version == 'frodo':
        url = '%s/image/image://%s' % (xbmc_url, urllib2.quote(url.encode('utf-8'), ''))

    img = StringIO.StringIO(urllib2.urlopen(url).read())
    return send_file(img, mimetype='image/jpeg')


def youtube_to_xbmc(url):
    """Convert youtube url to XBMC youtube plugin url"""
    x = url.find('?v=') + 3
    id = url[x:]
    return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + id


def lst2str(details, ignore=[]):
    """Convert list items into string.
       Format is: a / b / c
    """
    lists = ['genre', 'director', 'studio', 'writer', 'tag', 'style', 'mood', 'yearsactive', 'artist', 'theme']

    for i in details:
        if i in lists and i not in ignore:
            a = ''
            for b in details[i]:
                if b != '':
                    a += b + ' / '
            if a:
                details[i] = a[:-3]
            else:
                details[i] = a
    return details
