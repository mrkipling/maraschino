# Author: Geoffrey Huntley <ghuntley@ghuntley.com>

from flask import Flask, jsonify, render_template
import transmissionrpc

from datetime import timedelta
from Maraschino import app
from maraschino.tools import *

@app.route('/xhr/transmission')
@requires_auth
def xhr_transmission():
    # initialize empty list, which will be later populated with listing
    # of active torrents [of transmissionrpc.Client().info()]
    transmission = list()

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

    try:
        client = transmissionrpc.Client(**params)

        # return list of running jobs:
        # {1: <Torrent 1 "Hello">, 2: <Torrent 2 "World">}
        torrents = client.list()

        # loop through each job, add any active (downloading) torrents to the transmission list()
        for i in torrents:
            torrent = client.info(i)[i]
            if torrent.status == 'downloading':
                transmission.append(torrent)

                # take the ETA for the current torrent, add it to the total ETA remaining
                eta = eta + torrent.eta

        # unset transmission, if there are no torrents currently being downloaded/seeded
        if not transmission.__len__():
            transmission = None

    except:
        transmission = None

    return render_template('transmission.html',
        transmission = transmission,
        eta = eta
    )
