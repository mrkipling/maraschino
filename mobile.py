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
        logger.log('Could not retrieve recently added episodes', 'WARNING')

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
        logger.log('Could not retrieve recently added movies', 'WARNING')

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
        logger.log('Could not retrieve recently added albums', 'WARNING')

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
        logger.log('Could not retrieve movie library', 'WARNING')

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
        logger.log('Could not retrieve TV Shows: %s' % e, 'WARNING')

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
        logger.log('Could not retrieve TV Show [id: %i -  %s]' % (id, e), 'WARNING')

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
        logger.log('Could not retrieve TV Show [id: %i, season: %i -  %s]' % (id, season, e), 'WARNING')

    return render_template('mobile/xbmc/season.html',
        season=season,
        episodes=episodes,
        webroot=maraschino.WEBROOT,
    )

from modules.sickbeard import sickbeard_api, get_pic


@app.route('/mobile/sickbeard/')
@requires_auth
def sickbeard():

    try:
        sickbeard = sickbeard_api('/?cmd=future&sort=date')

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']
            for time in sickbeard:
                for episode in sickbeard[time]:
                    episode['image'] = get_pic(episode['tvdbid'], 'banner')

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/coming_episodes.html',
        coming_episodes=sickbeard,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/sickbeard/all/')
@requires_auth
def sickbeard_all():

    try:
        sickbeard = sickbeard_api('/?cmd=shows&sort=name')

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']

            for show in sickbeard:
                sickbeard[show]['url'] = get_pic(sickbeard[show]['tvdbid'], 'banner')

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/all.html',
        shows=sickbeard,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/sickbeard/history/')
@requires_auth
def sickbeard_history():

    try:
        sickbeard = sickbeard_api('/?cmd=history&limit=30')

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/history.html',
        history=sickbeard,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/sickbeard/show/<int:id>/')
@requires_auth
def sickbeard_show(id):
    params = '/?cmd=show&tvdbid=%s' % id

    try:
        sickbeard = sickbeard_api(params)

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']
            sickbeard['tvdbid'] = id

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/show.html',
        show=sickbeard,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/sickbeard/show/<int:id>/<int:season>/')
@requires_auth
def sickbeard_season(id, season):
    params = '/?cmd=show.seasons&tvdbid=%s&season=%s' % (id, season)

    try:
        sickbeard = sickbeard_api(params)

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/season.html',
        season_number=season,
        season=sickbeard,
        id=id,
        webroot=maraschino.WEBROOT,
    )


@app.route('/mobile/sickbeard/show/<int:id>/<int:season>/<int:episode>/')
@requires_auth
def sickbeard_episode(id, season, episode):
    params = '/?cmd=episode&tvdbid=%s&season=%s&episode=%s&full_path=1' % (id, season, episode)

    try:
        sickbeard = sickbeard_api(params)

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/episode.html',
        season_number=season,
        episode_number=episode,
        episode=sickbeard,
        id=id,
        webroot=maraschino.WEBROOT,
    )
