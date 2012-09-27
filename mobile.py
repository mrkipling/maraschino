# -*- coding: utf-8 -*-
"""Ressources to use Maraschino on mobile devices"""

import jsonrpclib

from flask import render_template
from maraschino import app, logger

from maraschino.tools import *
from maraschino.noneditable import *
import maraschino


@app.route('/mobile/')
@app.route('/mobile/temp_index_url')
@requires_auth
def mobile_index():
    return render_template('mobile/index.html')


@app.route('/mobile/recent_episodes/')
@requires_auth
def recently_added_episodes():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties=['title', 'season', 'episode', 'showtitle', 'playcount', 'thumbnail', 'firstaired'])['episodes']

    except:
        logger.log('Could not retrieve recently added episodes', 'WARNING')

    return render_template('mobile/recent_episodes.html',
        recently_added_episodes=recently_added_episodes,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/recent_movies/')
@requires_auth
def recently_added_movies():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_movies = xbmc.VideoLibrary.GetRecentlyAddedMovies(properties=['title', 'rating', 'year', 'thumbnail', 'tagline', 'playcount'])['movies']
        print recently_added_movies

    except:
        logger.log('Could not retrieve recently added movies', 'WARNING')

    return render_template('mobile/recent_movies.html',
        recently_added_movies=recently_added_movies,
        webroot=maraschino.WEBROOT,
    )
