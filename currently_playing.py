from flask import Flask, jsonify, render_template
import jsonrpclib

from htpcfrontend import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/currently_playing')
@requires_auth
def xhr_currently_playing():
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['title', 'season', 'episode', 'duration', 'showtitle', 'fanart', 'tvshowid', 'plot'])['item']
        fanart_url = currently_playing['fanart']

        # if watching a TV show
        if currently_playing['tvshowid'] != -1:
            fanart_url = xbmc.VideoLibrary.GetTVShowDetails(tvshowid = currently_playing['tvshowid'], properties = ['fanart'])['tvshowdetails']['fanart']

    except:
        return jsonify({ 'playing': False })

    try:
        fanart = '%s/vfs/%s' % (safe_server_address(), fanart_url)

    except:
        fanart = None

    time = xbmc.Player.GetProperties(playerid=1, properties=['time', 'totaltime', 'position', 'percentage'])

    return render_template('currently_playing.html',
        currently_playing = currently_playing,
        fanart = fanart,
        time = time,
        current_time = format_time(time['time']),
        total_time = format_time(time['totaltime']),
        percentage_progress = int(time['percentage']),
    )

@app.route('/xhr/synopsis')
@requires_auth
def xhr_synopsis():
    return render_template('synopsis.html')
