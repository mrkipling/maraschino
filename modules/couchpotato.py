from flask import Flask, jsonify, render_template, request, send_file
import json, jsonrpclib, urllib

from Maraschino import app
from settings import *
from maraschino.tools import *

def login_string():
    try:
        login = '%s:%s@' % (get_setting('couchpotato_user').value, get_setting('couchpotato_password').value)

    except:
        login = ''

    return login

def couchpotato_url():
    url = '%s:%s/%s' % (get_setting_value('couchpotato_ip'), get_setting_value('couchpotato_port'), get_setting_value('couchpotato_api'))

    if using_auth():
        return 'http://%s%s' % (login_string(), url)

    return 'http://%s' % (url)

def couchpotato_url_no_api():
    url = '%s:%s/' % (get_setting_value('couchpotato_ip'), get_setting_value('couchpotato_port'))

    if using_auth():
        return 'http://%s%s' % (login_string(), url)

    return 'http://%s' % (url)

@app.route('/xhr/couchpotato')
def xhr_couchpotato():
    try:
        url = '%s/movie.list/?status=active' % (couchpotato_url())
        result = urllib.urlopen(url).read()
        couchpotato = json.JSONDecoder().decode(result)

        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except:
        couchpotato = 'empty'

    compact_view = get_setting_value('couchpotato_compact') == '1'

    return render_template('couchpotato.html',
        url = couchpotato_url(),
        couchpotato = couchpotato,
        compact_view = compact_view,
    )