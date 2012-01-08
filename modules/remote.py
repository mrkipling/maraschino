from flask import Flask, jsonify, render_template
import jsonrpclib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *
from socket import *
from xbmcclient import XBMCClient
import time

global connected
global xbmc
xbmc = XBMCClient("Maraschino", "./static/images/maraschino_logo.png", ip=get_setting_value('server_hostname'))
connected = False

@app.route('/remote/<key>')
def remote(key):
    global connected

    xbmc = update_xbmc_object()

    if not connected:
        if xbmc.connect():
            connected = True
            
    xbmc.send_keyboard_button(key)

    time.sleep(0.5)
    
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
    global xbmc
    host = get_setting_value('server_hostname')
    if host is not xbmc.get_ip():
        xbmc = XBMCClient("Maraschino", "./static/images/maraschino_logo.png", ip=host)
        
    return xbmc
