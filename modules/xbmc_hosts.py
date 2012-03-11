from flask import Flask, jsonify, render_template

import jsonrpclib
from Maraschino import app
from settings import *
from maraschino.tools import *
from maraschino.models import Setting
from maraschino.database import db_session

@app.route('/xhr/xbmc_hosts')
def xhr_xbmc_hosts():

    hosts = []

    try:
        for host in XBMC_HOSTS:
            if host['HOSTNAME'] and host['PORT']:
                if not host['USERNAME']:
                    host['USERNAME'] = "no username"
                if not host['PASSWORD']:
                    host['PASSWORD'] = "no password"
                hosts.append(host)

        active = get_setting_value('server_hostname')

        return render_template('drop_menu.html',
            XBMC_HOSTS = hosts,
            active = active,
        )

    except:
        return None

@app.route('/xhr/xbmc_hosts/<hostname>/<port>/<username>/<password>')
def xhr_new_xbmc_host(hostname, port, username, password):

    if username == "no username":
        username = ""
    if password == "no password":
        password = ""

    user_pass = ""

    if username != "":
        user_pass = username
        if password != "":
            user_pass += ':' + password
        user_pass += '@'

    host_address = 'http://%s%s:%s/jsonrpc' % (user_pass, hostname, port, )
    xbmc = jsonrpclib.Server(host_address)

    try:
        xbmc.JSONRPC.Ping()
        settings = Setting.query.order_by(Setting.id)

        for setting in settings:
            if setting.key == 'server_hostname':
                setting.value = hostname
            if setting.key == 'server_port':
                setting.value = port
            if setting.key == 'server_username':
                setting.value = username
            if setting.key == 'server_password':
                setting.value = password

        db_session.commit()

        return jsonify({ 'status': 'successful'})

    except:
        return jsonify({ 'error': 'failed'})
