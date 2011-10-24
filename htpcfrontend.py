from flask import Flask, jsonify, render_template, request
from settings import *

import jsonrpclib, math

app = Flask(__name__)

SERVER_ADDRESS = 'http://%s:%s@%s:%s/jsonrpc' % (SERVER['username'], SERVER['password'], SERVER['hostname'], SERVER['port'])

@app.route('/')
def index():
    return render_template('index.html',
        applications = APPLICATIONS,
        modules = MODULES
    )

@app.route('/xhr/recently_added')
def xhr_recently_added():
    xbmc = jsonrpclib.Server(SERVER_ADDRESS)
    recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(fields = ['title', 'season', 'episode', 'showtitle'])

    return render_template('recently_added.html',
        recently_added_episodes = recently_added_episodes['episodes'][:NUM_RECENT_EPISODES],
        server = SERVER
    )

@app.route('/xhr/currently_playing')
def xhr_currently_playing():
    xbmc = jsonrpclib.Server(SERVER_ADDRESS)

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
    xbmc = jsonrpclib.Server(SERVER_ADDRESS)
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
