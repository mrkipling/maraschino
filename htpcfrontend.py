from flask import Flask, render_template
from settings import *

import jsonrpclib

app = Flask(__name__)

@app.route('/')
def index():
    xbmc = jsonrpclib.Server('http://%s:%s@%s:%s/jsonrpc' % (SERVER['username'], SERVER['password'], SERVER['hostname'], SERVER['port']))
    episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes()
    recently_added_episodes = []

    # tidy up filenames of recently added episodes
    for episode in episodes['episodes'][:NUM_RECENT_EPISODES]:
        filename = episode['file'].split('/').pop().replace('.', ' ')
        recently_added_episodes.append(filename)

    return render_template('index.html',
        recently_added_episodes = recently_added_episodes,
        applications = APPLICATIONS,
        server = SERVER
    )

if __name__ == '__main__':
    app.run(debug=True)
