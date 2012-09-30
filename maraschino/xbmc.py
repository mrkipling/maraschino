# -*- coding: utf-8 -*-
"""XBMC tools and handlers"""

from flask import json, send_file, request
from maraschino.tools import get_setting_value
from maraschino.models import Module, Setting, XbmcServer
from maraschino.database import db_session
from maraschino import app, logger
from jinja2.filters import FILTERS
import maraschino, urllib2, base64, StringIO


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

    if server['username']:
        username_password = server['username']
        if server['password']:
            username_password += ':' + server['password']
        username_password += '@'

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


def init_xbmc_server():
    """
    Check if there are any XBMC servers defined and
    initialize the active server if there is 1 defined.
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
                servers = XbmcServer.query.order_by(XbmcServer.position)

            except:
                logger.log('Could not create new XbmcServer based on legacy settings' , 'WARNING')

    if servers.count():
        set_xbmc_server()


def set_xbmc_server():
    """Set up connection to active XBMC server"""
    server = server_settings()
    maraschino.XBMC_VERSION = 0

    if server['hostname'] and server['port']:
        api_address = 'http://%s:%s/jsonrpc' % (server['hostname'], server['port'])
        maraschino.XBMC = XBMCJSON(api_address, server['username'], server['password'])

    else:
        logger.log('XBMC hostname and port are not defined', 'WARNING')
        maraschino.XBMC = XBMCJSON('', '', '')


def xbmc_image(url, label='default'):
    """Build xbmc image url"""
    if url.startswith('special://'): #eden
        return '%s/xhr/xbmc_image/%s/eden/?path=%s' % (maraschino.WEBROOT, label, url[len('special://'):])

    elif url.startswith('image://'): #frodo
        url = url[len('image://'):]
        url = urllib2.quote(url.encode('utf-8'), '')

        return '%s/xhr/xbmc_image/%s/frodo/?path=%s' % (maraschino.WEBROOT, label, url)
    else:
        return url

FILTERS['xbmc_image'] = xbmc_image

@app.route('/xhr/xbmc_image/<label>/<version>/')
def xbmc_proxy(version, label):
    """Proxy XBMC image to make it accessible from external networks."""

    url = request.args['path']

    if label != 'default':
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
    """Convert list items into string. Format is: a / b / c"""
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


class XBMCJSON:

    def __init__(self, server, username, password):
        """Initialize the XBMC server"""
        self.server = server
        self.username = username
        self.password = password

    def __call__(self, **kwargs):
        """Gets method and params from call"""
        method = '.'.join(map(str, self.n))
        self.n = []
        return XBMCJSON.__dict__['Request'](self, method, kwargs)
 
    def __getattr__(self, name):
        if not self.__dict__.has_key('n'):
            self.n=[]
        self.n.append(name)
        return self

    def Request(self, method, kwargs):
        """Process the XBMC request"""
        dev = False
        silent = False

        # Add dev=True to the request to print method, params and response
        if 'dev' in kwargs:
            dev = kwargs['dev']
            del kwargs['dev']

        # Add silent=True to server errors
        # Currently playing module needs this to stop it from spamming the logs
        if 'silent' in kwargs:
            silent = kwargs['silent']
            del kwargs['silent']

        if not self.server and not silent:
            logger.log('XBMC :: No XBMC server defined', 'ERROR')
            return 'No XBMC server defined'

        if dev:
            print 'METHOD: %s\nPARAMS:\n%s' % (method, json.dumps(kwargs, indent=4))

        # JSON data to be sent to XBMC
        data = [
            {
                'method': method,
                'params': kwargs,
                'jsonrpc': '2.0',
                'id': 0
            }
        ]

        # If XBMC version is unknown, add it to the request
        if not maraschino.XBMC_VERSION:
            data.append(
                {
                    'method': 'Application.GetProperties',
                    'params': {'properties': ['version']},
                    'jsonrpc': '2.0',
                    'id': 1
                }
            )

        data = json.JSONEncoder().encode(data)

        # Set content
        content = {
            'Content-Type': 'application/json',
            'Content-Length': len(data),
        }

        request = urllib2.Request(self.server, data, content)

        # If XBMC server requires username and password add auth header
        if self.username and self.password:
            base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

        # Send the request
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.URLError, e:
            if not silent:
                logger.log('XBMC :: %s' % e.reason, 'ERROR')

            # Reset XBMC version to unknown when we lose connection
            maraschino.XBMC_VERSION = 0

        response = json.JSONDecoder().decode(response)

        # If version request was included, save it to cache
        if len(response) > 1:
            if 'result' in response[1] and 'version' in response[1]['result']:
                maraschino.XBMC_VERSION = response[1]['result']['version']['major']

        if dev:
            print 'RESPONSE:\n%s' % json.dumps(response, indent=4)

        try:
            # Return the response result
            return response[0]['result']
        except:
            # If there is a error, log the error message
            logger.log('XBMC :: %s' % response[0]['error']['message'], 'ERROR')
            return response[0]['error']['message']


