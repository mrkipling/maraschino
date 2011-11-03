from flask import Flask, jsonify
import jsonrpclib

from htpcfrontend import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/play_episode/<int:episode_id>')
@requires_auth
def xhr_play_episode(episode_id):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    xbmc.Playlist.Clear(playlistid=1)

    item = { 'episodeid': episode_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/play_movie/<int:movie_id>')
@requires_auth
def xhr_play_movie(movie_id):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    xbmc.Playlist.Clear(playlistid=1)

    item = { 'movieid': movie_id }
    xbmc.Playlist.Add(playlistid=1, item=item)

    item = { 'playlistid': 1 }
    xbmc.Player.Open(item)

    return jsonify({ 'success': True })

@app.route('/xhr/controls/<command>')
@requires_auth
def xhr_controls(command):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    if command == 'play_pause':
        xbmc.Player.PlayPause(playerid=1)

    elif command == 'stop':
        xbmc.Player.Stop(playerid=1)

    return jsonify({ 'success': True })
