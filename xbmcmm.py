from flask import render_template, request, json, jsonify
from maraschino import app, logger
from maraschino.tools import requires_auth, get_setting_value, create_dir, download_image
from maraschino.noneditable import server_api_address
from maraschino.models import XbmcServer
from jinja2.filters import FILTERS
from tvdb_api import tvdb_api, tvdb_exceptions
from threading import Thread
import os
import urllib
import urllib2
import string
import maraschino
import jsonrpclib
import time
xbmc_error = 'There was a problem connecting to the XBMC server'


def xbmcmm_except(e):
    logger.log('XBMCMM :: EXCEPTION -- %s' % e, 'DEBUG')


def get_active_server():
    active_server = get_setting_value('active_server')
    if active_server and active_server.isdigit():
        active_server = int(active_server)

    return active_server


@app.route('/xbmcmm/')
@app.route('/xbmcmm/<type>/')
@requires_auth
def xbmcmm(type='movies'):
    message = ''
    media_list = ''

    try:
        media_list = xbmc_media_list(type)
    except Exception as e:
        xbmcmm_except(e)
        message = xbmc_error

    if not media_list:
        message = 'No XBMC server defined.'
        logger.log(message, 'ERROR')
        message = message

    return render_template('/xbmcmm/base.html',
        servers=XbmcServer.query.order_by(XbmcServer.position),
        active_server=get_active_server(),
        webroot=maraschino.WEBROOT,
        media_list=media_list,
        type=type,
        message=message
    )


### Get media list ###
def xbmc_media_list(type):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
    except Exception as e:
        xbmcmm_except(e)
        return False

    sort = {'method': 'label', 'ignorearticle': True}

    if type == 'movies':
        return xbmc.VideoLibrary.GetMovies(sort=sort)
    elif type == 'moviesets':
        return xbmc.VideoLibrary.GetMovieSets(sort=sort)
    else:
        return xbmc.VideoLibrary.GetTVShows(sort=sort)


### Get media details ###
@app.route('/xhr/xbmcmm/movie/<int:id>/')
@requires_auth
def xhr_xbmcmm_movie_details(id):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        item = xbmc.VideoLibrary.GetMovieDetails(movieid=id, properties=movie_properties)
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)

    try:
        item['sets'] = xbmc.VideoLibrary.GetMovieSets(sort={'method': 'label'})['sets']
    except:
        item['sets'] = []

    item['moviedetails'] = lst2str(item['moviedetails'])

    return render_template('/xbmcmm/movie.html',
        item=item
    )


@app.route('/xhr/xbmcmm/movieset/<int:id>/')
@requires_auth
def xhr_xbmcmm_movieset_details(id):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if id == 0:
            movieset = {'setid': 0, 'label': 'New Set', 'movies': []}
        else:
            movieset = xbmc.VideoLibrary.GetMovieSetDetails(setid=id)['setdetails']
        movies = xbmc.VideoLibrary.GetMovies(
            sort={'method': 'label', 'ignorearticle': True},
            properties=['set']
        )['movies']

    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)

    return render_template('/xbmcmm/movieset.html',
        movieset=movieset,
        movies=movies
    )


@app.route('/xhr/xbmcmm/tvshow/<int:id>/')
@requires_auth
def xhr_xbmcmm_show_details(id):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        item = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=id, properties=show_properties)
        try:
            seasons = xbmc.VideoLibrary.GetSeasons(tvshowid=id, sort={'method': 'label'}, properties=season_properties)['seasons']
        except:
            seasons = {}
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)

    item['seasons'] = seasons

    item['tvshowdetails'] = lst2str(item['tvshowdetails'])

    return render_template('/xbmcmm/tvshow-base.html',
        item=item
    )


@app.route('/xhr/xbmcmm/tvshow/<int:id>/season/<int:season>')
@requires_auth
def xhr_xbmcmm_season_details(id, season):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        item = xbmc.VideoLibrary.GetEpisodes(
            tvshowid=id,
            season=season,
            sort={'method': 'episode'},
            properties=['tvshowid', 'season', 'showtitle', 'episode']
        )
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)

    return render_template('/xbmcmm/tvshow-season.html',
        item=item
    )


@app.route('/xhr/xbmcmm/episode/<int:id>/')
@requires_auth
def xhr_xbmcmm_episode_details(id):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        item = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=id, properties=episode_properties)['episodedetails']
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)

    return render_template('/xbmcmm/tvshow-episode.html',
        episode=lst2str(item)
    )


### Get genres ###
@app.route('/xhr/xbmcmm_genres/<file_type>/<media>/', methods=['POST'])
@requires_auth
def xhr_xbmcmm_get_genres(file_type, media):
    xbmc = jsonrpclib.Server(server_api_address())

    genres = video_genres

    try:
        xbmc_genres = xbmc.VideoLibrary.GetGenres(type=media)['genres']
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)

    for genre in xbmc_genres:
        if not genre['label'] in genres:
            genres.append(genre['label'])

    existing = [x.strip() for x in request.form['exist'].split('/') if x != '']

    return render_template('xbmcmm/modals/genres.html',
        existing=existing,
        genres=sorted(genres)
    )


### Get tags ###
@app.route('/xhr/xbmcmm_tags/<media>/', methods=['POST'])
@requires_auth
def xhr_xbmcmm_get_tags(media):
    xbmc = jsonrpclib.Server(server_api_address())
    tags = []
    if media == 'movie':
        media_list = xbmc.VideoLibrary.GetMovies(properties=['tag'])['movies']
    elif media == 'tvshow':
        media_list = xbmc.VideoLibrary.GetTVShows(properties=['tag'])['tvshows']

    for x in media_list:
        if x['tag']:
            for y in x['tag']:
                if y not in tags:
                    tags.append(y)

    existing = [x.strip() for x in request.form['exist'].split('/') if x != '']

    return render_template('xbmcmm/modals/tags.html',
        existing=existing,
        tags=sorted(tags)
    )


### Remove library item ###
@app.route('/xhr/xbmcmm/remove/<media>/<int:id>/')
def xhr_xbmcmm_remove(media, id):
    return render_template('xbmcmm/modals/confirm.html',
        remove=True,
        media=media,
        id=id
    )


### Modify set modal ###
@app.route('/xhr/xbmcmm/modify_set_modal/<action>/')
def xhr_xbmcmm_modify_set_modal(action):
    return render_template('xbmcmm/modals/modify_set.html',
        action=action
    )


### Modify set ###
@app.route('/xhr/xbmcmm/modify_set/<action>/<int:movieid>', methods=['GET'])
@app.route('/xhr/xbmcmm/modify_set/<action>/', methods=['POST'])
def xhr_xbmcmm_modify_set(action, movieid=None):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if request.method == 'GET':
            params = {'movieid': movieid}

            if action == 'add':
                params['set'] = request.args['setlabel']
            else:
                params['set'] = ''

            xbmc.VideoLibrary.SetMovieDetails(**params)

        else:
            for movieid in request.form.getlist('movies[]'):
                params = {'movieid': int(movieid)}

                if action == 'rename':
                    params['set'] = request.form['setlabel']
                else:
                    params['set'] = ''

                xbmc.VideoLibrary.SetMovieDetails(**params)

        if action == 'add' or action == 'rename':
            movies = xbmc.VideoLibrary.GetMovies(properties=['set', 'setid'])['movies']
            setid = [x['setid'] for x in movies if x['set'] == params['set']][0]

            return jsonify(success=True, setid=setid)

        return jsonify(success=True)

    except Exception as e:
        xbmcmm_except(e)
        return jsonify(failed=True)


### Convert URL to XBMC URL ###
def url2xbmc_img(url):
    if not url.lower().startswith('image://'):
        return 'image://' + urllib.quote(url, '')
    else:
        return url


### Export library ###
@app.route('/xhr/xbmcmm/export/<media>/')
def xhr_xbmcmm_export(media):
    return render_template('xbmcmm/modals/export.html',
        media=media,
        filesystem=browse_filesystem()
    )


@app.route('/xhr/xbmcmm/export/filesystem/', methods=['POST'])
@requires_auth
def xhr_xbmcmm_export_filesystem():
    try:
        path = request.form['path']
        path = urllib.unquote(path.encode('ascii')).decode('utf-8')
        filesystem = browse_filesystem(path=path)
    except:
        filesystem = browse_filesystem()

    return render_template('xbmcmm/modals/export-filesystem.html',
        filesystem=filesystem
    )


### Set movie ###
@app.route('/xhr/xbmcmm/movie/set/<int:movieid>/', methods=['POST'])
@requires_auth
def xhr_xbmcmm_set_movie(movieid):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        params = {
            'movieid': movieid,
            'title': request.form['title'],
            'originaltitle': request.form['originaltitle'],
            'sorttitle': request.form['sorttitle'],
            'plot': request.form['plot'],
            'year': int(request.form['year']),
            'rating': float(request.form['rating']),
            'genre': str2lst(request.form['genre']),
            'director': str2lst(request.form['director']),
            'mpaa': request.form['mpaa'],
            'studio': str2lst(request.form['studio']),
            'tagline': request.form['tagline'],
            'set': request.form['set'],
            'tag': str2lst(request.form['tag']),
            'trailer': request.form['trailer'],
            'writer': str2lst(request.form['writer']),
            'runtime': int(request.form['runtime']),
            'votes': request.form['votes'],
        }

        # Only set artwork if it exists
        art = {}
        if request.form['poster']:
            art['poster'] = request.form['poster']
        if request.form['fanart']:
            art['fanart'] = request.form['fanart']
        if request.form['banner']:
            art['banner'] = request.form['banner']
        if request.form['discart']:
            art['discart'] = request.form['discart']
        if request.form['clearart']:
            art['clearart'] = request.form['clearart']
        if request.form['clearlogo']:
            art['clearlogo'] = request.form['clearlogo']

        if art:
            params['art'] = art

        # Check playcount
        if 'playcount' in request.form:
            params['playcount'] = 1
        else:
            params['playcount'] = 0

    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error='Invalid parameters.')

    try:
        xbmc.VideoLibrary.SetMovieDetails(**params)
        return jsonify(status='Movie details successfully changed.')

    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)


### Set show ###
@app.route('/xhr/xbmcmm/tvshow/set/<int:tvshowid>/', methods=['POST'])
@requires_auth
def xhr_xbmcmm_set_tvshow(tvshowid):
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        params = {
            'tvshowid': tvshowid,
            'title': request.form['title'],
            'originaltitle': request.form['originaltitle'],
            'sorttitle': request.form['sorttitle'],
            'plot': request.form['plot'],
            'rating': float(request.form['rating']),
            'genre': str2lst(request.form['genre']),
            'premiered': request.form['premiered'],
            'mpaa': request.form['mpaa'],
            'studio': str2lst(request.form['studio']),
            'votes': request.form['votes'],
            'tag': str2lst(request.form['tag']),
        }

        # Only set artwork if it exists
        art = {}
        if request.form['poster']:
            art['poster'] = request.form['poster']
        if request.form['fanart']:
            art['fanart'] = request.form['fanart']
        if request.form['banner']:
            art['banner'] = request.form['banner']
        if request.form['clearart']:
            art['clearart'] = request.form['clearart']
        if request.form['clearlogo']:
            art['clearlogo'] = request.form['clearlogo']
        if request.form['characterart']:
            art['characterart'] = request.form['characterart']
        if request.form['landscape']:
            art['landscape'] = request.form['landscape']

        if art:
            params['art'] = art

    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error='Invalid parameters.')

    try:
        xbmc.VideoLibrary.SetTVShowDetails(**params)
        return jsonify(status='TV show details successfully changed.')
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)


### Set episode ###
@app.route('/xhr/xbmcmm/episode/set/<int:episodeid>/', methods=['POST'])
@requires_auth
def xhr_xbmcmm_set_episode(episodeid):
    xbmc = jsonrpclib.Server(server_api_address())
    print 'here'
    try:
        params = {
            'episodeid': episodeid,
            'title': request.form['title'],
            'plot': request.form['plot'],
            'firstaired': request.form['firstaired'],
            'rating': float(request.form['rating']),
            'votes': request.form['votes'],
            'director': str2lst(request.form['director']),
            'writer': str2lst(request.form['writer']),
        }

        # Only set artwork if it exists
        if request.form['thumb']:
            params['art'] = {'thumb': request.form['thumb']}

        # Check playcount
        if 'playcount' in request.form:
            params['playcount'] = 1
        else:
            params['playcount'] = 0

    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error='Invalid parameters.')

    try:
        xbmc.VideoLibrary.SetEpisodeDetails(**params)
        return jsonify(status='Episode details successfully changed.')
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error=xbmc_error)


### Image URL ###
@app.route('/xhr/xbmcmm_url/<type>/')
@requires_auth
def xhr_xbmcmm_url(type):
    return render_template('xbmcmm/modals/url.html', type=type)

### fanart.tv ###
fanarttv_apikey = '560fee4c7ffe8f503e0f9474b8adb3e6'


def fanarttv_url(media, type, id, sort=1, limit=2):
    return 'http://fanart.tv/webservice/%s/%s/%s/json/%s/%s/%s/' % (media, fanarttv_apikey, id, type, sort, limit)


def fanarttv_api(url, dev=False):
    request = urllib2.Request(url)
    data = urllib2.urlopen(request).read()
    data = json.JSONDecoder().decode(data)

    if dev:
        print url
        print json.dumps(data, sort_keys=True, indent=4)

    return data


@app.route('/xhr/fanarttv/<media>/<type>/<id>/')
@requires_auth
def xhr_xbmcmm_fanarttv(media, type, id):
    logger.log('XBMCMM :: Fething %s images for %s: %s from fanart.tv' % (type, media, id), 'INFO')

    fanarttv_media = {
        'movie': {
            'banner': 'moviebanner',
            'fanart': 'moviebackground',
            'discart': 'moviedisc',
            'clearlogo': 'movielogo',
            'clearart': 'movieart'
        },
        'series': {
            'banner': 'tvbanner',
            'fanart': 'showbackground',
            'clearlogo': 'clearlogo',
            'clearart': 'clearart',
            'landscape': 'tvthumb',
            'characterart': 'characterart'
        }
    }

    img_type = fanarttv_media[media][type]

    try:
        fanarttv = fanarttv_api(fanarttv_url(media, img_type, id), True)
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error='Failed to retrieve images from fanart.tv')

    if media == 'series':
        media = 'show'

    images = {}

    try:
        for item in fanarttv[fanarttv.keys()[0]][img_type]:
            url = item['url']

            cache_params = {
                'image': url + '/preview',
                'media_type': media + 's',
                'img_type': type,
                media + '_name': id,
                'fanarttv': True
            }

            images[str(len(images))] = {
                'url': url,
                'local': xbmcmm_image_cache(**cache_params)
            }
    except Exception as e:
        xbmcmm_except(e)

    while maraschino.THREADS:
        time.sleep(1)

    return render_template('xbmcmm/modals/fanarttv.html',
        images=images,
        type=type
    )


### TMDB ###
tmdb_apikey = '54fe2d0eef90c6257f746dddb7df8826'


def tmdb_api(id, param='', dev=False):
    url = 'http://api.themoviedb.org/3/movie/' + id
    url += param
    url += '?api_key=' + tmdb_apikey
    request = urllib2.Request(url)
    request.add_header("Accept", "application/json")
    data = urllib2.urlopen(request).read()
    data = json.JSONDecoder().decode(data)

    if dev:
        print url
        print json.dumps(data, sort_keys=True, indent=4)

    return data


@app.route('/xhr/tmdb/<id>/')
@requires_auth
def xhr_xbmcmm_tmdb_info(id):
    logger.log('XBMCMM :: Fething information for movie: %s from TMDB' % id, 'INFO')

    try:
        movie = tmdb_api(id)
        casts = tmdb_api(id, '/casts')
        releases = tmdb_api(id, '/releases')
        trailers = tmdb_api(id, '/trailers')
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error='Failed to retrieve movie information from TMDB')

    if movie['genres']:
        genres = ''
        for genre in movie['genres']:
            genres += genre['name'] + ' / '
        movie['genres'] = genres[:-3]

    if movie['production_companies']:
        companies = ''
        for company in movie['production_companies']:
            companies += company['name'] + ' / '
        movie['production_companies'] = companies[:-3]

    if casts['crew']:
        directors = ''
        writers = ''
        for person in casts['crew']:
            if person['job'].lower() == 'director':
                directors += person['name'] + ' / '
            if person['department'].lower() == 'writing':
                writers += person['name'] + ' / '

        if directors:
            movie['director'] = directors[:-3]
        if writers:
            movie['writer'] = writers[:-3]

    if releases:
        for release in releases['countries']:
            if release['iso_3166_1'].lower() == 'us':
                movie['mpaa'] = release['certification']

    if trailers:
        if trailers['youtube']:
            movie['trailer'] = trailers['youtube'][0]['source']

    return render_template('xbmcmm/modals/tmdb_info.html',
        movie=movie
    )


@app.route('/xhr/tmdb/images/<type>/<id>/')
@requires_auth
def xhr_xbmcmm_tmdb_images(type, id):
    logger.log('XBMCMM :: Fething %s images for movie: %s from TMDB' % (type, id), 'INFO')

    images = {'fanart': {}, 'poster': {}}
    base = 'http://cf2.imgobject.com/t/p/'

    try:
        tmdb = tmdb_api(id, '/images')
    except Exception as e:
        xbmcmm_except(e)
        return jsonify(error='Failed to retrieve images from TMDB')

    if type == 'fanart':
        if tmdb['backdrops']:
            for fanart in tmdb['backdrops']:
                url = base + 'original' + fanart['file_path']
                thumb_url = base + 'w185' + fanart['file_path']
                images['fanart']['image' + str(len(images['fanart']))] = {
                    'url': url,
                    'local': xbmcmm_image_cache(thumb_url, 'movies', 'fanart', movie_name=id)
                }
    else:
        if tmdb['posters']:
            for poster in tmdb['posters']:
                url = base + 'original' + poster['file_path']
                thumb_url = base + 'w185' + poster['file_path']
                images['poster']['image' + str(len(images['poster']))] = {
                    'url': url,
                    'local': xbmcmm_image_cache(thumb_url, 'movies', 'posters', movie_name=id)
                }

    while maraschino.THREADS:
        time.sleep(1)

    return render_template('xbmcmm/modals/tmdb_images.html',
        images=images,
        type=type
    )


### TVDB ###
tvdb_apikey = 'F437CB7A56AE5209'


class maraUI(tvdb_api.BaseUI):
    global tvdb_show_list

    def selectSeries(self, shows):
        '''This is not a perfect solution, but it works..'''
        global tvdb_show_list
        tvdb_show_list = shows
        return shows[0]


def tvdb_show_search(show_name):
    t = tvdb_api.Tvdb(apikey=tvdb_apikey, custom_ui=maraUI)
    global tvdb_show_list
    try:
        t[show_name]
        shows = tvdb_show_list
    except tvdb_exceptions.tvdb_shownotfound:
        logger.log('Unable to find' + show_name + 'on TVDB', 'ERROR')
        return []
    except tvdb_exceptions.tvdb_error:
        logger.log('TVDB :: Cannot connect to TVDB', 'ERROR')
        return []
    return shows


def tvdb_str2list(show=None, episode=None):
    def split_var(var):
        return ' / '.join([x for x in var.split('|') if x])

    if show:
        if show['genre']:
            show['genre'] = split_var(show['genre'])
        return lst2str(show)
    else:
        if episode['writer']:
            episode['writer'] = split_var(episode['writer'])
        if episode['director']:
            episode['director'] = split_var(episode['director'])
        return lst2str(episode)


@app.route('/xhr/tvdb_show/<show_name>/')
@app.route('/xhr/tvdb_show/<show_name>/<id>/')
@requires_auth
def xhr_tvdb(show_name, id=None):
    args = request.args

    tvdb_params = {'apikey': tvdb_apikey}
    render_params = {'show_name': show_name}

    if args:
        tvdb_params['banners'] = True
        render_params['img_type'] = args['images']
        render_params['template'] = 'xbmcmm/modals/tvdb_images.html'

    t = tvdb_api.Tvdb(**tvdb_params)

    if id:
        if id.isdigit():
            logger.log('TVDB :: Grabbing show info based on TVBD ID', 'INFO')

            try:
                show = t[int(id)].data
            except tvdb_exceptions.tvdb_shownotfound:
                return tvdb_except('notfound', show_name)

            except tvdb_exceptions.tvdb_error:
                return tvdb_except('noconnect', show_name)

            if args:
                tvdb_show_image_cache(show, args['images'])
            render_params['show'] = tvdb_str2list(show=show)
            return render_tvdb(**render_params)

        elif id.startswith('tt'):
            logger.log('TVDB :: Grabbing show info based on IMDB ID', 'INFO')

            try:
                show = t[show_name].data
            except tvdb_exceptions.tvdb_shownotfound:
                return tvdb_except('notfound', show_name)

            except tvdb_exceptions.tvdb_error:
                return tvdb_except('noconnect', show_name)

            if show['imdb_id'] and id == show['imdb_id']:
                logger.log('TVDB :: Found IMDB ID match', 'INFO')

                render_params['show'] = tvdb_str2list(show=show)
                return render_tvdb(**render_params)

    logger.log('TVDB :: No ID supplied, or ID does not match title. Searching using title', 'WARNING')
    shows = tvdb_show_search(show_name)
    if not shows:
        return tvdb_except('notfound', show_name)

    render_params['shows'] = shows
    render_params['template'] = 'xbmcmm/modals/tvdb_info.html'
    return render_tvdb(**render_params)


@app.route('/xhr/tvdb_episode/<int:tvshowid>/<int:season>/<int:episode_number>/')
@requires_auth
def xhr_tvdb_episode(tvshowid, season, episode_number):
    xbmc = jsonrpclib.Server(server_api_address())
    t = tvdb_api.Tvdb(apikey=tvdb_apikey)

    show = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=tvshowid, properties=['imdbnumber'])['tvshowdetails']

    if show['imdbnumber'] and show['imdbnumber'].isdigit():
        logger.log('TVDB :: Grabbing episode info based on TVBD ID', 'INFO')
        try:
            episode = t[int(show['imdbnumber'])][season][episode_number]
        except tvdb_exceptions.tvdb_shownotfound:
            return tvdb_except('notfound', show['label'])

        except tvdb_exceptions.tvdb_error:
            return tvdb_except('noconnect', show['label'])

    else:
        logger.log('TVDB :: No TVDB ID supplied. Searching using title', 'WARNING')
        try:
            episode = t[show['label']][season][episode_number]
        except tvdb_exceptions.tvdb_shownotfound:
            return tvdb_except('notfound', show['label'])

        except tvdb_exceptions.tvdb_error:
            return tvdb_except('noconnect', show['label'])

    title = '%s - %02dx%02d' % (show['label'], season, episode_number)

    return render_template('xbmcmm/modals/tvdb_episode_info.html',
        title=title,
        episode=tvdb_str2list(episode=episode)
    )


def tvdb_show_image_cache(show, img_type):
    '''
    Navigates show returned from tvdb and pulls out
    all the image urls to be sent to cache.
    '''
    show_name = show['id']

    if img_type == 'poster' and show['_banners']['poster']:  # Posters
        for size in show['_banners']['poster']:
            for image in show['_banners']['poster'][str(size)]:
                url = show['_banners']['poster'][str(size)][str(image)]['_bannerpath']
                show['_banners']['poster'][str(size)][str(image)]['localpath'] = xbmcmm_image_cache(url, 'shows', 'posters', show_name=show_name)

    elif img_type == 'banner' and show['_banners']['series']:  # Banners
        for ban_type in show['_banners']['series']:
            for image in show['_banners']['series'][ban_type]:
                url = show['_banners']['series'][ban_type][str(image)]['_bannerpath']
                show['_banners']['series'][ban_type][str(image)]['localpath'] = xbmcmm_image_cache(url, 'shows', 'banners', show_name=show_name)

    else:  # Fanart
        if show['_banners']['fanart']:
            for size in show['_banners']['fanart']:
                for image in show['_banners']['fanart'][str(size)]:
                    url = show['_banners']['fanart'][str(size)][image]['_thumbnailpath']
                    show['_banners']['fanart'][str(size)][str(image)]['localpath'] = xbmcmm_image_cache(url, 'shows', 'fanart', show_name=show_name)

    while maraschino.THREADS:
        time.sleep(1)
    return show


def tvdb_except(e_type, show_name):
    if e_type == 'notfound':
        logger.log('TVDB :: Unable to find ' + show_name + ' on TVDB', 'ERROR')
        return render_tvdb(
            show_name=show_name,
            message='Unable to find ' + show_name + ' on TVDB',
        )

    elif e_type == 'noconnect':
        logger.log('TVDB :: Cannot connect to TVDB', 'ERROR')
        return render_tvdb(
            show_name=show_name,
            message='Cannot connect to TVDB',
        )


def render_tvdb(
    template='xbmcmm/modals/tvdb_info.html',
    shows=False,
    show=False,
    show_name='',
    message='',
    img_type=''
):
    return render_template(template,
        show_name=show_name,
        shows=shows,
        show=show,
        message=message,
        img_type=img_type,
        bannerart=get_setting_value('library_use_bannerart') == '1'
    )


### Image cache ###
def xbmcmm_image_cache(
    image,
    media_type,
    img_type,
    show_name=None,
    season=None,
    episode=None,
    movie_name=None,
    fanarttv=False
):

    base_dir = os.path.join(maraschino.DATA_DIR, 'cache', 'XBMCMM', media_type)

    if show_name:
        base_dir = os.path.join(base_dir, show_name)
        if season:
            base_dir = os.path.join(base_dir, 'season ' + str(season))
            if episode:
                base_dir = os.path.join(base_dir, 'episode ' + str(episode))
    elif movie_name:
        base_dir = os.path.join(base_dir, movie_name)

    base_dir = os.path.join(base_dir, img_type)
    create_dir(base_dir)

    if fanarttv:
        fanarttv_img = image[:-8]
        x = fanarttv_img.rfind('/')
        filename = fanarttv_img[x + 1:]
    else:
        x = image.rfind('/')
        filename = image[x + 1:]

    file_path = os.path.join(base_dir, filename)

    if not os.path.exists(file_path):
        Thread(target=download_image, args=(image, file_path)).start()
        maraschino.THREADS.append(len(maraschino.THREADS) + 1)

    if file_path.startswith('/'):
        file_path = file_path[1:]
        return '%s/cache/image_file/unix/%s' % (maraschino.WEBROOT, file_path)

    return '%s/cache/image_file/win/%s' % (maraschino.WEBROOT, file_path)


### File system ###
img_ext = ['.jpg', '.jpeg', '.tbn']


def get_win_drives():
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()  # @UndefinedVariable
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter + ':\\')
        bitmask >>= 1

    return drives


def get_dir(path):
    dir = {'dirs': [], 'files': []}

    for item in os.listdir(path):
        full_path = os.path.join(path, item)

        if os.path.isdir(full_path):
            dir['dirs'].append(full_path)

        if os.path.isfile(full_path):
            for ext in img_ext:
                if full_path.endswith(ext):
                    dir['files'].append(full_path)

    return dir


def get_parent_dir(path):
    dirname = os.path.basename(path)
    parent = path[:-len(dirname)]
    if parent == '/':
        parent = ''
    return parent


def strip_parent_dirs(path):
    if os.name == 'nt' and path[-2] == ':':
        return path
    return os.path.basename(path)


def get_home_dirs():
    if os.name == 'nt':
        return {'dirs': get_win_drives(), 'files': []}
    else:
        return get_dir('/')


def browse_filesystem(dir=get_home_dirs(), path=''):
    if path:
        dir = get_dir(path)
        root = False
    else:
        root = True
        path = 'Root'

    if dir['dirs'] == []:
        dir['dirs'].append('empty')

    if path[-1] == '\\' and path[-2] != ':':
        path = path[:-1]
    elif path[-1] == '/':
        path = path[:-1]

    return {
        'current_path': path,
        'root': root,
        'dir': dir
    }


@app.route('/xhr/filesystem/', methods=['GET', 'POST'])
@requires_auth
def xhr_filesystem():
    try:
        path = request.form['path']
        path = urllib.unquote(path.encode('ascii')).decode('utf-8')
        filesystem = browse_filesystem(path=path)
    except:
        filesystem = browse_filesystem()

    dir = filesystem['dir']
    root = filesystem['root']
    path = filesystem['current_path']

    return render_template('xbmcmm/modals/filesystem.html',
        path=path,
        dir=dir,
        root=root,
    )


### List to srting ###
def lst2str(details):
    for i in details:
        if isinstance(details[i], list):
            details[i] = ' / '.join(details[i])
    return details


### String to list ###
def str2lst(str_lst):
    return [x.strip() for x in str_lst.split('/') if x != '']


def is_digit(var):
    return var.isdigit()


def tostring(var):
    return str(var)

### Filters ###
FILTERS['parent'] = get_parent_dir
FILTERS['strip_parents'] = strip_parent_dirs
FILTERS['isdigit'] = is_digit
FILTERS['str'] = tostring


### Media properties ###
movie_properties = ['title', 'originaltitle', 'sorttitle', 'rating', 'studio', 'tagline', 'mpaa',
                    'set', 'year', 'genre', 'plot', 'director', 'art', 'trailer', 'playcount',
                    'imdbnumber', 'writer', 'runtime', 'votes', 'tag']

show_properties = ['title', 'sorttitle', 'originaltitle', 'mpaa', 'rating', 'votes', 'genre', 'plot',
                   'studio', 'premiered', 'imdbnumber', 'art', 'tag']

season_properties = ['season', 'showtitle', 'tvshowid']

episode_properties = ['title', 'rating', 'plot', 'director', 'writer', 'season', 'firstaired',
                      'art', 'episode', 'tvshowid', 'showtitle', 'votes', 'playcount']


### Genres  ###
video_genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Disaster', 'Documentary', 'Drama',
                'Family', 'Fantasy', 'Film Noir', 'Foreign', 'History', 'Holiday', 'Horror', 'Indie',
                'Music', 'Musical', 'Mystery', 'Road Movie', 'Romance', 'Science Fiction', 'Sport',
                'Sports Film', 'Suspense', 'Thriller', 'War', 'Western']
