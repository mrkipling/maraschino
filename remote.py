from flask import Flask, jsonify, render_template
import jsonrpclib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/remote/<key>')
def arrow(key):
    try:
        api_address = server_api_address()

        if not api_address:
            return jsonify({ 'error': 'server address not defined' })

        xbmc = jsonrpclib.Server(api_address)
    except:
        return jsonify({ 'error': 'could not reach XBMC' })

    if xbmc.Player.GetActivePlayers():
        return xbmc_player(key, xbmc)
    else:
        return xbmc_input(key, xbmc)

def xbmc_input(key, xbmc):
    try:
        if key == 'left':
            xbmc.Input.left()
        elif key == 'up':
            xbmc.Input.up()
        elif key == 'right':
            xbmc.Input.right()
        elif key == 'down':
            xbmc.Input.down()
        elif key == 'select':
            xbmc.Input.select()
        elif key == 'back':
            xbmc.Input.back()
        elif key == 'home':
            xbmc.Input.home()
    except:
        error = '%s input failed' % (key)
        return jsonify({ 'error': error})
        
    return jsonify({ 'status': 'success'})
    
def xbmc_player(key, xbmc):
    try:
        if key == 'select':
            xbmc.Input.select()
        elif key == 'back':
            xbmc.Input.back()
        elif key == 'home':
            xbmc.Player.PlayPause(playerid=1)
        else:
            xbmc_input(key, xbmc)
    except:
        error = '%s input failed' % (key)
        return jsonify({ 'error': error})
        
    return jsonify({ 'status': 'success'})
    