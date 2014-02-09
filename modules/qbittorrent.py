# -*- coding: utf-8 -*-

import urllib2
import urllib

try:
    import json
except ImportError:
    import simplejson as json

from jinja2.filters import FILTERS

from flask import Flask, jsonify, render_template
from Maraschino import app
from maraschino import logger
from maraschino.tools import *

def qbt_http():
    if get_setting_value('qbittorrent_https') == '1':
        return 'https://'
    else:
        return 'http://'

def qbt_url():
    port = get_setting_value('qbittorrent_port')
    url_base = get_setting_value('qbittorrent_ip')
    webroot = get_setting_value('qbittorrent_webroot')
    
    if port:
        url_base= '%s:%s' % (url_base, port)
    
    if webroot:
        url_base = '%s/%s' % (url_base, webroot)
     
    url = '%s/' % url_base
    
    return qbt_http() + url

#Gets access the torrent list and start the rest.
@requires_auth
@app.route('/xhr/qbittorrent/') 
def get_torrent_list():
    url = qbt_url()
    username = get_setting_value('qbittorrent_username')
    password = get_setting_value('qbittorrent_password')
    show_que = get_setting_value('qbittorrent_show_que')
    
    realm = 'Web UI Access'
    
    authhandler = urllib2.HTTPDigestAuthHandler()
    authhandler.add_password(realm, url, username, password)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    q_in_pause = ['error', 'pausedUP', 'pausedDL', 'checkingUP']
    q_in_play = ['queuedUP', 'queuedDL', 'uploading', 'stalledUP', 'checkingDL', 'downloading', 'stalledDL']
    
    qbittorrent = None
    message = None
    result = None
    cp = 0
    
    try:
        
        result  = urllib2.urlopen(url + 'json/torrents').read()
        qbittorrent = json.JSONDecoder('UTF-8').decode(result)
    
    
    except Exception as e:
        qbittorrent_exception(e)
    
    if result: # there is connection
        if result == '[]': # if the connection ok and there is no torrents
            downloadstatus = None
            return render_template('qbittorrent/qbittorrent.html',
                result = result,
                speed = transfer_info(),
                downloadstatus = downloadstatus,
                g_global_downspeed = g_global_downspeed(),
                g_global_upspeed = g_global_upspeed())
                
        
        if qbittorrent:
            total_torrents = len(qbittorrent)
            for item in qbittorrent:
                if item['state'] in q_in_pause:
                    cp += 1
                    
            if cp == total_torrents:
                downloadstatus = 'resumeall'
            else: 
                downloadstatus = 'pauseall'
                
            return render_template('qbittorrent/qbittorrent.html',
                    result = result,
                    qbittorrent = qbittorrent, 
                    speed = transfer_info(), 
                    downloadstatus = downloadstatus, 
                    show_que = show_que,
                    message = message,
                    g_global_downspeed = g_global_downspeed(),
                    g_global_upspeed = g_global_upspeed(),
                    q_in_pause = q_in_pause)
                    
    else:
        logger.log('qbittorrent :: There is a problem reaching qBittorrent', 'INFO')
        return render_template('qbittorrent/qbittorrent.html',
            result = result,
            qbittorrent = qbittorrent)

# Current transfer info dl and upload
def transfer_info():
    url = qbt_url()
    
    try:
        result = urllib2.urlopen(url + 'json/transferInfo').read()
        tra_info = json.JSONDecoder('UTF-8').decode(result)
        
    except Exception as e:
        qbittorrent_exception(e)
        tra_info = 'ERROR'
        
    return tra_info

# singel torrent resume, pause and delete
@requires_auth
@app.route('/xhr/qbittorrent/command/<state>/<hash>/<name>/')
def command(state, hash, name):
    data = {}
    if state == 'delete':
        data['hashes'] = hash
    else:
        data['hash']  = hash
    
    data = urllib.urlencode(data)
    url = qbt_url() + 'command/' + state
    
    try:
        result = urllib2.urlopen(url, data)
        
    except Exception as e:
        qbittorrent_exception(e)
    
    if not result:
        logger.log('qBittorrent :: %s :: %s :: %s' % (state, name, hash), 'INFO')
        #data = 'true' 
        return jsonify({'status': 'false'})
    
    logger.log('qBittorrent :: %s :: %s :: %s' % (state, name, hash), 'INFO')
    return jsonify({'status': 'true'})

# sets speed limit up and down
@requires_auth
@app.route('/xhr/qbittorrent/speedlimit/<type>/<int:speed>/')
def qbittorrent_set_speedlimit(type, speed):
    speed2 = speed
    if speed == 0:
        speed = 0
    else:
        speed *= 1024
    
    url = qbt_url() + 'command/' + type
    
    data = {}
    data['limit'] = speed
    data = urllib.urlencode(data)
    
    try:
        result = urllib2.urlopen(url, data)
        
        if result:
            logger.log('qBittorrent :: set %s :: to :: %s' % (type, speed2), 'INFO')
        
    except Exception as e:
        qbittorrent_exception(e)
    
    if not result:
        logger.log('qBittorrent :: failed set :: %s :: to :: %s' %(type, speed2), 'INFO')
        return jsonify({'status': 'false'})
    
    return jsonify({'status': 'true'})

# This one pause/resumes all
@requires_auth
@app.route('/xhr/qbittorrent/command/<type>/')
def pause_resume_all(type):
    url = qbt_url() + 'command/' + type
    check_pause_status = type
    
    try:
        result = urllib2.urlopen(url)
        if result:
            logger.log('qBittorrent :: %s :: torrents' % type, 'INFO')
    
    except Exception as e:
        qbittorrent_exception(e)
    
    if not result:
        logger.log('qBittorrent :: FAILED to :: %s :: torrents' % type, 'INFO')
        return jsonify({'status': 'false'})
    
    return jsonify({'status': 'true'})

def g_global_downspeed():
    url = qbt_url() + 'command/getGlobalDlLimit'
    
    try:
        result = urllib2.urlopen(url).read()
        
        if result:
            result = int(result) / 1024
            
    except Exception as e:
        qbittorrent_exception(e)
    
    if not result:
        logger.log('qBittorrent :: FAILED to :: get globaldownload speed', 'INFO')
        result = 'ERROR'
        
    return result

def g_global_upspeed():
    url = qbt_url() + 'command/getGlobalUpLimit'
    result = None
    try:
        result = urllib2.urlopen(url).read()
        
        if result:
            result =int(result)/1024
        
    except Exception as e:
        qbittorrent_exception(e)
    
    if not result:
        result = 'ERROR'
        logger.log('qBittorrent :: FAILED :: Global upload speed is %s' % result, 'INFO')

    return result

def qbittorrent_exception(e):
    logger.log('qBittorrent :: EXCEPTION -- %s' % e, 'DEBUG')