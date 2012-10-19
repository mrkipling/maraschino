# -*- coding: utf-8 -*-
"""Ressources to use Maraschino on mobile devices"""

import jsonrpclib

from flask import render_template
from maraschino import app, logger

from maraschino.tools import *
from maraschino.noneditable import *

global sabnzbd_history_slots
sabnzbd_history_slots = None


@app.route('/mobile/')
@requires_auth
def mobile_index():
    xbmc = True
    available_modules = Module.query.order_by(Module.position)
    servers = XbmcServer.query.order_by(XbmcServer.position)

    if servers.count() == 0:
        xbmc = False

    return render_template('mobile/index.html',
        available_modules=available_modules,
        xbmc=xbmc,
        search=get_setting_value('search') == '1',
    )


from modules.recently_added import get_recently_added_episodes, get_recently_added_movies, \
                                   get_recently_added_albums, get_recent_xbmc_api_url


@app.route('/mobile/recent_episodes/')
@requires_auth
def recently_added_episodes():
    xbmc = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_server'))
    recently_added_episodes = get_recently_added_episodes(xbmc, mobile=True)

    return render_template('mobile/xbmc/recent_episodes.html',
        recently_added_episodes=recently_added_episodes[0],
        using_db=recently_added_episodes[1],
    )


@app.route('/mobile/recent_movies/')
@requires_auth
def recently_added_movies():
    xbmc = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_movies_server'))
    recently_added_movies = get_recently_added_movies(xbmc, mobile=True)

    return render_template('mobile/xbmc/recent_movies.html',
        recently_added_movies=recently_added_movies[0],
        using_db=recently_added_movies[1],
    )


@app.route('/mobile/recent_albums/')
@requires_auth
def recently_added_albums():
    xbmc = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_albums_server'))
    recently_added_albums = get_recently_added_albums(xbmc, mobile=True)

    return render_template('mobile/xbmc/recent_albums.html',
        recently_added_albums=recently_added_albums[0],
        using_db=recently_added_albums[1],
    )


@app.route('/mobile/xbmc/')
@requires_auth
def xbmc():
    servers = XbmcServer.query.order_by(XbmcServer.position)
    active_server = int(get_setting_value('active_server'))
    return render_template('mobile/xbmc/xbmc.html',
        servers=servers,
        active_server=active_server,
    )


@app.route('/mobile/movie_library/')
@requires_auth
def movie_library():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        sort = {'method': 'label', 'ignorearticle': True}
        movies = xbmc.VideoLibrary.GetMovies(sort=sort, properties=['title', 'rating', 'year', 'thumbnail', 'tagline', 'playcount'])['movies']

    except:
        logger.log('Mobile :: XBMC :: Could not retrieve movie library', 'WARNING')

    return render_template('mobile/xbmc/movie_library.html',
        movies=movies,
    )


@app.route('/mobile/tv_library/')
@requires_auth
def tv_library():
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        sort = {'method': 'label', 'ignorearticle': True}
        TV = xbmc.VideoLibrary.GetTVShows(sort=sort, properties=['thumbnail'])['tvshows']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve TV Shows: %s' % e, 'WARNING')

    return render_template('mobile/xbmc/tv_library.html',
        TV=TV,
    )


@app.route('/mobile/tvshow/<int:id>/')
@requires_auth
def tvshow(id):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        show = xbmc.VideoLibrary.GetSeasons(tvshowid=id, properties=['tvshowid', 'season', 'showtitle', 'playcount'])['seasons']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve TV Show [id: %i -  %s]' % (id, e), 'WARNING')

    return render_template('mobile/xbmc/tvshow.html',
        show=show,
    )


@app.route('/mobile/tvshow/<int:id>/<int:season>/')
@requires_auth
def season(id, season):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=id, season=season, sort={'method': 'episode'}, properties=['tvshowid', 'season', 'showtitle', 'playcount'])['episodes']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve TV Show [id: %i, season: %i -  %s]' % (id, season, e), 'WARNING')

    return render_template('mobile/xbmc/season.html',
        season=season,
        episodes=episodes,
    )


@app.route('/mobile/movie/<int:id>/info/')
@requires_auth
def movie_info(id):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        properties = ['thumbnail', 'rating', 'director', 'genre', 'plot', 'year', 'trailer']
        movie = xbmc.VideoLibrary.GetMovieDetails(movieid=id, properties=properties)['moviedetails']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve movie details [id: %i -  %s]' % (id, e), 'WARNING')

    return render_template('mobile/xbmc/movie-details.html',
        movie=movie
    )


@app.route('/mobile/tvshow/<int:id>/info/')
@requires_auth
def tvshow_info(id):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        properties = ['thumbnail', 'rating', 'studio', 'genre', 'plot']
        show = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=id, properties=properties)['tvshowdetails']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve TV Show details [id: %i -  %s]' % (id, e), 'WARNING')

    return render_template('mobile/xbmc/tvshow-details.html',
        show=show,
        banners=get_setting_value('library_use_bannerart') == '1'
    )

@app.route('/mobile/episode/<int:id>/info/')
@requires_auth
def episode_info(id):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        properties = ['thumbnail', 'firstaired', 'rating', 'plot', 'title']
        episode = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=id, properties=properties)['episodedetails']

    except Exception as e:
        logger.log('Mobile :: XBMC :: Could not retrieve episode details [id: %i -  %s]' % (id, e), 'WARNING')

    return render_template('mobile/xbmc/episode-details.html',
        episode=episode
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
    )


@app.route('/mobile/sickbeard/show/<int:id>/<int:season>/')
@requires_auth
def sickbeard_season(id, season):
    params = '/?cmd=show.seasons&tvdbid=%s&season=%s' % (id, season)

    try:
        sickbeard = sickbeard_api(params)

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']
            numbers = sorted(sickbeard, key=int)

    except Exception as e:
        logger.log('Could not retrieve sickbeard - %s]' % (e), 'WARNING')
        sickbeard = None

    return render_template('mobile/sickbeard/season.html',
        season_number=season,
        season=sickbeard,
        id=id,
        numbers=numbers,
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
    )


@app.route('/mobile/sickbeard/episode_options/<int:id>/<int:season>/<int:episode>/')
@requires_auth
def sickbeard_episode_options(id, season, episode):

    return render_template('mobile/sickbeard/episode_options.html',
        season_number=season,
        episode_number=episode,
        show_number=id,
    )


@app.route('/mobile/sickbeard/search/')
@app.route('/mobile/sickbeard/search/<query>/')
def sickbeard_search(query=None):
    from urllib2 import quote
    sickbeard = None
    if query:
        try:
            sickbeard = sickbeard_api('/?cmd=sb.searchtvdb&name=%s' % (quote(query)))
            sickbeard = sickbeard['data']['results']

        except Exception as e:
            logger.log('Mobile :: SickBeard :: Could not retrieve shows - %s]' % (e), 'WARNING')

    return render_template('mobile/sickbeard/search.html',
        results=sickbeard,
        query=query,
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
    )


@app.route('/mobile/couchpotato/history/')
@requires_auth
def couchpotato_history():
    unread = 0
    try:
        couchpotato = couchpotato_api('notification.list')
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


@app.route('/mobile/couchpotato/search/')
@app.route('/mobile/couchpotato/search/<query>/')
def couchpotato_search(query=None):
    couchpotato = None
    if query:
        try:
            couchpotato = couchpotato_api('movie.search', params='q=%s' % query)
            if couchpotato['success']:
                couchpotato = couchpotato['movie']

        except Exception as e:
            logger.log('Mobile :: CouchPotato :: Could not retrieve movie - %s]' % (e), 'WARNING')

    return render_template('mobile/couchpotato/search.html',
        results=couchpotato,
        query=query,
    )

from modules.headphones import *


@app.route('/mobile/headphones/')
@requires_auth
def headphones_wanted():
    albums = xhr_headphones_upcoming(mobile=True)
    upcoming = albums[0]
    wanted = albums[1]

    if upcoming == 'empty':
        upcoming = []

    if wanted == 'empty':
        wanted = []

    return render_template('mobile/headphones/wanted.html',
        upcoming=upcoming,
        wanted=wanted
    )


@app.route('/mobile/headphones/history/')
@requires_auth
def headphones_history():
    history = xhr_headphones_history(mobile=True)

    return render_template('mobile/headphones/history.html',
        history=history
    )


@app.route('/mobile/headphones/all/')
@requires_auth
def headphones_all():
    artists = xhr_headphones_artists(mobile=True)

    return render_template('mobile/headphones/all.html',
        artists=artists
    )


@app.route('/mobile/headphones/album/<albumid>/')
@requires_auth
def headphones_album(albumid):
    album = xhr_headphones_album(albumid, mobile=True)

    return render_template('mobile/headphones/album.html',
        album=album
    )


@app.route('/mobile/headphones/artist/<artistid>/')
@requires_auth
def headphones_artist(artistid):
    artist = xhr_headphones_artist(artistid, mobile=True)

    return render_template('mobile/headphones/artist.html',
        artist=artist
    )


@app.route('/mobile/headphones/search/<type>/')
@app.route('/mobile/headphones/search/<type>/<query>/')
def headphones_search(type, query=None):
    results = None
    if query:
        results = xhr_headphones_search(type, query, mobile=True)

    return render_template('mobile/headphones/search.html',
        type=type,
        results=results,
        query=query
    )


@app.route('/mobile/headphones/artist/action/<artistid>/<action>/')
def headphones_artist_action(artistid, action):
    result = xhr_headphones_artist_action(artistid, action, mobile=True)
    return result


@app.route('/mobile/headphones/album/<albumid>/<status>/')
def headphones_album_status(albumid, status):
    result = xhr_headphones_album_status(albumid, status, mobile=True)
    return result


from modules.sabnzbd import sabnzbd_api


@app.route('/mobile/sabnzbd/')
@requires_auth
def sabnzbd():
    try:
        sabnzbd = sabnzbd_api(method='queue')
        sabnzbd = sabnzbd['queue']
        download_speed = format_number(int((sabnzbd['kbpersec'])[:-3]) * 1024) + '/s'
        if sabnzbd['speedlimit']:
            sabnzbd['speedlimit'] = format_number(int((sabnzbd['speedlimit'])) * 1024) + '/s'

    except Exception as e:
        logger.log('Mobile :: SabNZBd+ :: Could not retrieve SabNZBd - %s]' % (e), 'WARNING')
        sabnzbd = None

    return render_template('mobile/sabnzbd/sabnzbd.html',
        queue=sabnzbd,
        download_speed=download_speed,
    )


@app.route('/mobile/sabnzbd/history/')
@requires_auth
def sabnzbd_history():
    global sabnzbd_history_slots
    try:
        sabnzbd = sabnzbd_api(method='history', params='&limit=50')
        sabnzbd = sabnzbd_history_slots = sabnzbd['history']

    except Exception as e:
        logger.log('Mobile :: SabNZBd+ :: Could not retrieve SabNZBd - %s]' % (e), 'WARNING')
        sabnzbd = None

    return render_template('mobile/sabnzbd/history.html',
        history=sabnzbd,
    )


@app.route('/mobile/sabnzbd/queue/<id>/')
@requires_auth
def sabnzbd_queue_item(id):
    try:
        sab = sabnzbd_api(method='queue')
        sab = sab['queue']

        for item in sab['slots']:
            if item['nzo_id'] == id:
                return render_template('mobile/sabnzbd/queue_item.html',
                    item=item,
                )
    except Exception as e:
        logger.log('Mobile :: SabNZBd+ :: Could not retrieve SabNZBd - %s]' % (e), 'WARNING')

    return sabnzbd()


@app.route('/mobile/sabnzbd/history/<id>/')
@requires_auth
def sabnzbd_history_item(id):
    global sabnzbd_history_slots
    if sabnzbd_history_slots:
        for item in sabnzbd_history_slots['slots']:
            if item['nzo_id'] == id:
                return render_template('mobile/sabnzbd/history_item.html',
                    item=item,
                )

        return sabnzbd_history()
    else:
        try:
            sabnzbd = sabnzbd_api(method='history', params='&limit=50')
            sabnzbd = sabnzbd_history_slots = sabnzbd['history']

            for item in sabnzbd_history_slots['slots']:
                if item['nzo_id'] == id:
                    return render_template('mobile/sabnzbd/history_item.html',
                        item=item,
                    )
        except Exception as e:
            logger.log('Mobile :: SabNZBd+ :: Could not retrieve SabNZBd - %s]' % (e), 'WARNING')
            sabnzbd = None

        return render_template('mobile/sabnzbd/history.html',
            history=sabnzbd,
        )


from modules.search import cat_newznab, cat_nzbmatrix, nzb_matrix, nzb_su


@app.route('/mobile/search/')
@app.route('/mobile/search/<site>/')
def search(site="nzbmatrix"):
    if site == 'nzb.su':
        categories = cat_newznab
    else:
        categories = cat_nzbmatrix

    return render_template('mobile/search.html',
        categories=categories,
    )


@app.route('/mobile/search/nzbmatrix/<query>/')
@app.route('/mobile/search/nzbmatrix/<query>/<cat>/')
def mobile_nzbmatrix(query, cat=None):

    return render_template('mobile/search.html',
        categories=cat_nzbmatrix,
        results=nzb_matrix(item=query, cat=cat, mobile=True)
    )


@app.route('/mobile/search/nzb.su/<query>/')
@app.route('/mobile/search/nzb.su/<query>/<cat>/')
def mobile_nzbsu(query, cat=None):

    return render_template('mobile/search.html',
        categories=cat_newznab,
        results=nzb_su(item=query, cat=cat, mobile=True)
    )
