from flask import Flask, jsonify, render_template

from maraschino import app, RUNDIR
from socket import *
from xbmc.xbmcclient import XBMCClient
from maraschino.tools import get_setting_value
from maraschino.noneditable import *

import time, os

global connected
connected = False

def update_xbmc_object():
    serversettings = server_settings()
    host = serversettings['hostname']

    try:
        icon = RUNDIR + '/static/images/maraschino_logo.png'

        xbmc = XBMCClient('Maraschino', icon, ip=host)

    except:
        xbmc = None

    return xbmc

@app.route('/remote/<key>')
def remote(key):
    global connected

    xbmc = update_xbmc_object()

    if not connected:
        if xbmc.connect():
            connected = True

    xbmc.send_keyboard_button(key)

    time.sleep(0.3)

    if xbmc.release_button():
            return jsonify({ 'status': 'successful'})

    return jsonify({ 'error': 'failed'})

@app.route('/remote/ping')
def ping():
    global connected

    xbmc = update_xbmc_object()

    if xbmc.ping():
        connected = True
        return jsonify({ 'status': 'successful'})

    connected = False
    return jsonify({ 'error': 'failed'})

@app.route('/remote/close')
def close():
    global connected

    xbmc = update_xbmc_object()

    if xbmc.close():
        connected = False
        return jsonify({ 'status': 'successful'})

    return jsonify({ 'error': 'failed'})

@app.route('/remote/connect')
def connect():
    global connected

    xbmc = update_xbmc_object()

    if xbmc.connect():
        connected = True
        return jsonify({ 'status': 'successful'})

    return jsonify({ 'error': 'failed'})
