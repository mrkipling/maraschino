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
        playerid = active_player[0]['playerid']
        player_info = xbmc.Player.GetProperties(playerid=playerid, properties=['time', 'totaltime', 'position', 'percentage', 'repeat', 'shuffled'])
        muted = xbmc.Application.GetProperties(properties=['muted'])['muted']
        vfs_url = '/xhr/vfs_proxy/'

        if active_player[0]['type'] == 'video':
            currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['title', 'season', 'episode', 'duration', 'showtitle', 'fanart', 'tvshowid', 'plot', 'thumbnail'])['item']
            fanart_url = currently_playing['fanart']
            itemart_url = currently_playing['thumbnail']

        # if watching a TV show

            if currently_playing['tvshowid'] != -1:
                fanart_url = xbmc.VideoLibrary.GetTVShowDetails(tvshowid = currently_playing['tvshowid'], properties = ['fanart'])['tvshowdetails']['fanart']
                itemart_url = currently_playing['thumbnail']

        # if playing music

        if active_player[0]['type'] == 'audio':
            currently_playing = xbmc.Player.GetItem(playerid = 0, properties = ['title', 'duration', 'fanart', 'artist', 'albumartist', 'album', 'track', 'artistid', 'albumid', 'thumbnail', 'year'])['item']
            fanart_url = currently_playing['fanart']
            itemart_url = currently_playing['thumbnail']

        try:
            itemart = vfs_url + strip_special(itemart_url)

        except:
            itemart = None

    except:
        return jsonify({ 'playing': False })

    try:
        fanart = vfs_url + strip_special(fanart_url)

    except:
        fanart = None
	
    return render_template('currently_playing.html',
        currently_playing = currently_playing,
        fanart = fanart,
        itemart = itemart,
        shuffled = player_info['shuffled'],
        repeat = player_info['repeat'],
        muted = muted,
        current_time = format_time(player_info['time']),
        total_time = format_time(player_info['totaltime']),
        percentage_progress = int(player_info['percentage']),
    )

@app.route('/xhr/synopsis')
@requires_auth
def xhr_synopsis():
    return render_template('synopsis.html')
