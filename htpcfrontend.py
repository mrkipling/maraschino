from flask import Flask, jsonify, render_template, request
from settings import *

import jsonrpclib

app = Flask(__name__)

SERVER_ADDRESS = 'http://%s:%s@%s:%s/jsonrpc' % (SERVER['username'], SERVER['password'], SERVER['hostname'], SERVER['port'])

@app.route('/')
def index():
    return render_template('index.html',
        applications = APPLICATIONS,
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
def currently_playing():
    xbmc = jsonrpclib.Server(SERVER_ADDRESS)

    try:
        time = xbmc.VideoPlayer.GetTime()
        print time

    except:
        return jsonify({ 'playing': False })

    currently_playing = xbmc.VideoPlaylist.GetItems(fields = ['title', 'season', 'episode', 'duration', 'showtitle'], id=1)
    print currently_playing

    return render_template('currently_playing.html')

if __name__ == '__main__':
    app.run(debug=True)
