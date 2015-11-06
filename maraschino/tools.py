# -*- coding: utf-8 -*-
"""Util functions for different things. For example: format time or bytesize correct."""

from flask import request, Response
from functools import wraps
from jinja2.filters import FILTERS
import os
import maraschino
from maraschino import app, logger
from maraschino.models import Setting, XbmcServer
from flask import send_file
import StringIO
import urllib
import urllib2
import re

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == maraschino.AUTH['username'] and password == maraschino.AUTH['password']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if maraschino.AUTH['username'] != None and maraschino.AUTH['password'] != None:
            creds = maraschino.AUTH

        else:
            return f(*args, **kwargs)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        return f(*args, **kwargs)
    return decorated

def using_auth():
    """Check if authentication is necessary"""
    if maraschino.AUTH['username'] != None and maraschino.AUTH['password'] != None:
        return True

    else:
        return False

def format_time(time):
    """Format the time for the player info"""
    formatted_time = ''

    if time['hours'] > 0:
        formatted_time += str(time['hours']) + ':'

        if time['minutes'] == 0:
            formatted_time += '00:'

    formatted_time += '%0*d' % (2, time['minutes']) + ':'
    formatted_time += '%0*d' % (2, time['seconds'])

    return formatted_time

def format_seconds(time):
    hours = time / 3600
    minutes = time / 60
    seconds = time % 60
    if time < 3600:
        time = '%02d:%02d' % (minutes, seconds)
    else:
        time = '%02d:%02d:%02d' % (hours, minutes, seconds)

    return time

FILTERS['format_seconds'] = format_seconds

def round_number(num):
    if (num > 0):
        return int(num+.5)
    else:
        return int(num-.5)

FILTERS['round_number'] = round_number

def format_number(num, binary=True):
    if binary:
        extension_list = ['bytes', 'kiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
        number_base = 1024
    else:
        extension_list = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']
        number_base = 1000

    for i in range(len(extension_list)):
        base = number_base**i
        if num/base < number_base:
            return '%.2f' % (float(num)/base) + ' ' + extension_list[i]

    return str(num) + ' bytes'

def get_setting(key):
    """Get setting 'key' from db"""
    try:
        return Setting.query.filter(Setting.key == key).first()

    except:
        return None

def get_setting_value(key, default=None):
    """Get value for setting 'key' from db"""
    try:
        value = Setting.query.filter(Setting.key == key).first().value

        if value == '':
            return None

        #Strip http/https from hostnames
        if key.endswith('_host') or key.endswith('_ip'):
            if value.startswith('http://'):
                return value[7:]
            elif value.startswith('https://'):
                return value[8:]
        return value

    except:
        return default

def get_file_list(folder, extensions, prepend_path=True, prepend_path_minus_root=False):
    filelist = []

    for root, subFolders, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1] in extensions:
                if prepend_path:
                    filelist.append(os.path.join(root,file))
                elif prepend_path_minus_root:
                    full = os.path.join(root, file)
                    partial = full.replace(folder, '')
                    if partial.startswith('/'):
                        partial = partial.replace('/', '', 1)
                    elif partial.startswith('\\'):
                        partial = partial.replace('\\', '', 1)
                        
                    filelist.append(partial)
                else:
                    filelist.append(file)

    return filelist


def convert_bytes(bytes, with_extension=True):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2f' % terabytes
        extension = 'TB'
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2f' % gigabytes
        extension = 'GB'
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2f' % megabytes
        extension = 'MB'
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2f' % kilobytes
        extension = 'KB'
    else:
        size = '%.2f' % bytes
        extension = 'B'

    if with_extension:
        size = '%s%s' % (size, extension)
        return size

    return size, extension

FILTERS['convert_bytes'] = convert_bytes

def xbmc_image(url, label='default'):
    """Build xbmc image url"""
    if url.startswith('special://'): #eden
        return '%s/xhr/xbmc_image/%s/eden/?path=%s' % (maraschino.WEBROOT, label, url[len('special://'):])

    elif url.startswith('image://'): #frodo
        url = url[len('image://'):]
        url = urllib.quote(url.encode('utf-8'), '')

        return '%s/xhr/xbmc_image/%s/frodo/?path=%s' % (maraschino.WEBROOT, label, url)
    else:
        return url

FILTERS['xbmc_image'] = xbmc_image

def epochTime(seconds):
    """Convert the time expressed by 'seconds' since the epoch to string"""
    import time
    return time.ctime(seconds)

FILTERS['time'] = epochTime

@app.route('/xhr/xbmc_image/<label>/<version>/')
def xbmc_proxy(version, label):
    """Proxy XBMC image to make it accessible from external networks."""
    from maraschino.noneditable import server_address
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
        url = '%s/image/image://%s' % (xbmc_url, urllib.quote(url.encode('utf-8'), ''))

    img = StringIO.StringIO(urllib.urlopen(url).read())
    return send_file(img, mimetype='image/jpeg')


def youtube_to_xbmc(url):
    x = url.find('?v=') + 3
    id = url[x:]
    return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + id


def download_image(image, file_path):
    """Download image file"""
    try:
        logger.log('Creating file %s' % file_path, 'INFO')
        downloaded_image = file(file_path, 'wb')
    except:
        logger.log('Failed to create file %s' % file_path, 'ERROR')
        maraschino.THREADS.pop()

    try:
        logger.log('Downloading %s' % image, 'INFO')

        headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65 Safari/537.36' }
        request = urllib2.Request(image, None, headers)
        image_on_web = urllib2.urlopen(request, None)
        while True:
            buf = image_on_web.read(65536)
            if len(buf) == 0:
                break
            downloaded_image.write(buf)
        downloaded_image.close()
        image_on_web.close()
    except:
        logger.log('Failed to download %s' % image, 'ERROR')

    maraschino.THREADS.pop()

    return


@app.route('/cache/image_file/<type>/<path:file_path>/')
@app.route('/cache/image_url/<path:file_path>/')
@requires_auth
def file_img_cache(file_path, type=None):
    if not type:
        file_path = 'http://' + file_path
        file_path = StringIO.StringIO(urllib.urlopen(file_path).read())

    elif type == 'unix':
        file_path = '/' + file_path
    return send_file(file_path, mimetype='image/jpeg')


def create_dir(dir):
    if not os.path.exists(dir):
        try:
            logger.log('Creating dir %s' % dir, 'INFO')
            os.makedirs(dir)
        except Exception as e:
            logger.log('Problem creating dir %s' % dir, 'ERROR')
            logger.log(e, 'DEBUG')


def natural_sort(list, key=lambda s:s):
    """
    Sort a list into natural alphanumeric order.
    """
    def get_alphanum_key_func(key):
        convert = lambda text: int(text) if text.isdigit() else text
        return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]

    sort_key = get_alphanum_key_func(key)
    return list.sort(key=sort_key)
