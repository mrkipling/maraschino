from flask import render_template, request
import json
import urllib

from Maraschino import app
from maraschino.tools import *


def login_string():
    try:
        login = '%s:%s@' % (get_setting_value('couchpotato_user'), get_setting_value('couchpotato_password'))

    except:
        login = ''

    return login


def couchpotato_url():
    return 'http://%s%s:%s/api/%s' % (login_string(), get_setting_value('couchpotato_ip'), get_setting_value('couchpotato_port'), get_setting_value('couchpotato_api'))


def couchpotato_url_no_api():
    return 'http://%s%s:%s/' % (login_string(), get_setting_value('couchpotato_ip'), get_setting_value('couchpotato_port'))


@app.route('/xhr/couchpotato')
def xhr_couchpotato():
    try:
        print couchpotato_url()
        url = '%s/movie.list/' % (couchpotato_url())
        result = urllib.urlopen(url).read()
        couchpotato = json.JSONDecoder().decode(result)

        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except:
        couchpotato = 'empty'

    compact_view = get_setting_value('couchpotato_compact') == '1'

    return render_template('couchpotato.html',
        url=couchpotato_url(),
        couchpotato=couchpotato,
        compact_view=compact_view,
    )


@app.route('/couchpotato/search/')
def cp_search():
    couchpotato = {}
    params = ''

    try:
        params = request.args['name']
    except:
        pass

    if params is not '':
        try:
            url = '%s/movie.search/?q=%s' % (couchpotato_url(), params)
            result = urllib.urlopen(url).read()
            couchpotato = json.JSONDecoder().decode(result)

        except:
            couchpotato = None

    else:
        couchpotato = None

    return render_template('couchpotato-search.html',
        data=couchpotato,
        couchpotato='results',
    )
