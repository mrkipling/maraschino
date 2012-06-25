from flask import jsonify, render_template
import jsonrpclib
import maraschino
from maraschino import app, logger
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
            currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['title', 'season', 'episode', 'duration', 'showtitle', 'fanart', 'tvshowid', 'plot', 'thumbnail', 'year'])['item']

        if active_player[0]['type'] == 'audio':
            currently_playing = xbmc.Player.GetItem(playerid = 0, properties = ['title', 'duration', 'fanart', 'artist', 'albumartist', 'album', 'track', 'artistid', 'albumid', 'thumbnail', 'year'])['item']

        fanart = currently_playing['fanart']
        itemart = currently_playing['thumbnail']

    except:
        return jsonify({ 'playing': False })
	
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

@app.route('/xhr/currently_playing/playlist')
@requires_auth
def xhr_current_playlist():
    xbmc = jsonrpclib.Server(server_api_address())

    active_player = xbmc.Player.GetActivePlayers()
    playerid = active_player[0]['playerid']
    player_info = xbmc.Player.GetProperties(playerid=playerid, properties=['position'])
    currently_playing = xbmc.Player.GetItem(playerid = playerid)['item']
    playlist = xbmc.Playlist.GetItems(playlistid = playerid)

    if playlist['limits']['total']:
        for item in playlist['items']:
            item['position'] = playlist['items'].index(item)

            if item['position'] == player_info['position']:
                if item['label'] == currently_playing['label']:
                    item['playing'] = True
            else:
                item['playing'] = False

    playlist['id'] = playerid

    return render_template('playlist_dialog.html', playlist=playlist)

@app.route('/xhr/synopsis')
@requires_auth
def xhr_synopsis():
    return render_template('synopsis.html')
