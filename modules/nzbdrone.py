from flask import render_template, json, jsonify
import urllib2

from maraschino import app
from maraschino.tools import *
import datetime as DT


def nzbdrone_http():
    if get_setting_value('nzbdrone_https') == '1':
        return 'https://'
    else:
        return 'http://'


def nzbdrone_url():
    port = get_setting_value('nzbdrone_port')
    url_base = get_setting_value('nzbdrone_ip')
    webroot = get_setting_value('nzbdrone_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    url = '%s/api/' % (url_base)

    return nzbdrone_http() + url


def nzbdrone_url_no_api():
    port = get_setting_value('nzbdrone_port')
    url_base = get_setting_value('nzbdrone_ip')
    webroot = get_setting_value('nzbdrone_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    return nzbdrone_http() + url_base


def nzbdrone_api(params=None, use_json=True, dev=False, post=False, data=None):
    url = nzbdrone_url() + params
    if post:
        if dev:
            print jsonify(data)
        r = urllib2.Request(url, jsonify(data))
        r.add_header('Content-Type', 'application/json')
    else:
        r = urllib2.Request(url)
    r.add_header("X-Api-Key ", get_setting_value('nzbdrone_api'))

    data = urllib2.urlopen(r).read()
    if dev:
        print url
        print data
    if use_json:
        data = json.JSONDecoder().decode(data)
    return data


def nzbdrone_root():
    return nzbdrone_api('Rootfolder')


def nzbdrone_qualities():
    return nzbdrone_api('QualityProfile')


@app.route('/xhr/nzbdrone/')
def xhr_nzbdrone():
    params = 'Calendar?end=%s' %(DT.date.today() + DT.timedelta(days=7))

    try:
        nzbdrone = nzbdrone_api(params)

    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone.html',
        nzbdrone=nzbdrone,
    )


@app.route('/xhr/nzbdrone/series/')
def series():
    params = 'Series'

    try:
        nzbdrone = nzbdrone_api(params)
    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone/series.html',
        nzbdrone=nzbdrone,
    )


@app.route('/xhr/nzbdrone/history/')
def nzbdrone_history():
    params = 'History?page=1&pageSize=50&sortKey=date&sortDir=desc'

    try:
        nzbdrone = nzbdrone_api(params)
    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone/history.html',
        nzbdrone=nzbdrone['records'],
    )


@app.route('/xhr/nzbdrone/search/<query>/')
@requires_auth
def nzbdrone_search(query):
    params = 'Series/lookup?term=%s' % (urllib2.quote(query))
    try:
        nzbdrone = nzbdrone_api(params)
        root = nzbdrone_root()
        qualities = nzbdrone_qualities()
    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone/results.html',
        nzbdrone=nzbdrone,
        root=root,
        qualities=qualities,
    )


@app.route('/xhr/nzbdrone/add/', methods=['POST'])
@requires_auth
def nzbdrone_add():
    params = 'Series'
    nzbdrone = nzbdrone_api(params, post=True, data=request.form, dev=True)
    return nzbdrone
    return render_template('nzbdrone/results.html',
        nzbdrone=nzbdrone,
    )
