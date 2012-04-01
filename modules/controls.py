from flask import Flask, jsonify
import jsonrpclib, socket, struct
import urllib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/play/<file_type>/<media_type>/<int:media_id>')
@requires_auth
def xhr_play_media(file_type, media_type, media_id):
    xbmc = jsonrpclib.Server(server_api_address())

    if file_type == 'video':
        xhr_clear_playlist('video')

        if media_type == 'tvshow':
            tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, sort={ 'method': 'episode' })['episodes']

            for episode in tvshow_episodes:
                episodeid = episode['episodeid']
                item = { 'episodeid': episodeid }
                xbmc.Playlist.Add(playlistid=1, item=item)

        elif 'season' in media_type:
            media_type = media_type.split('_')
            season = int(media_type[1])

            tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, season=season, sort={ 'method': 'episode' })['episodes']

            for episodes in tvshow_episodes:
                episodeid = episodes['episodeid']
                item = { 'episodeid': episodeid }
                xbmc.Playlist.Add(playlistid=1, item=item)

        else:
            item = { media_type + 'id': media_id }
            xbmc.Playlist.Add(playlistid=1, item=item)

        playlistid = 1

    else:
        xhr_clear_playlist('audio')

        item = { media_type + 'id': media_id }
        xbmc.Playlist.Add(playlistid=0, item=item)

        playlistid = 0

    item = { 'playlistid': playlistid }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue/<file_type>/<media_type>/<int:media_id>')
@requires_auth
def xhr_enqueue_media(file_type, media_type, media_id):
    xbmc = jsonrpclib.Server(server_api_address())

    if file_type == 'video':

        if media_type == 'tvshow':
            tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, sort={ 'method': 'episode' })['episodes']

            for episode in tvshow_episodes:
                episodeid = episode['episodeid']
                item = { 'episodeid': episodeid }
                xbmc.Playlist.Add(playlistid=1, item=item)

        elif 'season' in media_type:
            media_type = media_type.split('_')
            season = int(media_type[1])

            tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, season=season, sort={ 'method': 'episode' })['episodes']

            for episodes in tvshow_episodes:
                episodeid = episodes['episodeid']
                item = { 'episodeid': episodeid }
                xbmc.Playlist.Add(playlistid=1, item=item)

        else:
            item = { media_type + 'id': media_id }
            xbmc.Playlist.Add(playlistid=1, item=item)

        playlistid = 1

    else:

        item = { media_type + 'id': media_id }
        xbmc.Playlist.Add(playlistid=0, item=item)

        playlistid = 0

    item = { 'playlistid': playlistid }

    return jsonify({ 'success': True })

@app.route('/xhr/resume/video/<video_type>/<int:video_id>')
@requires_auth
def xhr_resume_video(video_type, video_id):
    xbmc = jsonrpclib.Server(server_api_address())
    xhr_clear_playlist('video')

    if video_type == "episode":
        video = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=video_id, properties=['resume'])['episodedetails']
    else:
        video = xbmc.VideoLibrary.GetMovieDetails(movieid=video_id, properties=['resume'])['moviedetails']

    seconds = int(video['resume']['position'])

    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes

    position = { 'hours': hours, 'minutes': minutes, 'seconds': seconds }

    item = { video_type + 'id': video_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)
    xbmc.Player.Seek(playerid=1, value=position)

    return jsonify({ 'success': True })

@app.route('/xhr/play/trailer/<int:movieid>')
@requires_auth
def xhr_play_trailer(movieid):
    xbmc = jsonrpclib.Server(server_api_address())
    xhr_clear_playlist('video')

    trailer = xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties= ['trailer'])['moviedetails']['trailer']
    item = { 'file': trailer }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/play_file/<file_type>/', methods=['POST'])
@requires_auth
def xhr_play_file(file_type):
    xbmc = jsonrpclib.Server(server_api_address())

    if file_type == "music":
        file_type = "audio"
    xhr_clear_playlist(file_type)

    file = request.form['file']
    file = urllib.unquote(file.encode('ascii')).decode('utf-8')

    if file_type == "video":
        player = 1
    else:
        player = 0

    item = { 'file': file }
    xbmc.Playlist.Add(playlistid=player, item=item)

    item = { 'playlistid': player }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue_file/<file_type>/', methods=['POST'])
@requires_auth
def xhr_enqueue_file(file_type):
    xbmc = jsonrpclib.Server(server_api_address())

    file = request.form['file']
    file = urllib.unquote(file.encode('ascii')).decode('utf-8')

    if file_type == "video":
        player = 1
    else:
        player = 0

    item = { 'file': file }
    xbmc.Playlist.Add(playlistid=player, item=item)

    return jsonify({ 'success': True })

@app.route('/xhr/clear_playlist/<playlist_type>')
@requires_auth
def xhr_clear_playlist(playlist_type):
    xbmc = jsonrpclib.Server(server_api_address())

    if playlist_type == 'audio':
        xbmc.Playlist.Clear(playlistid=0)
    elif playlist_type == 'video':
        xbmc.Playlist.Clear(playlistid=1)

    return jsonify({ 'success': True })

@app.route('/xhr/controls/<command>')
@requires_auth
def xhr_controls(command):
    xbmc = jsonrpclib.Server(server_api_address())
    try:
        active_player = xbmc.Player.GetActivePlayers()
    except:
        active_player = None

    if command == 'play_pause':
        if active_player[0]['type'] == 'video':
            xbmc.Player.PlayPause(playerid=1)
        elif active_player[0]['type'] == 'audio':
            xbmc.Player.PlayPause(playerid=0)

    elif command == 'stop':
        if active_player[0]['type'] == 'video':
            xbmc.Player.Stop(playerid=1)
        elif active_player[0]['type'] == 'audio':
            xbmc.Player.Stop(playerid=0)

    elif command == 'update_video':
    	xbmc.VideoLibrary.Scan()

    elif command == 'clean_video':
    	xbmc.VideoLibrary.Clean()

    elif command == 'update_audio':
        xbmc.AudioLibrary.Scan()

    elif command == 'clean_audio':
        xbmc.AudioLibrary.Clean()

    elif command == 'poweroff':
        xbmc.System.Shutdown()

    elif command == 'suspend':
        xbmc.System.Suspend()

    elif command == 'reboot':
	    xbmc.System.Reboot()

    elif command == 'poweron':
        server_macaddress = get_setting_value('server_macaddress')
        addr_byte = server_macaddress.split(':')
        hw_addr = struct.pack('BBBBBB',
        int(addr_byte[0], 16),
        int(addr_byte[1], 16),
        int(addr_byte[2], 16),
        int(addr_byte[3], 16),
        int(addr_byte[4], 16),
        int(addr_byte[5], 16))

        msg = '\xff' * 6 + hw_addr * 16
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, ("255.255.255.255", 9))

    return jsonify({ 'success': True })
