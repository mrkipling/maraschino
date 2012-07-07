from flask import request, Response
from functools import wraps
from jinja2.filters import FILTERS
import os
import maraschino
from maraschino import app
from maraschino.models import Setting
from flask import send_file
import StringIO
import urllib

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
    if maraschino.AUTH['username'] != None and maraschino.AUTH['password'] != None:
        return True

    else:
        return False

def format_time(time):
    formatted_time = ''

    if time['hours'] > 0:
        formatted_time += str(time['hours']) + ':'

        if time['minutes'] == 0:
            formatted_time += '00:'

    formatted_time += '%0*d' % (2, time['minutes']) + ':'
    formatted_time += '%0*d' % (2, time['seconds'])

    return formatted_time

def format_number(num):
    extension_list = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']

    for i in range(len(extension_list)):
        base = 1024**i
        if num/base < 1024:
            return '%.2f' % (float(num)/base) + ' ' + extension_list[i]

    return str(num) + ' bytes'

def get_setting(key):
    try:
        return Setting.query.filter(Setting.key == key).first()

    except:
        return None

def get_setting_value(key, default=None):
    try:
        value = Setting.query.filter(Setting.key == key).first().value

        if value == '':
            return None

        return value

    except:
        return default

def get_file_list(folder, extensions, prepend_path=True):
    filelist = []

    for root, subFolders, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1] in extensions:
                if prepend_path:
                    filelist.append(os.path.join(root,file))
                else:
                    filelist.append(file)

    return filelist

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fTB' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fGB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fKB' % kilobytes
    else:
        size = '%.2fB' % bytes
    return size

FILTERS['convert_bytes'] = convert_bytes

def xbmc_image(url):
    if url.startswith('special://'): #eden
        return '%s/xhr/xbmc_image/eden/%s' % (maraschino.WEBROOT, url[len('special://'):])
    elif url.startswith('image://'): #frodo
        url = urllib.quote(url[len('image://'):].encode('utf-8'), '')
        return '%s/xhr/xbmc_image/frodo/%s' % (maraschino.WEBROOT, url)
    else:
        return url

FILTERS['xbmc_image'] = xbmc_image


def epochTime(seconds):
    import time
    return time.ctime(seconds)

FILTERS['time'] = epochTime


@app.route('/xhr/xbmc_image/<version>/<path:url>')
def xbmc_proxy(version, url):
    from maraschino.noneditable import server_address

    if version == 'eden':
        url = '%s/vfs/special://%s' % (server_address(), url)
    elif version == 'frodo':
        url = '%s/image/image://%s' % (server_address(), urllib.quote(url.encode('utf-8'), ''))

    img = StringIO.StringIO(urllib.urlopen(url).read())
    return send_file(img, mimetype='image/jpeg')
