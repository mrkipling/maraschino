from flask import Flask, jsonify, render_template
import jsonrpclib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/currently_playing')
@requires_auth
def xhr_currently_playing():
    try:
        api_address = server_api_address()

        if not api_address:
            raise Exception

        xbmc = jsonrpclib.Server(api_address)
        active_player = xbmc.Player.GetActivePlayers()

        if active_player[0]['type'] == 'video':

            albumart = None
            currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['title', 'season', 'episode', 'duration', 'showtitle', 'fanart', 'tvshowid', 'plot'])['item']
            fanart_url = currently_playing['fanart']

        # if watching a TV show
            if currently_playing['tvshowid'] != -1:
                fanart_url = xbmc.VideoLibrary.GetTVShowDetails(tvshowid = currently_playing['tvshowid'], properties = ['fanart'])['tvshowdetails']['fanart']

            time = xbmc.Player.GetProperties(playerid=1, properties=['time', 'totaltime', 'position', 'percentage'])

        #if playing music
        if active_player[0]['type'] == 'audio':
            currently_playing = xbmc.Player.GetItem(playerid = 0, properties = ['title', 'duration', 'fanart', 'artist', 'album', 'track', 'artistid', 'albumid', 'thumbnail'])['item']
            fanart_url = currently_playing['fanart']
            albumart_url = currently_playing['thumbnail']
            time = xbmc.Player.GetProperties(playerid=0, properties=['time', 'totaltime', 'position', 'percentage'])

            try:
                albumart = '%s/vfs/%s' % (safe_server_address(), albumart_url)

            except:
                albumart = None

    except:
        return jsonify({ 'playing': False })

    try:
        fanart = '%s/vfs/%s' % (safe_server_address(), fanart_url)

    except:
        fanart = None



	
    return render_template('currently_playing.html',
        currently_playing = currently_playing,
        fanart = fanart,
        albumart = albumart,
        time = time,
        current_time = format_time(time['time']),
        total_time = format_time(time['totaltime']),
        percentage_progress = int(time['percentage']),
    )

@app.route('/xhr/synopsis')
@requires_auth
def xhr_synopsis():
    return render_template('synopsis.html')
