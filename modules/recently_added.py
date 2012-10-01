from flask import render_template
import jsonrpclib, ast, os

from maraschino import app, logger, DATA_DIR, THREADS, HOST, PORT, WEBROOT
from maraschino.noneditable import *
from maraschino.tools import *
from threading import Thread
from maraschino.models import RecentlyAdded, XbmcServer
from maraschino.database import db_session


@app.route('/xhr/recently_added/')
@requires_auth
def xhr_recently_added():
    return render_recently_added_episodes()


@app.route('/xhr/recently_added_movies/')
@requires_auth
def xhr_recently_added_movies():
    return render_recently_added_movies()


@app.route('/xhr/recently_added_albums/')
@requires_auth
def xhr_recently_added_albums():
    return render_recently_added_albums()


@app.route('/xhr/recently_added/<int:episode_offset>')
@requires_auth
def xhr_recently_added_episodes_offset(episode_offset):
    return render_recently_added_episodes(episode_offset)


@app.route('/xhr/recently_added_movies/<int:movie_offset>')
@requires_auth
def xhr_recently_added_movies_offset(movie_offset):
    return render_recently_added_movies(movie_offset)


@app.route('/xhr/recently_added_albums/<int:album_offset>')
@requires_auth
def xhr_recently_added_albums_offset(album_offset):
    return render_recently_added_albums(album_offset)


def get_recent_xbmc_api_url(setting):
    if get_setting_value(setting):
        return ast.literal_eval(get_setting_value(setting))['api']
    else:
        return server_api_address()

def get_recent_xbmc_label(setting):
    if get_setting_value(setting):
        return ast.literal_eval(get_setting_value(setting))['label']
    else:
        active_server = get_setting_value('active_server')
        if active_server:
            active_server = int(active_server)

            server = XbmcServer.query.filter(XbmcServer.id == active_server).first()
            return server.label
        else:
            return 'unknown'


def render_recently_added_episodes(episode_offset=0):
    compact_view = get_setting_value('recently_added_compact') == '1'
    show_watched = get_setting_value('recently_added_watched_episodes') == '1'
    view_info = get_setting_value('recently_added_info') == '1'

    xbmc = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_server'))
    recently_added_episodes = get_recently_added_episodes(xbmc, episode_offset)

    return render_template('recently_added.html',
        recently_added_episodes = recently_added_episodes[0],
        episode_offset = episode_offset,
        compact_view = compact_view,
        total_episodes = recently_added_episodes[1],
        view_info = view_info,
        using_db = recently_added_episodes[2]
    )


def render_recently_added_movies(movie_offset=0):
    compact_view = get_setting_value('recently_added_movies_compact') == '1'
    show_watched = get_setting_value('recently_added_watched_movies') == '1'
    view_info = get_setting_value('recently_added_movies_info') == '1'

    xbmc = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_movies_server'))
    recently_added_movies = get_recently_added_movies(xbmc, movie_offset)

    return render_template('recently_added_movies.html',
        recently_added_movies = recently_added_movies[0],
        movie_offset = movie_offset,
        compact_view = compact_view,
        total_movies = recently_added_movies[1],
        view_info = view_info,
        using_db = recently_added_movies[2]
    )


def render_recently_added_albums(album_offset=0):
    compact_view = get_setting_value('recently_added_albums_compact') == '1'
    view_info = get_setting_value('recently_added_albums_info') == '1'


    xbmc = jsonrpclib.Server(get_recent_xbmc_api_url('recently_added_albums_server'))
    recently_added_albums = get_recently_added_albums(xbmc, album_offset)


    return render_template('recently_added_albums.html',
        recently_added_albums = recently_added_albums[0],
        album_offset = album_offset,
        compact_view = compact_view,
        view_info = view_info,
        using_db = recently_added_albums[1]
    )


def get_num_recent_episodes():
    try:
        return int(get_setting_value('num_recent_episodes'))

    except:
        return 3

def get_num_recent_movies():
    try:
        return int(get_setting_value('num_recent_movies'))

    except:
        return 3


def get_num_recent_albums():
    try:
        return int(get_setting_value('num_recent_albums'))

    except:
        return 3


def get_recently_added_episodes(xbmc, episode_offset=0, mobile=False):
    num_recent_videos = get_num_recent_episodes()
    xbmc_label = get_recent_xbmc_label('recently_added_server')
    total_episodes = 0
    using_db = False

    try:
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'playcount', 'thumbnail'])['episodes']
        recently_added_db_add(xbmc_label, 'episodes', recently_added_episodes)

        thumbs = [recent_image_file(xbmc_label, 'episodes', x['episodeid'])[1] for x in recently_added_episodes]
        cache_dir = os.path.join(DATA_DIR, 'cache', 'xbmc', xbmc_label, 'recent_episodes')

        try:
            remove_recent_images(cache_dir, thumbs)
        except:
            logger.log('Failed to delete old images from %s' % cache_dir, 'WARNING')

        for episode in recently_added_episodes:
            episode['thumbnail'] = cache_recent_image(xbmc_label, 'episodes', episode['episodeid'], episode['thumbnail'])

    except:
        recently_added_episodes = []

    if not recently_added_episodes:
        try:
            logger.log('Using cached recently added episodes', 'INFO')
            recently_added_episodes = RecentlyAdded.query.filter(RecentlyAdded.name == '%s_episodes' % xbmc_label).first().data

            for episode in recently_added_episodes:
                thumb = recent_image_file(xbmc_label, 'episodes', episode['episodeid'])
                episode['thumbnail'] = thumb[0] + thumb[1]

            using_db = True
        except:
            recently_added_episodes = []
            logger.log('Failed to get recently added episodes from database', 'ERROR')

    if recently_added_episodes:
        if get_setting_value('recently_added_watched_episodes') == '0':
            recently_added_episodes = get_unwatched(recently_added_episodes)

    if mobile:
        return [recently_added_episodes, using_db]

    if recently_added_episodes:
        total_episodes = len(recently_added_episodes)
        recently_added_episodes = recently_added_episodes[episode_offset:num_recent_videos + episode_offset]

    return [recently_added_episodes, total_episodes, using_db]


def get_recently_added_movies(xbmc, movie_offset=0, mobile=False):
    num_recent_videos = get_num_recent_movies()
    xbmc_label = get_recent_xbmc_label('recently_added_movies_server')
    total_movies = 0
    using_db = False

    try:
        recently_added_movies = xbmc.VideoLibrary.GetRecentlyAddedMovies(properties = ['title', 'year', 'rating', 'playcount', 'thumbnail'])['movies']
        recently_added_db_add(xbmc_label, 'movies', recently_added_movies)

        thumbs = [recent_image_file(xbmc_label, 'movies', x['movieid'])[1] for x in recently_added_movies]
        cache_dir = os.path.join(DATA_DIR, 'cache', 'xbmc', xbmc_label, 'recent_movies')

        try:
            remove_recent_images(cache_dir, thumbs)
        except:
            logger.log('Failed to delete old images from %s' % cache_dir, 'WARNING')

        for movie in recently_added_movies:
            movie['thumbnail'] = cache_recent_image(xbmc_label, 'movies', movie['movieid'], movie['thumbnail'])

    except:
        recently_added_movies = []

    if not recently_added_movies:
        try:
            logger.log('Using cached recently added movies', 'INFO')
            recently_added_movies = RecentlyAdded.query.filter(RecentlyAdded.name == '%s_movies' % xbmc_label).first().data

            for movie in recently_added_movies:
                thumb = recent_image_file(xbmc_label, 'movies', movie['movieid'])
                movie['thumbnail'] = thumb[0] + thumb[1]

            using_db = True
        except:
            recently_added_movies = []
            logger.log('Failed to get recently added movies from database', 'ERROR')

    if recently_added_movies:
        if get_setting_value('recently_added_watched_movies') == '0':
            recently_added_movies = get_unwatched(recently_added_movies)

    if mobile:
        return [recently_added_movies, using_db]

    if recently_added_movies:
        total_movies = len(recently_added_movies)
        recently_added_movies = recently_added_movies[movie_offset:num_recent_videos + movie_offset]

    return [recently_added_movies, total_movies, using_db]

def get_recently_added_albums(xbmc, album_offset=0, mobile=False):
    num_recent_albums = get_num_recent_albums()
    xbmc_label = get_recent_xbmc_label('recently_added_albums_server')
    using_db = False

    try:
        recently_added_albums = xbmc.AudioLibrary.GetRecentlyAddedAlbums(properties = ['title', 'year', 'rating', 'artist', 'thumbnail'])['albums']
        recently_added_db_add(xbmc_label, 'albums', recently_added_albums)

        thumbs = [recent_image_file(xbmc_label, 'albums', x['albumid'])[1] for x in recently_added_albums]
        cache_dir = os.path.join(DATA_DIR, 'cache', 'xbmc', xbmc_label, 'recent_albums')

        try:
            remove_recent_images(cache_dir, thumbs)
        except:
            logger.log('Failed to delete old images from %s' % cache_dir, 'WARNING')

        for album in recently_added_albums:
            album['thumbnail'] = cache_recent_image(xbmc_label, 'albums', album['albumid'], album['thumbnail'])

    except:
        recently_added_albums = []

    if not recently_added_albums:
        try:
            logger.log('Using cached recently added albums', 'INFO')
            recently_added_albums = RecentlyAdded.query.filter(RecentlyAdded.name == '%s_albums' % xbmc_label).first().data

            for album in recently_added_albums:
                thumb = recent_image_file(xbmc_label, 'albums', album['albumid'])
                album['thumbnail'] = thumb[0] + thumb[1]

            using_db = True
        except:
            recently_added_movies = []
            logger.log('Failed to get recently added albums from database', 'ERROR')

    if not mobile and recently_added_albums:
        recently_added_albums = recently_added_albums[album_offset:num_recent_albums + album_offset]

    return [recently_added_albums, using_db]


def get_unwatched(recently_added):
    unwatched = []
    for media in recently_added:
        if media['playcount'] == 0:
            unwatched.append(media)

    return unwatched


def recently_added_db_add(server, media_type, recently_added):
    name = '%s_%s' % (server, media_type)
    if RecentlyAdded.query.filter(RecentlyAdded.name == name).first() == None:
        db_session.add(RecentlyAdded(name=name, data=[]))
        db_session.commit()

    recent = RecentlyAdded.query.filter(RecentlyAdded.name == name).first()

    if recently_added:
        recent.data = recently_added
        db_session.add(recent)
        db_session.commit()

    return


def cache_recent_image(label, type, id, image):
    file_dir = os.path.join(DATA_DIR, 'cache', 'xbmc', label, 'recent_%s' % type)
    create_dir(file_dir)

    file_path = os.path.join(file_dir, '%s.jpg' % id)

    if not os.path.exists(file_path):
        image_path = maraschino_path() + xbmc_image(image, label)
        Thread(target=download_image, args=(image_path, file_path)).start()
        THREADS.append(len(THREADS) + 1)

    return xbmc_image(image, label)


def recent_image_file(server, media_type, id):
    filepath = os.path.join(DATA_DIR, 'cache', 'xbmc', server, 'recent_%s' % media_type, '%s.jpg' % id)
    if os.name == 'nt':
        system = 'win'
    else:
        system = 'unix'
        filepath = filepath[1:]

    return ['%s/cache/image_file/%s/' % (WEBROOT, system), filepath]


def remove_recent_images(cache_dir, thumbs):
    if os.path.exists(cache_dir):
        exist = os.listdir(cache_dir)
        if exist:
            for img in exist:
                if not os.path.join(cache_dir, img) in thumbs:
                    os.remove(os.path.join(cache_dir, img))


def maraschino_path():
    if HOST == '0.0.0.0':
        return 'http://127.0.0.1:' + str(PORT)
    else:
        return 'http://' + HOST + ':' + str(PORT)