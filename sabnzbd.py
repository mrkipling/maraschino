from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from tools import *

@app.route('/xhr/sabnzbd')
@requires_auth
def xhr_sabnzbd():
    SABNZBD_URL = get_setting_value('sabnzbd_url')

    try:
        if SABNZBD_URL == None:
            raise Exception

        url = '%s&mode=qstatus&output=json' % (SABNZBD_URL)
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
    )

