from flask import Flask, jsonify, render_template
import jsonrpclib

from Maraschino import app
from socket import *
from xbmc.xbmcclient import XBMCClient
from maraschino.tools import get_setting_value
import time

global connected
connected = False

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

def update_xbmc_object():
    host = get_setting_value('server_hostname')
    try:
        xbmc = XBMCClient("Maraschino", "./static/images/maraschino_logo.png", ip=host)
    except:
        xbmc = None

    return xbmc
