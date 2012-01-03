from flask import Flask, jsonify, render_template
import jsonrpclib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/remote/arrow/<direction>')
def arrow(direction):
    try:
        api_address = server_api_address()

        if not api_address:
            return jsonify({ 'error': 'server address not defined' })

        xbmc = jsonrpclib.Server(api_address)
    except:
        return jsonify({ 'error': 'could not reach XBMC' })

    try:
        if direction == 'left':
            xbmc.Input.left()
        elif direction == 'up':
            xbmc.Input.up()
        elif direction == 'right':
            xbmc.Input.right()
        elif direction == 'down':
            xbmc.Input.down()
    except:
        error = '%s input failed' % (direction)
        return jsonify({ 'error': error})
        
    return jsonify({ 'status': 'success'})