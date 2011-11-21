from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from tools import *

@app.route('/xhr/sabnzbd')
@requires_auth
def xhr_sabnzbd():
    SABNZBD_URL = get_setting_value('sabnzbd_url')

    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=queue&start=START&limit=LIMIT&output=json' % (SABNZBD_URL)
        result = urllib.urlopen(url).read()
        sabnzbd_base = json.JSONDecoder().decode(result)
        sabnzbd = sabnzbd_base['queue']

        percentage_total = 0
        currentdl = 0        		
        download_speed = '%s kB/s' % (int(float(sabnzbd['kbpersec'])))

        if sabnzbd['slots']:
            percentage_total = int(100 - (float(slotA['mbleft']) / float(slotA['mb']) * 100))
            currentdl = sabnzbd['slots'][0]

    except:
        sabnzbd = None
        percentage_total = None
        download_speed = None
        currentdl = None

    return render_template('sabnzbd.html',
        sabnzbd = sabnzbd,
        percentage_total = percentage_total,
        download_speed = download_speed,
        currentdl = currentdl,
    )
    
@app.route('/sabnzbd/<state>')
def state_change(state):
    SABNZBD_URL = get_setting_value('sabnzbd_url')
    
    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=%s' % (SABNZBD_URL, state)
        result = urllib.urlopen(url).read()
            
    except:
        sabnzbd = None
        percentage_total = None
        download_speed = None
        
    return result

@app.route('/sabnzbd/set_speed/<speed>')
def set_speed(speed):
    SABNZBD_URL = get_setting_value('sabnzbd_url')
    
    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=config&name=speedlimit&value=%s' % (SABNZBD_URL, speed)
        result = urllib.urlopen(url).read()
            
    except:
        sabnzbd = None
        
    return result
