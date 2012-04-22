from flask import Flask, jsonify, render_template
import jsonrpclib, os

from Maraschino import app
from socket import *
from xbmc.xbmcclient import *
from maraschino.tools import *
from maraschino.models import XbmcServer

@app.route('/xhr/xbmc_notify')
def xhr_notify():
    name_address = []
    servers_db = XbmcServer.query.order_by(XbmcServer.position)

    for server in servers_db:
        server = {'name': server.label, 'address': server.hostname}
        name_address.append(server)

    dir = './static/images/notifications'
    icons = get_file_list(
        folder = dir,
        extensions = ['.png', '.jpg'],
        prepend_path = False,
    )

    return render_template('xbmc_notify.html',
    name_address = name_address,
    icons = icons,
    )

@app.route('/xhr/xbmc_notify/<icon>/<address>/<title>/<message>')
def xhr_notify_message(icon, address, title, message):
    message = str(message)
    ip = str(address)
    port = int(get_setting_value('xbmc_event_port'))
    title = str(title)
    icon = os.path.abspath('static/images/notifications/' + icon)

    if not os.path.exists(icon):
        icon = os.path.abspath('static/images/maraschino_logo.png')

    if not os.path.exists(icon):
        icon = os.path.abspath('maraschino/static/images/maraschino_logo.png')

    if icon[-3:] == "png":
        icon_type = ICON_PNG
    elif icon[-3:] == "jpg":
        icon_type = ICON_JPEG
    elif icon[-4:] == "jpeg":
        icon_type = ICON_JPEG
    elif icon[-3:] == "gif":
        icon_type = ICON_GIF
    else:
        icon_type = ICON_NONE

    if title == "Title":
        title = "Maraschino";

    if message == "Message":
        message = None;

    addr = (ip, port)
    sock = socket(AF_INET,SOCK_DGRAM)

    try:
        packet = PacketNOTIFICATION(title, message, icon_type, icon)
        packet.send(sock, addr)
        return jsonify({ 'status': 'successful'})
    except:
        return jsonify({ 'error': 'failed'})
