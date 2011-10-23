from flask import Flask, render_template
from settings import *

import jsonrpclib

app = Flask(__name__)

@app.route('/')
def index():
    xbmc = jsonrpclib.Server(SERVER_ADDRESS)
    episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes()
    recently_added_episodes = []

    # tidy up filenames of recently added episodes

    for episode in episodes['episodes'][:NUM_RECENT_EPISODES]:
        filename = episode['file'].split('/').pop().replace('.', ' ')
        recently_added_episodes.append(filename)

    # currently playing

    #currently_playing = xbmc.VideoPlaylist.GetItems(id=1)
    #time = xbmc.VideoPlayer.GetTime()

    return render_template('index.html',
        recently_added_episodes = recently_added_episodes,
        applications = APPLICATIONS
    )

if __name__ == '__main__':
    app.run(debug=True)
