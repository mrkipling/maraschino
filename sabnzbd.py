from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from tools import *

SABNZBD_URL = get_setting_value('sabnzbd_url')

@app.route('/xhr/sabnzbd')
@requires_auth
def xhr_sabnzbd():
    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=queue&start=START&limit=LIMIT&output=json' % (SABNZBD_URL)
        result = urllib.urlopen(url).read()
        sabnzbd_base = json.JSONDecoder().decode(result)
        sabnzbd = sabnzbd_base['queue']

        percentage_total = 0
        download_speed = '%s kB/s' % (int(float(sabnzbd['kbpersec'])))
        
        if sabnzbd['slots']:
            percentage_total = int(sabnzbd['slots'][0]['percentage'])

    except:
        sabnzbd = None
        percentage_total = None
        download_speed = None

    return render_template('sabnzbd.html',
        sabnzbd = sabnzbd,
        percentage_total = percentage_total,
        download_speed = download_speed,
    )
    
@app.route('/sabnzbd/<state>')
@requires_auth
def state_change(state):    
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
@requires_auth
def set_speed(speed):    
    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=config&name=speedlimit&value=%s' % (SABNZBD_URL, speed)
        result = urllib.urlopen(url).read()
            
    except:
        sabnzbd = None
        
    return result
    
@app.route('/sabnzbd/remove/<sabid>')
@requires_auth
def remove_item(sabid):
    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=queue&name=delete&value=%s' % (SABNZBD_URL, sabid)
        result = urllib.urlopen(url).read()
        if result.rfind('ok') >= 0:
        	result = sabid
            
    except:
        result = False
        
    return result
