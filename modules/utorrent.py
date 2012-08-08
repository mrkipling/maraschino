# Author: Geoffrey Huntley <ghuntley@ghuntley.com>
#Author: robweber
#Based on the tranmission maraschino module by Geoffrey Huntley <ghuntley@ghuntley.com>

from flask import Flask, jsonify, render_template
import utorrentclient

from datetime import timedelta
from Maraschino import app
from maraschino.tools import *

@app.route('/xhr/utorrent/')
@requires_auth
def xhr_utorrent():
    # initialize empty list, which will be later populated with listing
    # of active torrents [of transmissionrpc.Client().info()]
    utorrent = list()

    # initialize empty datetime, which will be later incremented
    # to hold the total time remaining for all active downloads
    eta = timedelta()


    try:
        client = utorrentclient.uTorrent(get_setting_value('utorrent_ip'),get_setting_value('utorrent_port'),get_setting_value('utorrent_user'),get_setting_value('utorrent_password'))

        # return list of running jobs:
        # {1: <Torrent 1 "Hello">, 2: <Torrent 2 "World">}
        torrents = client.listTorrents()

        # loop through each job, add any active (downloading) torrents to utorrent()
        for i in torrents:
            if int(i.progress) < 100:
                utorrent.append(i)

        # unset transmission, if there are no torrents currently being downloaded/seeded
        if not utorrent.__len__():
            utorrent = None
    except:
        utorrent = None


    return render_template('utorrent.html',
        torrents = utorrent
    )

