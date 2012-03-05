from flask import Flask, jsonify, render_template
import jsonrpclib

from Maraschino import app
from socket import *
from xbmc.xbmcclient import XBMCClient
from maraschino.tools import get_setting_value
import time, os

@app.route('/xhr/notify')
def xhr_notify():
    addresses = str(get_setting_value('notify_addresses'))
    addresses = addresses.split(", ")
    name_address = []
    for address in addresses:
        x = address.find(":")
        name = address[:x]
        ip = address[x+2:]
        name_address.append({ 'name': name, 'address': ip })

    return render_template('notify.html',
    name_address = name_address,
    )

@app.route('/xhr/notify/<address>/<message>')
def xhr_notify_message(address, message):
    message = str(message)
    address = str(address)
    icon = os.path.abspath('static/images/maraschino_logo.png')
    if not os.path.exists(icon):
        icon = os.path.abspath('maraschino/static/images/maraschino_logo.png')

    try:
        xbmc = XBMCClient('Maraschino', icon, ip=address)
        xbmc.send_notification(title="Maraschino", message=message, icon_file=icon)
        return jsonify({ 'status': 'successful'})
    except:
        return jsonify({ 'error': 'failed'})


