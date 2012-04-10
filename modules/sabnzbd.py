try:
    import json
except ImportError:
    import simplejson as json

from flask import Flask, jsonify, render_template, request
import jsonrpclib, urllib
from jinja2.filters import FILTERS

from Maraschino import app
from settings import *
from maraschino.tools import *

def sabnzbd_url_no_api():
    url_base = get_setting_value('sabnzbd_host')
    port = get_setting_value('sabnzbd_port')

    if port:
        url_base = '%s:%s' % (url_base, port)

    return 'http://%s' % (url_base)

def sabnzbd_url(mode, extra = ""):
    return '%s/api?apikey=%s&mode=%s&output=json%s' % (sabnzbd_url_no_api(), get_setting_value('sabnzbd_api'), mode, extra)

def sab_link():
    SABNZBD_HOST = get_setting_value('sabnzbd_host')
    SABNZBD_PORT = get_setting_value('sabnzbd_port')
    SABNZBD_API = get_setting_value('sabnzbd_api')

    SABNZBD_URL = 'http://%s:%s' % (SABNZBD_HOST, SABNZBD_PORT)
    
    return '%s/api?apikey=%s' % (SABNZBD_URL, SABNZBD_API)
    
def add_to_sab_link(nzb):
    if get_setting_value('sabnzbd_api') != None:
        return '%s&mode=addurl&name=http://%s&output=json' % (sab_link(), nzb)
    return False

FILTERS['add_to_sab'] = add_to_sab_link

@app.route('/xhr/sabnzbd/')
@app.route('/xhr/sabnzbd/<queue_status>')
@requires_auth
def xhr_sabnzbd(queue_status = 'hide'):
    old_config = False

    if not get_setting_value('sabnzbd_host'):
        if get_setting_value('sabnzbd_url') != None:
            old_config = True
        
    downloading = None
    sabnzbd = None
    percentage_total = None
    download_speed = None
    downloading = None
    download_left = None

    try:
        result = urllib.urlopen(sabnzbd_url('queue')).read()
        sabnzbd = json.JSONDecoder().decode(result)
        sabnzbd = sabnzbd['queue']

        download_speed = format_number(int((sabnzbd['kbpersec'])[:-3])*1024) + '/s'

        if sabnzbd['slots']:
            percentage_total = int(100 - (float(sabnzbd['mbleft']) / float(sabnzbd['mb']) * 100))
            for item in sabnzbd['slots']:
                if item['status'] == 'Downloading':
                    downloading = item
                    break

        download_left = format_number(int(float(sabnzbd['mbleft'])*1024*1024))

    except:
        pass

    return render_template('sabnzbd-queue.html',
        sabnzbd = sabnzbd,
        percentage_total = percentage_total,
        download_speed = download_speed,
        download_left = download_left,
        old_config = old_config,
        first_downloading = downloading,
        queue_status = queue_status,
    )

@app.route('/xhr/sabnzbd/queue/<action>/')
@app.route('/xhr/sabnzbd/queue/pause/<time>')
@requires_auth
def sabnzb_queue(action = "pause", time = None):
    if not time:
        try:
            result = urllib.urlopen(sabnzbd_url(action)).read()
            sabnzbd = json.JSONDecoder().decode(result)
        except:
            pass
    else:
        try:
            result = urllib.urlopen(sabnzbd_url('config', '&name=set_pause&value='+time)).read()
            sabnzbd = json.JSONDecoder().decode(result)
        except:
            pass

    if sabnzbd:
        return jsonify ({'status': sabnzbd['status']})

    return jsonify ({'status': False})

@app.route('/xhr/sabnzbd/speedlimit/<int:speed>/')
@requires_auth
def sabnzb_speed_limit(speed):
    try:
        result = urllib.urlopen(sabnzbd_url('config', '&name=speedlimit&value=%i'%(speed))).read()
        sabnzbd = json.JSONDecoder().decode(result)
        if sabnzbd:
            return jsonify ({'status': sabnzbd['status']})
    except:
        pass

    return jsonify ({'status': False})

@app.route('/xhr/sabnzbd/individual/<state>/<id>/')
@requires_auth
def sabnzb_individual_toggle(state, id):
    try:
        result = urllib.urlopen(sabnzbd_url('queue', '&name=%s&value=%s'%(state, id))).read()
        sabnzbd = json.JSONDecoder().decode(result)
        if sabnzbd:
            return jsonify ({'status': sabnzbd['status']})
    except:
        pass

    return jsonify ({'status': False})

@app.route('/sabnzbd/add/', methods=['POST'])
def add_to_sab():
    try:
        url = request.form['url']
    except:
        return jsonify({ 'error': 'Did not receive URL variable'})
        
    try:
        return urllib.urlopen(url).read()
    except:
        return jsonify({ 'error': 'Failed to open URL: %s' %(url)})
