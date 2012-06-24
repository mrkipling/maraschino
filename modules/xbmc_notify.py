from flask import Flask, jsonify, render_template, request
import os

from maraschino import app, RUNDIR, logger
from socket import *
from xbmc.xbmcclient import *
from maraschino.tools import get_file_list
from maraschino.models import XbmcServer

@app.route('/xhr/xbmc_notify', methods=['post'])
def xhr_notify():
    label = request.form['label']
    hostname = request.form['hostname']

    dir = os.path.join(RUNDIR, 'static', 'images', 'notifications')
    icons = get_file_list(
        folder = dir,
        extensions = ['.png', '.jpg'],
        prepend_path = False,
    )

    return render_template('xbmc_notify_dialog.html',
    label = label,
    hostname = hostname,
    icons = icons,
    )

@app.route('/xhr/xbmc_notify/send', methods=['post'])
def xhr_notify_message():
    label = str(request.form['label'])
    hostname = str(request.form['hostname'])
    message = str(request.form['message'])
    title = str(request.form['title'])
    port = 9777
    icon = os.path.join(RUNDIR, 'static', 'images', 'notifications', request.form['image'])

    if title == "Title":
        title = "Maraschino"

    if not os.path.exists(icon):
        icon = os.path.join(RUNDIR, 'static', 'images', 'maraschino_logo.png')


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

    addr = (hostname, port)
    sock = socket(AF_INET,SOCK_DGRAM)

    try:
        logger.log('NOTIFY XBMC :: Sending message to %s' % label, 'INFO')
        packet = PacketNOTIFICATION(title, message, icon_type, icon)
        packet.send(sock, addr)
        return jsonify({ 'status': 'successful'})
    except:
        logger.log('NOTIFY XBMC :: Message failed to send', 'ERROR')
        return jsonify({ 'error': 'Message failed to send'})
