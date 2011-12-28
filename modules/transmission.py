from flask import Flask, jsonify, render_template
import transmissionrpc

from datetime import timedelta
from maraschino import app
from settings import *
from lib.tools import *

@app.route('/xhr/transmission')
@requires_auth
def xhr_transmission():
    TRANSMISSION_IP = get_setting_value('transmission_ip')
    TRANSMISSION_PORT = get_setting_value('transmission_port')
    TRANSMISSION_USER = get_setting_value('transmission_user') or None
    TRANSMISSION_PASSWORD = get_setting_value('transmission_password') or None

    # initialize empty list, which will be later populated with listing
    # of active torrents [of transmissionrpc.Client().info()]
    transmission = list()

    eta = timedelta()

    try:
        if TRANSMISSION_IP == None or TRANSMISSION_PORT == None:
            raise Exception

        client = transmissionrpc.Client(TRANSMISSION_IP, port=TRANSMISSION_PORT, user=TRANSMISSION_USER, password=TRANSMISSION_PASSWORD)

        # return list of running jobs:
        # {1: <Torrent 1 "Hello">, 2: <Torrent 2 "World">}
        torrents = client.list()

        # loop through each job, add atimedeltany active (downloading) torrents to the transmission list()
        for x in torrents:
            torrent = client.info(x)[x]
            if torrent.status == 'downloading':
                eta = eta + torrent.eta
                transmission.append(torrent)
        # unset transmission, if there are no torrents currently being downloaded/seeded
        if not transmission.__len__():
            transmission = None

    except:
        transmission = None

    return render_template('transmission.html',
        transmission = transmission,
        eta = eta
    )
