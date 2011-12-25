from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from lib.tools import *

# documentation can be found @ http://packages.python.org/transmissionrpc/
import transmissionrpc

@app.route('/xhr/transmission')
@requires_auth
def xhr_transmission():
    trans_host = get_setting_value('trans_host')

    params = {
        'address': get_setting_value('trans_host'),
        'port': get_setting_value('trans_port'),
        'user': get_setting_value('trans_user'),
        'password': get_setting_value('trans_pass')
    }

    try:
        transmission = transmissionrpc.Client(**params)
        torrents = transmission.info()
        for i, torrent in torrents.iteritems():
            statusline = "[%(status)s] %(down)s down (%(pct).2f%%), %(up)s up (Ratio: %(ratio).2f)" % \
                {'down': torrent.downloadedEver, 'pct': torrent.progress, \
                'up': torrent.uploadedEver, 'ratio': torrent.ratio, \
                'status': torrent.status}
            torrentid = torrent.id
            size = torrent.size
            name = torrent.name
            status = torrent.status
            downsize = torrent.completed
            upsize = torrent.uploadedEver
            ratio = torrent.ratio
            progress = torrent.progress
            eta = torrent.eta
            if torrent.status is 'downloading':
                statusline += " ETA: %(eta)s" % \
                    {'eta': torrent.eta}

    except:
        torrentid = 0,
        name = None,
        status = None,
        size = 0,
        downsize = 0,
        progress = 0

    return render_template('transmission.html',
            torrents = torrents,
            torrentid = torrentid,
            name = name,
            status = status,
            size = size,
            downsize = downsize,
            progress = progress,
        )

