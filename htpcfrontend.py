from flask import Flask, jsonify, render_template, request
from settings import *

import json, jsonrpclib, math, urllib

app = Flask(__name__)

SERVER['username_password'] = ''
if SERVER['username'] != None:
    SERVER['username_password'] = SERVER['username']
    if SERVER['password'] != None:
        SERVER['username_password'] += ':' + SERVER['password']
    SERVER['username_password'] += '@'

SERVER_ADDRESS = 'http://%s%s:%s' % (SERVER['username_password'], SERVER['hostname'], SERVER['port'])

SERVER_API_ADDRESS = '%s/jsonrpc' % (SERVER_ADDRESS)

@app.route('/')
def index():
    return render_template('index.html',
        modules = MODULES,
        show_currently_playing = SHOW_CURRENTLY_PLAYING,
        trakt_backgrounds = TRAKT_BACKGROUNDS
    )

@app.route('/xhr/applications')
def xhr_applications():
    return render_template('applications.html',
        applications = APPLICATIONS
    )

@app.route('/xhr/recently_added')
def xhr_recently_added():
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'lastplayed', 'thumbnail'])

    return render_template('recently_added.html',
        recently_added_episodes = recently_added_episodes['episodes'][:NUM_RECENT_EPISODES],
        server = SERVER
    )

@app.route('/xhr/sabnzbd')
def xhr_sabnzbd():
    url = '%s&mode=qstatus&output=json' % (SABNZBD_URL)
    result = urllib.urlopen(url).read()
    sabnzbd = json.JSONDecoder().decode(result)

    return render_template('sabnzbd.html', sabnzbd=sabnzbd)

@app.route('/xhr/trakt')
def xhr_trakt():
    trakt = {}
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    try:
        currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['tvshowid', 'season', 'episode', 'imdbnumber', 'title'])['item']
        imdbnumber = currently_playing['imdbnumber']

        # if watching a TV show
        if currently_playing['tvshowid'] != -1:
            show = xbmc.VideoLibrary.GetTVShowDetails(tvshowid = currently_playing['tvshowid'], properties = ['imdbnumber'])['tvshowdetails']
            imdbnumber = show['imdbnumber']

    except:
        currently_playing = None

    if currently_playing:
        trakt['title'] = currently_playing['title']

        if currently_playing['tvshowid'] != -1:
            url = 'http://api.trakt.tv/show/episode/shouts.json/%s/%s/%s/%s' % (TRAKT_API_KEY, imdbnumber, currently_playing['season'], currently_playing['episode'])

        else:
            url = 'http://api.trakt.tv/movie/shouts.json/%s/%s' % (TRAKT_API_KEY, imdbnumber)

        result = urllib.urlopen(url).read()
        trakt['shouts'] = json.JSONDecoder().decode(result)

    return render_template('trakt.html', trakt=trakt)

@app.route('/xhr/currently_playing')
def xhr_currently_playing():
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    try:
        currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['title', 'season', 'episode', 'duration', 'showtitle'])['item']

    except:
        return jsonify({ 'playing': False })

    time = xbmc.Player.GetProperties(playerid=1, properties=['time', 'totaltime', 'position', 'percentage'])

    return render_template('currently_playing.html',
        currently_playing = currently_playing,
        time = time,
        current_time = format_time(time['time']),
        total_time = format_time(time['totaltime']),
        percentage_progress = int(time['percentage'])
    )

@app.route('/xhr/play_episode/<int:episode_id>')
def xhr_play_episode(episode_id):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    xbmc.VideoPlaylist.Clear()
    xbmc.VideoPlaylist.Add(episodeid=episode_id)
    xbmc.VideoPlaylist.Play()

    return jsonify({ 'success': True })

def format_time(time):
    formatted_time = ''

    if time['hours'] > 0:
        formatted_time += str(time['hours']) + ':'

        if time['minutes'] == 0:
            formatted_time += '00:'

    formatted_time += '%0*d' % (2, time['minutes']) + ':'
    formatted_time += '%0*d' % (2, time['seconds'])

    return formatted_time

if __name__ == '__main__':
    app.run(debug=True)
