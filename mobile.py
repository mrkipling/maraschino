# -*- coding: utf-8 -*-
"""Ressources to use Maraschino on mobile devices"""

import jsonrpclib

from flask import render_template
from maraschino import app, logger

from maraschino.tools import *
from maraschino.noneditable import *
import maraschino


@app.route('/mobile/')
@requires_auth
def mobile_index():
    return render_template('mobile/index.html', webroot=maraschino.WEBROOT)


@app.route('/mobile/recent_episodes/')
@requires_auth
def recently_added_episodes():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties=['title', 'season', 'episode', 'showtitle', 'playcount', 'thumbnail', 'firstaired'])['episodes']
        if get_setting_value('recently_added_watched_episodes') == '0':
            recently_added_episodes = [x for x in recently_added_episodes if not x['playcount']]

    except:
        logger.log('Mobile :: XBMC :: Could not retrieve recently added episodes', 'WARNING')

    return render_template('mobile/xbmc/recent_episodes.html',
        recently_added_episodes=recently_added_episodes,
        webroot=maraschino.WEBROOT
    )


@app.route('/mobile/recent_movies/')
@requires_auth
def recently_added_movies():

    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_movies = xbmc.VideoLibrary.GetRecentlyAddedMovies(properties=['title', 'rating', 'year', 'thumbnail', 'tagline', 'playcount'])['movies']
        if get_setting_value('recently_added_watched_movies') == '0':
            recently_added_movies = [x for x in recently_added_movies if not x['playcount']]

    except:
        logger.log('Mobile :: XBMC :: Could not retrieve recently added movies', 'WARNING')

    return render_template('mobile/xbmc/recent_movies.html',
        recently_added_movies=recently_added_movies,
        webroot=maraschino.WEBROOT
    )


@app.route('/mobile/recent_albums/')
@requires_auth
def recently_added_albums():

    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_albums = xbmc.AudioLibrary.GetRecentlyAddedAlbums(properties=['title', 'rating', 'thumbnail', 'artist'])['albums']

    except:
        logger.log('Mobile :: XBMC :: Could not retrieve recently added albums', 'WARNING')

    return render_template('mobile/xbmc/recent_albums.html',
        recently_added_albums=recently_added_albums,
        webroot=maraschino.WEBROOT
    )


@app.route('/mobile/xbmc/')
@requires_auth
def xbmc():
    return render_template('mobile/xbmc/xbmc.html',
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/movie_library/')
@requires_auth
def movie_library():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        movies = xbmc.VideoLibrary.GetMovies(properties=['title', 'rating', 'year', 'thumbnail', 'tagline', 'playcount'])['movies']

    except:
        logger.log('Mobile :: XBMC :: Could not retrieve movie library', 'WARNING')

    return render_template('mobile/xbmc/movie_library.html',
        movies=movies,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/tv_library/')
@requires_auth
def tv_library():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        TV = xbmc.VideoLibrary.GetTVShows(properties=['thumbnail'])['tvshows']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve TV Shows: %s' % e, 'WARNING')

    return render_template('mobile/xbmc/tv_library.html',
        TV=TV,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/tvshow/<int:id>/')
@requires_auth
def tvshow(id):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        show = xbmc.VideoLibrary.GetSeasons(tvshowid=id, properties=['tvshowid', 'season', 'showtitle', 'playcount'])['seasons']

    except Exception as e:
        logger.log('Mobile :: SickBeard :: Could not retrieve TV Show [id: %i -  %s]' % (id, e), 'WARNING')

    return render_template('mobile/xbmc/tvshow.html',
        show=show,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/tvshow/<int:id>/<int:season>/')
@requires_auth
def season(id, season):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=id, season=season, sort={'method': 'episode'}, properties=['tvshowid', 'season', 'showtitle', 'playcount'])['episodes']

    except Exception as e:
        logger.log('Mobile :: SickBeard :: Could not retrieve TV Show [id: %i, season: %i -  %s]' % (id, season, e), 'WARNING')

    return render_template('mobile/xbmc/season.html',
        season=season,
        episodes=episodes,
        webroot=maraschino.WEBROOT,
    )


from modules.couchpotato import couchpotato_api


@app.route('/mobile/couchpotato/')
@requires_auth
def couchpotato():
    try:
        couchpotato = couchpotato_api('movie.list', params=False)
        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except Exception as e:
        logger.log('Mobile :: CouchPotato :: Could not retrieve Couchpotato - %s]' % (e), 'WARNING')
        couchpotato = None

    return render_template('mobile/couchpotato/wanted.html',
        wanted=couchpotato,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/couchpotato/all/')
@requires_auth
def couchpotato_all():
    try:
        couchpotato = couchpotato_api('movie.list', params='status=done')
        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except Exception as e:
        logger.log('Mobile :: CouchPotato :: Could not retrieve Couchpotato - %s]' % (e), 'WARNING')
        couchpotato = None

    return render_template('mobile/couchpotato/all.html',
        all=couchpotato,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/couchpotato/history/')
@requires_auth
def couchpotato_history():
    unread = 0
    try:
        couchpotato = couchpotato_api('notification.list', params='limit_offset=50')
        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['notifications']
            for notification in couchpotato:
                if not notification['read']:
                    unread = unread + 1

    except Exception as e:
        logger.log('Mobile :: CouchPotato :: Could not retrieve Couchpotato - %s]' % (e), 'WARNING')
        couchpotato = None

    return render_template('mobile/couchpotato/history.html',
        history=couchpotato,
        unread=unread,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/couchpotato/movie/<id>/')
def couchpotato_movie(id):
    try:
        couchpotato = couchpotato_api('movie.get', 'id=%s' % id)
        if couchpotato['success']:
            couchpotato = couchpotato['movie']

    except Exception as e:
        logger.log('Mobile :: CouchPotato :: Could not retrieve movie - %s]' % (e), 'WARNING')

    return render_template('mobile/couchpotato/movie.html',
        movie=couchpotato,
    )
