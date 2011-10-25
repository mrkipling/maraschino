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
        show_currently_playing = SHOW_CURRENTLY_PLAYING
    )

@app.route('/xhr/applications')
def xhr_applications():
    return render_template('applications.html',
        applications = APPLICATIONS
    )

@app.route('/xhr/recently_added')
def xhr_recently_added():
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(fields = ['title', 'season', 'episode', 'showtitle', 'lastplayed'])

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

    url = 'http://api.trakt.tv/user/watching.json/%s/%s' % (TRAKT_API_KEY, TRAKT_USERNAME)
    result = urllib.urlopen(url).read()
    trakt['watching'] = json.JSONDecoder().decode(result)

    if trakt['watching']:
        if trakt['watching']['type'] == 'episode':
            url = 'http://api.trakt.tv/show/episode/shouts.json/%s/%s/%s/%s' % (TRAKT_API_KEY, trakt['watching']['show']['tvdb_id'], trakt['watching']['episode']['season'],trakt['watching']['episode']['number'])

        else:
            url = 'http://api.trakt.tv/movie/shouts.json/%s/%s' % (TRAKT_API_KEY, trakt['watching']['movie']['imdb_id'])

        result = urllib.urlopen(url).read()
        trakt['shouts'] = json.JSONDecoder().decode(result)

    return render_template('trakt.html', trakt=trakt)

@app.route('/xhr/currently_playing')
def xhr_currently_playing():
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    try:
        time = xbmc.VideoPlayer.GetTime()

    except:
        return jsonify({ 'playing': False })

    currently_playing = xbmc.VideoPlaylist.GetItems(fields = ['title', 'season', 'episode', 'duration', 'showtitle'], id=1)

    return render_template('currently_playing.html',
        currently_playing = currently_playing['items'][0],
        current_time = format_time(time['time']),
        total_time = format_time(time['total']),
        percentage_progress = int((float(time['time']) / float(time['total'])) * 100)
    )

@app.route('/xhr/play_episode/<int:episode_id>')
def xhr_play_episode(episode_id):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    xbmc.VideoPlaylist.Clear()
    xbmc.VideoPlaylist.Add(episodeid=episode_id)
    xbmc.VideoPlaylist.Play()

    return jsonify({ 'success': True })

def format_time(total):
    total_mins = int(math.floor(total / 60))
    total_secs = '%0*d' % (2, int(total - (total_mins * 60)))

    total_hours = int(math.floor(total_mins / 60))
    total_mins = total_mins - (total_hours * 60)

    mins_secs = '%s:%s' % (total_mins, total_secs)

    if total_hours > 0:
        return '%s:%s' % (total_hours, mins_secs)

    return mins_secs

if __name__ == '__main__':
    app.run(debug=True)
