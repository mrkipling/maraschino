# -*- coding: utf-8 -*-
"""Simple mode"""

import jsonrpclib

from flask import render_template
from maraschino import app, logger

from maraschino.tools import *
from maraschino.noneditable import *

from modules.recently_added import get_recently_added_episodes, get_recently_added_movies, \
                                   get_recently_added_albums, get_recent_xbmc_api_url

@app.route('/simple/')
@requires_auth
def simple_index():
    # recently added episodes
    xbmc_episodes = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_server'))
    recently_added_episodes = get_recently_added_episodes(xbmc_episodes, extra_info=True, get_all=True)

    xbmc_movies = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_movies_server'))
    recently_added_movies = get_recently_added_movies(xbmc_movies)

    return render_template('simple/index.html',
        recently_added_episodes = recently_added_episodes[0],
        using_db_episodes = recently_added_episodes[1],
        recently_added_movies = recently_added_movies[0],
        using_db_movies = recently_added_movies[1],
    )
