from flask import request, Response
from functools import wraps
from settings import *
import os

from database import *
from models import Setting

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == AUTH['username'] and password == AUTH['password']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            creds = AUTH

        except:
            return f(*args, **kwargs)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        return f(*args, **kwargs)
    return decorated

def using_auth():
    try:
        if AUTH:
            return True
    except:
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

def get_setting(key):
    try:
        return Setting.query.filter(Setting.key == key).first()

    except:
        return None

def get_setting_value(key):
    try:
        value = Setting.query.filter(Setting.key == key).first().value

        if value == '':
            return None

        return value

    except:
        return None

def get_file_list(dir, extensions, prepend_path=True):
    filelist = []

    for root, subFolders, files in os.walk(dir):
        for file in files:
            if os.path.splitext(file)[1] in extensions:
                if prepend_path:
                    filelist.append(os.path.join(root,file))
                else:
                    filelist.append(file)

    return filelist
