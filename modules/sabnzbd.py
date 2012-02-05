from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from Maraschino import app
from settings import *
from maraschino.tools import *

def sabnzbd_url_no_api():
    return 'http://%s:%s' % (get_setting_value('sabnzbd_host'), get_setting_value('sabnzbd_port'))

def sabnzbd_url(mode, extra = ""):
    return '%s/api?apikey=%s&mode=%s&output=json%s' % (sabnzbd_url_no_api(), get_setting_value('sabnzbd_api'), mode, extra)

@app.route('/xhr/sabnzbd')
@requires_auth
def xhr_sabnzbd():
    old_config = False

    if not get_setting_value('sabnzbd_host'):
        if get_setting_value('sabnzbd_url') != None:
            old_config = True

    try:
        result = urllib.urlopen(sabnzbd_url('queue')).read()
        sabnzbd = json.JSONDecoder().decode(result)
        sabnzbd = sabnzbd['queue']
        
        percentage_total = 0
        download_speed = '%s kB/s' % ((sabnzbd['kbpersec'])[:-3])
    
        if sabnzbd['slots']:
            percentage_total = int(100 - (float(sabnzbd['mbleft']) / float(sabnzbd['mb']) * 100))

    except:
        sabnzbd = None
        percentage_total = None
        download_speed = None

    return render_template('sabnzbd-queue.html',
        sabnzbd = sabnzbd,
        percentage_total = percentage_total,
        download_speed = download_speed,
        old_config = old_config,
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
