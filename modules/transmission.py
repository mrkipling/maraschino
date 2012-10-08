# Author: Geoffrey Huntley <ghuntley@ghuntley.com>

from flask import Flask, jsonify, render_template
import transmissionrpc

from datetime import timedelta
from maraschino.tools import *
from maraschino import app, logger


def log_exception(e):
    logger.log('Transmission :: EXCEPTION -- %s' % e, 'DEBUG')

@app.route('/xhr/transmission')
@app.route('/xhr/transmission/')
@requires_auth
def xhr_transmission():
    # initialize empty list, which will be later populated with listing
    # of active torrents [of transmissionrpc.Client().info()]
    transmission = list()
    seeding = list()

    # initialize empty datetime, which will be later incremented
    # to hold the total time remaining for all active downloads
    eta = timedelta()

    # transmissionrpc connection params
    params = {
        'address' : get_setting_value('transmission_ip'),
        'port' : get_setting_value('transmission_port'),
        'user' : get_setting_value('transmission_user') or None,
        'password' : get_setting_value('transmission_password') or None
    }
    
    connection = False

    try:
        client = transmissionrpc.Client(**params)

        stats = client.session_stats()

        # return list of running jobs:
        # {1: <Torrent 1 "Hello">, 2: <Torrent 2 "World">}
        torrents = client.list()
        
        if client is not None:
            connection = True

        # loop through each job, add any active (downloading) torrents to the transmission list()
        for i in torrents:
            torrent = client.info(i)[i]
            if torrent.status == 'downloading':
                transmission.append(torrent)

                # take the ETA for the current torrent, add it to the total ETA remaining
                if torrent.eta is not None:
                    eta = eta + torrent.eta
            
            # if torrent is seeding instead, note as such            
            elif torrent.status == 'seeding':
                seeding.append(torrent)

    except Exception as e:
        log_exception(e)

    return render_template('transmission.html',
        connection = connection,
        show_empty = get_setting_value('transmission_show_empty') == '1',
        transmission = transmission,
        seeding = seeding,
        upload = "%.1f" % (stats.uploadSpeed / 1024.0),
        download = "%.1f" % (stats.downloadSpeed / 1024.0),
        eta = eta,
        seeds = len(seeding),
        down = len(transmission),
    )