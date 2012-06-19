import jsonrpclib

from flask import Flask, render_template
from maraschino import app, logger

from maraschino.tools import *
from maraschino.noneditable import *
from modules.recently_added import get_recently_added_episodes
import maraschino

@app.route('/mobile/temp_index_url')
@requires_auth
def mobile_index():
    return render_template('mobile/index.html')

@app.route('/mobile')
@requires_auth
def recently_added_episodes():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'playcount', 'thumbnail', 'firstaired'])['episodes']

        for episode in recently_added_episodes:
            episode['thumbnail'] = maraschino.WEBROOT + '/xhr/vfs_proxy/' + strip_special(episode['thumbnail'])

    except:
        logger.log('Could not retrieve recently added episodes' , 'WARNING')

    return render_template('mobile/recent_episodes.html',
        recently_added_episodes = recently_added_episodes,
        webroot = maraschino.WEBROOT,
    )
