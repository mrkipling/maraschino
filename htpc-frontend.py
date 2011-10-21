from flask import Flask, render_template
from settings import *

import jsonrpclib

app = Flask(__name__)

@app.route('/')
def index():
    xbmc = jsonrpclib.Server(SERVER_ADDRESS)
    episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes()

    return render_template('index.html', recently_added_episodes = episodes)

if __name__ == '__main__':
    app.run(debug=True)
