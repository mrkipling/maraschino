from flask import Flask, jsonify
import jsonrpclib, socket, struct
import urllib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/play_video/<video_type>/<int:video_id>')
@requires_auth
def xhr_play_video(video_type, video_id):
    xbmc = jsonrpclib.Server(server_api_address())
    xhr_clear_playlist('video')

    item = { video_type + 'id': video_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/resume_video/<video_type>/<int:video_id>')
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

@app.route('/xhr/play_tvshow/<int:tvshowid>')
@requires_auth
def xhr_play_tvshow(tvshowid):
    xbmc = jsonrpclib.Server(server_api_address())
    xhr_clear_playlist('video')

    video_type = "episode"
    tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=tvshowid, sort={ 'method': 'episode' })
    tvshow_episodes = tvshow_episodes['episodes']

    for episodes in tvshow_episodes:
        episodeid = episodes['episodeid']
        item = { video_type + 'id': episodeid }
        xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/play_season/<int:tvshow_id>/<int:video_id>')
@requires_auth
def xhr_play_season(video_id, tvshow_id):
    xbmc = jsonrpclib.Server(server_api_address())
    xhr_clear_playlist('video')

    video_type = "episode"
    tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=tvshow_id, season=video_id, sort={ 'method': 'episode' })
    tvshow_episodes = tvshow_episodes['episodes']

    for episodes in tvshow_episodes:
        episodeid = episodes['episodeid']
        item = { video_type + 'id': episodeid }
        xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/play_trailer/<int:movieid>')
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

@app.route('/xhr/play_audio/<audio_type>/<int:audio_id>')
@requires_auth
def xhr_play_audio(audio_type, audio_id):
    xbmc = jsonrpclib.Server(server_api_address())
    xhr_clear_playlist('audio')

    item = { audio_type + 'id': audio_id }
    xbmc.Playlist.Add(playlistid=0, item=item)

    item = { 'playlistid': 0 }
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

@app.route('/xhr/enqueue_tvshow/<int:video_id>')
@requires_auth
def xhr_enqueue_tvshow(video_id):
    xbmc = jsonrpclib.Server(server_api_address())

    video_type = "episode"
    tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=video_id, sort={ 'method': 'episode' })
    tvshow_episodes = tvshow_episodes['episodes']

    for episodes in tvshow_episodes:
        episodeid = episodes['episodeid']
        item = { video_type + 'id': episodeid }
        xbmc.Playlist.Add(playlistid=1, item=item)

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue_season/<int:tvshow_id>/<int:video_id>')
@requires_auth
def xhr_enqueue_season(video_id, tvshow_id):
    xbmc = jsonrpclib.Server(server_api_address())

    video_type = "episode"
    tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=tvshow_id, season=video_id, sort={ 'method': 'episode' })
    tvshow_episodes = tvshow_episodes['episodes']

    for episodes in tvshow_episodes:
        episodeid = episodes['episodeid']
        item = { video_type + 'id': episodeid }
        xbmc.Playlist.Add(playlistid=1, item=item)

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue_video/<video_type>/<int:video_id>')
@requires_auth
def xhr_enqueue_video(video_type, video_id):
    xbmc = jsonrpclib.Server(server_api_address())

    item = { video_type + 'id': video_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue_audio/<audio_type>/<int:audio_id>')
@requires_auth
def xhr_enqueue_audio(audio_type, audio_id):
    xbmc = jsonrpclib.Server(server_api_address())

    item = { audio_type + 'id': audio_id }
    xbmc.Playlist.Add(playlistid=0, item=item)

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
        if active_player[0]['type'] == 'video':
            playerid = 1
        elif active_player[0]['type'] == 'audio':
            playerid = 0
    except:
        active_player = None

    if command == 'play_pause':
        xbmc.Player.PlayPause(playerid=playerid)

    elif command == 'stop':
        xbmc.Player.Stop(playerid=playerid)

    elif command == 'volume_up':
        volume = xbmc.Application.GetProperties(properties=['volume', 'muted'])['volume']
        volume = volume + 5
        try:
            xbmc.Application.SetVolume(volume=volume)
        except:
            xbmc.Application.SetVolume(volume=100)

    elif command == 'volume_down':
        volume = xbmc.Application.GetProperties(properties=['volume', 'muted'])['volume']
        volume = volume - 5
        try:
            xbmc.Application.SetVolume(volume=volume)
        except:
            xbmc.Application.SetVolume(volume=0)

    elif command == 'mute':
        muted = xbmc.Application.GetProperties(properties=['muted'])['muted']
        if muted == True:
            xbmc.Application.SetMute(mute=False)
        else:
            xbmc.Application.SetMute(mute=True)

    elif command == 'next':
        xbmc.Player.GoNext(playerid=playerid)

    elif command == 'previous':
        xbmc.Player.GoPrevious(playerid=playerid)

    elif command == 'fast_forward':
        xbmc.Player.SetSpeed(playerid=playerid, speed='increment')

    elif command == 'rewind':
        xbmc.Player.SetSpeed(playerid=playerid, speed='decrement')

    elif 'seek' in command:
        percentage = command.split('_')
        percentage = int(percentage[1])
        print percentage
        xbmc.Player.Seek(playerid=playerid, value=percentage)

    elif command == 'shuffle':
        shuffled = xbmc.Player.GetProperties(playerid=playerid, properties=['shuffled'])['shuffled']
        if shuffled == True:
            xbmc.Player.UnShuffle(playerid=playerid)
        else:
            xbmc.Player.Shuffle(playerid=playerid)

    elif command == 'repeat':
        states = ['off', 'one', 'all']
        repeat = xbmc.Player.GetProperties(playerid=playerid, properties=['repeat'])['repeat']
        state = states.index(repeat)
        if state <= 1:
            state = state + 1
        else:
            state = 0

        state = states[state]
        xbmc.Player.Repeat(playerid=playerid, state=state)

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
