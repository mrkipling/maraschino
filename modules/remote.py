from flask import Flask, jsonify, render_template
import jsonrpclib

from Maraschino import app
from settings import *
from noneditable import *
from tools import *
from socket import *
from xbmcclient import XBMCClient
import time

connected = False
latest_call = time.time()*1000

@app.route('/remote/<key>')
def remote(key):
    global connected
    host = get_setting_value('server_hostname')

    # Create an XBMCClient object and connect
    xbmc = XBMCClient("Maraschino", "./static/images/maraschino_logo.png", ip=host)
    
    if not connected:
        if xbmc.connect():
            connected = True
        else:
            connected = False


    # send a right key press using the keyboard map "KB" and button
    xbmc.send_keyboard_button(key)

    time.sleep(0.5)
    
    if xbmc.release_button():
            xbmc.close()
            connected = False
            return jsonify({ 'status': 'successful'})    

    return jsonify({ 'error': 'failed'})