from flask import Flask, jsonify, render_template
import jsonrpclib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/xbmc_control')
@requires_auth
def xhr_xbmc_control():
    api_address = server_api_address()
    
    try:
        xbmc = jsonrpclib.Server(api_address)
        version = (xbmc.Application.GetProperties(properties=['version']))
    except:
        version = None

    return render_template('xbmc_control.html', version = version)

def check_server():
    api_address = server_api_address()
    
    try:
        xbmc = jsonrpclib.Server(api_address)
        version = (xbmc.Application.GetProperties(properties=['version']))
    except:
        version = None

    return version
