from flask import Flask, jsonify, render_template
import jsonrpclib, maraschino
from maraschino import app
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
        volume = xbmc.Application.GetProperties(properties=['volume'])['volume']

        if active_player[0]['type'] == 'video':
            currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['title', 'season', 'episode', 'duration', 'showtitle', 'fanart', 'tvshowid', 'plot', 'thumbnail'])['item']

        if active_player[0]['type'] == 'audio':
            currently_playing = xbmc.Player.GetItem(playerid = 0, properties = ['title', 'duration', 'fanart', 'artist', 'albumartist', 'album', 'track', 'artistid', 'albumid', 'thumbnail', 'year'])['item']

        fanart_url = currently_playing['fanart']
        itemart_url = currently_playing['thumbnail']
        vfs_url = maraschino.WEBROOT + '/xhr/vfs_proxy/'
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
        volume = volume,
        current_time = format_time(player_info['time']),
        total_time = format_time(player_info['totaltime']),
        percentage_progress = int(player_info['percentage']),
        total_time_seconds = player_info['totaltime']['hours']*3600+player_info['totaltime']['minutes']*60+player_info['totaltime']['seconds'],
    )

@app.route('/xhr/synopsis')
@requires_auth
def xhr_synopsis():
    return render_template('synopsis.html')
