from flask import Flask, render_template
import jsonrpclib

from htpcfrontend import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/recently_added')
@requires_auth
def xhr_recently_added():
    return render_recently_added_episodes()

@app.route('/xhr/recently_added/<int:offset>')
@requires_auth
def xhr_recently_added_offset(offset):
    return render_recently_added_episodes(offset)

def render_recently_added_episodes(offset=0):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'lastplayed', 'thumbnail'])
    vfs_url = '%s/vfs/' % (SAFE_SERVER_ADDRESS)

    NUM_RECENT_EPISODES = int(get_setting('num_recent_episodes').value)

    return render_template('recently_added.html',
        recently_added_episodes = recently_added_episodes['episodes'][offset:NUM_RECENT_EPISODES + offset],
        vfs_url = vfs_url,
        offset = offset,
    )
