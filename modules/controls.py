from flask import Flask, jsonify
import jsonrpclib, socket, struct

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

@app.route('/xhr/enqueue_video/<video_type>/<int:video_id>')
@requires_auth
def xhr_enqueue_video(video_type, video_id):
    xbmc = jsonrpclib.Server(server_api_address())
    
    item = { video_type + 'id': video_id }
    xbmc.Playlist.Add(playlistid=1, item=item)
    
    return jsonify({ 'success': True })

@app.route('/xhr/enqueue_audio/<audio_type>/<int:audio_id>')
@requires_auth
def xhr_enqueue_audio(audio_id):
    xbmc = jsonrpclib.Server(server_api_address())
    
    item = { audio_type + 'id': audio_id }
    xbmc.Playlist.Add(playlistid=0, item=item)
    
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

    if command == 'play_pause':
        xbmc.Player.PlayPause(playerid=1)

    elif command == 'stop':
        xbmc.Player.Stop(playerid=1)

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
