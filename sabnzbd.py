from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from tools import *

@app.route('/xhr/sabnzbd')
@requires_auth
def xhr_sabnzbd():
    SABNZBD_HOST = get_setting_value('sabnzbd_host')
    SABNZBD_PORT = get_setting_value('sabnzbd_port')
    SABNZBD_API = get_setting_value('sabnzbd_api')

    SABNZBD_URL = 'http://%s:%s' % (SABNZBD_HOST, SABNZBD_PORT)

    old_config = False

    if not SABNZBD_HOST:
        if get_setting_value('sabnzbd_url') != None:
            old_config = True

    try:
        url = '%s/api?apikey=%s&mode=qstatus&output=json' % (SABNZBD_URL, SABNZBD_API)
        result = urllib.urlopen(url).read()
        sabnzbd = json.JSONDecoder().decode(result)

        percentage_total = 0
        download_speed = '%s kB/s' % (int(sabnzbd['kbpersec']))

        if sabnzbd['paused']:
            download_speed = "PAUSED"

        if sabnzbd['jobs']:
            percentage_total = int(100 - (sabnzbd['mbleft'] / sabnzbd['mb'] * 100))

    except:
        sabnzbd = None
        percentage_total = None
        download_speed = None

    return render_template('sabnzbd.html',
        sabnzbd = sabnzbd,
        percentage_total = percentage_total,
        download_speed = download_speed,
        old_config = old_config,
    )
