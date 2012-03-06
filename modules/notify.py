from flask import Flask, jsonify, render_template
import jsonrpclib

from Maraschino import app
from socket import *
from xbmc.xbmcclient import XBMCClient
from maraschino.tools import *
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

    dir = './static/images/notifications'
    icons = get_file_list(
        folder = dir,
        extensions = ['.png', '.jpg'],
        prepend_path = False,
    )

    return render_template('notify.html',
    name_address = name_address,
    icons = icons,
    )

@app.route('/xhr/notify/<icon>/<address>/<title>/<message>')
def xhr_notify_message(icon, address, title, message):
    message = str(message)
    address = str(address)
    title = str(title)
    icon = os.path.abspath('static/images/notifications/' + icon)

    if not os.path.exists(icon):
        icon = os.path.abspath('static/images/maraschino_logo.png')

    if not os.path.exists(icon):
        icon = os.path.abspath('maraschino/static/images/maraschino_logo.png')

    try:
        xbmc = XBMCClient(title, icon, ip=address)
        xbmc.send_notification(title=title, message=message, icon_file=icon)
        return jsonify({ 'status': 'successful'})
    except:
        return jsonify({ 'error': 'failed'})


