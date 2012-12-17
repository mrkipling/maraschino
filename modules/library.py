from flask import render_template, jsonify
import jsonrpclib
import urllib

from maraschino.noneditable import *
from maraschino.tools import *
from maraschino import app, logger

xbmc_error = 'There was a problem connecting to the XBMC server'


@app.route('/xhr/library')
@requires_auth
def xhr_library():
    return render_library()


@app.route('/xhr/library/<item_type>')
@requires_auth
def xhr_library_root(item_type):
    api_address = server_api_address()

    if not api_address:
        logger.log('LIBRARY :: No XBMC server defined', 'ERROR')
        return render_library(message="You need to configure XBMC server settings first.")

    try:
        xbmc = jsonrpclib.Server(api_address)
        library = []
        title = "Movies"

        if item_type == 'movies':
            logger.log('LIBRARY :: Retrieving movies', 'INFO')
            library = xbmc.VideoLibrary.GetMovies(sort={'method': 'label', 'ignorearticle': True}, properties=['playcount'])
            logger.log('LIBRARY :: Finished retrieveing movies', 'DEBUG')

            if get_setting_value('library_watched_movies') == '0':
                logger.log('LIBRARY :: Showing only unwatched movies', 'INFO')
                unwatched = []

                for movies in library['movies']:
                    movie_playcount = movies['playcount']

                    if movie_playcount == 0:
                        unwatched.append(movies)

                unwatched = {'movies': unwatched}
                library = unwatched

        if item_type == 'shows':
            logger.log('LIBRARY :: Retrieving TV shows', 'INFO')
            title = "TV Shows"
            library = xbmc.VideoLibrary.GetTVShows(sort={'method': 'label', 'ignorearticle': True}, properties=['playcount'])
            logger.log('LIBRARY :: Finished retrieveing TV Shows', 'DEBUG')

            if get_setting_value('library_watched_tv') == '0':
                logger.log('LIBRARY :: Showing only unwatched TV shows', 'INFO')
                unwatched = []

                for tvshows in library['tvshows']:
                    tvshow_playcount = tvshows['playcount']

                    if tvshow_playcount == 0:
                        unwatched.append(tvshows)

                unwatched = {'tvshows': unwatched}
                library = unwatched

        if item_type == 'artists':
            logger.log('LIBRARY :: Retrieving music', 'INFO')
            title = "Music"
            library = xbmc.AudioLibrary.GetArtists(sort={'method': 'label', 'ignorearticle': True})
            logger.log('LIBRARY :: Finished retrieveing music', 'DEBUG')

        if item_type == 'files':
            logger.log('LIBRARY :: Retrieving files', 'INFO')
            title = "Files"
            library = {'filemode': 'true'}
            xbmc.JSONRPC.Ping()

    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    return render_library(library, title)


@app.route('/xhr/library/shows/<int:show>')
@requires_auth
def xhr_library_show(show):
    logger.log('LIBRARY :: Retrieving seasons', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.VideoLibrary.GetSeasons(tvshowid=show, properties=['tvshowid', 'season', 'showtitle', 'playcount'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if get_setting_value('library_watched_tv') == '0':
        logger.log('LIBRARY :: Showing only unwatched seasons', 'INFO')
        unwatched = []

        for seasons in library['seasons']:
            season_playcount = seasons['playcount']

            if season_playcount == 0:
                unwatched.append(seasons)

        unwatched = {'seasons': unwatched}
        library = unwatched

    library['tvshowid'] = show
    title = library['seasons'][0]['showtitle']

    return render_library(library, title)


@app.route('/xhr/library/shows/<int:show>/<int:season>')
@requires_auth
def xhr_library_season(show, season):
    logger.log('LIBRARY :: Retrieving episodes', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    sort = {'method': 'episode'}

    try:
        library = xbmc.VideoLibrary.GetEpisodes(tvshowid=show, season=season, sort=sort, properties=['tvshowid', 'season', 'showtitle', 'episode', 'plot', 'playcount'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if get_setting_value('library_watched_tv') == '0':
        logger.log('LIBRARY :: Showing only unwatched episodes', 'INFO')
        unwatched = []

        for episodes in library['episodes']:
            episode_playcount = episodes['playcount']

            if episode_playcount == 0:
                unwatched.append(episodes)

        unwatched = {'episodes': unwatched}
        library = unwatched

    episode = library['episodes'][0]
    title = '%s - Season %s' % (episode['showtitle'], episode['season'])

    return render_library(library, title)


@app.route('/xhr/library/artists/<int:artist>')
@requires_auth
def xhr_library_artist(artist):
    logger.log('LIBRARY :: Retrieving albums', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    sort = {'method': 'year'}

    try:
        library = xbmc.AudioLibrary.GetAlbums(artistid=artist, sort=sort, properties=['artistid', 'title', 'artist', 'year'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    library['artistid'] = artist
    title = library['albums'][0]['artist']

    return render_library(library, title)


@app.route('/xhr/library/artists/<int:artist>/<int:album>')
@requires_auth
def xhr_library_album(artist, album):
    logger.log('LIBRARY :: Retrieving songs', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    sort = {'method': 'track'}

    try:
        library = xbmc.AudioLibrary.GetSongs(artistid=artist, albumid=album, sort=sort, properties=['artistid', 'artist', 'album', 'track', 'playcount', 'year'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    song = library['songs'][0]
    title = '%s - %s (%s)' % (song['artist'], song['album'], song['year'])

    return render_library(library, title)


@app.route('/xhr/library/<type>/info/<int:id>')
@requires_auth
def xhr_library_info(type, id):
    logger.log('LIBRARY :: Retrieving %s details' % type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if type == 'movie':
            library = xbmc.VideoLibrary.GetMovieDetails(movieid=id, properties=['title', 'rating', 'year', 'genre', 'plot', 'director', 'thumbnail', 'trailer', 'playcount', 'resume'])
            title = library['moviedetails']['title']

        elif type == 'tvshow':
            library = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=id, properties=['title', 'rating', 'year', 'genre', 'plot', 'premiered', 'thumbnail', 'playcount', 'studio'])
            title = library['tvshowdetails']['title']

        elif type == 'episode':
            library = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=id, properties=['season', 'tvshowid', 'title', 'rating', 'plot', 'thumbnail', 'playcount', 'firstaired', 'resume'])
            title = library['episodedetails']['title']

        elif type == 'artist':
            library = xbmc.AudioLibrary.GetArtistDetails(artistid=id, properties=['description', 'thumbnail', 'genre'])
            title = library['artistdetails']['label']

        elif type == 'album':
            library = xbmc.AudioLibrary.GetAlbumDetails(albumid=id, properties=['artistid', 'title', 'artist', 'year', 'genre', 'description', 'albumlabel', 'rating', 'thumbnail'])
            title = library['albumdetails']['title']

    except:
        message = 'Could not retrieve %s details' % type
        logger.log('LIBRARY :: %s' % message, 'ERROR')
        return render_library(message=message)

    return render_library(library, title)


@app.route('/xhr/library/<type>/resume_check/<int:id>/')
@requires_auth
def xhr_library_resume_check(type, id):
    logger.log('LIBRARY :: Checking if %s has resume position' % type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        if type == 'movie':
            library = xbmc.VideoLibrary.GetMovieDetails(movieid=id, properties=['resume'])

        elif type == 'episode':
            library = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=id, properties=['resume'])

    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    position = library[type + 'details']['resume']['position']

    if position:
        hours = position / 3600
        minutes = position / 60
        seconds = position % 60
        if position < 3600:
            position = '%02d:%02d' % (minutes, seconds)
        else:
            position = '%02d:%02d:%02d' % (hours, minutes, seconds)

        template = render_template('library-resume_dialog.html', position=position, library=library)
        return jsonify(resume=True, template=template)
    else:
        return jsonify(resume=False, template=None)


@app.route('/xhr/library/files/<file_type>')
@requires_auth
def xhr_library_files_file_type(file_type):
    logger.log('LIBRARY :: Retrieving %s sources' % file_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.Files.GetSources(media=file_type)
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if file_type == "video":
        title = "Files - Video"
    else:
        title = "Files - Music"

    return render_library(library, title, file_type)


@app.route('/xhr/library/files/<file_type>/dir/', methods=['POST'])
@requires_auth
def xhr_library_files_directory(file_type):
    path = request.form['path']
    path = urllib.unquote(path.encode('ascii')).decode('utf-8')
    logger.log('LIBRARY :: Retrieving %s path: %s' % (file_type, path), 'INFO')

    xbmc = jsonrpclib.Server(server_api_address())
    sort = {'method': 'file'}

    try:
        library = xbmc.Files.GetDirectory(media=file_type, sort=sort, directory=path)
        sources = xbmc.Files.GetSources(media=file_type)
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if path[-7:] == "%2ezip/":
        path = urllib.unquote(path.encode('ascii')).decode('utf-8')
        path = path.replace('zip://', '')

    if "\\" in path:
        windows = True
    else:
        windows = False

    if path.endswith('\\') or path.endswith('/'):
        previous_dir = path[:-1]
    else:
        previous_dir = path

    if windows:
        x = previous_dir.rfind("\\")
    else:
        x = previous_dir.rfind("/")

    current_dir = previous_dir[x + 1:]
    previous_dir = previous_dir[:x + 1]

    for source in sources['sources']:
        if source['file'] in path:
            current_source = source['file']
            source_label = source['label']
            break
        else:
            current_source = 'special://userdata/playlists/%s/' % file_type
            source_label = 'Playlists'

    if not current_source in previous_dir:
        previous_dir = "sources"

    if file_type == "video":
        file_type = "video_directory"
        if not current_source in previous_dir:
            title = "Video - " + source_label
        else:
            title = "Video - " + current_dir
    else:
        file_type = "music_directory"
        if not current_source in previous_dir:
            title = "Music - " + source_label
        else:
            title = "Music - " + current_dir

    if library['files'] == None:
        library['files'] = [{'filetype': 'none'}]

    return render_library(library, title, file_type, previous_dir)


def render_library(library=None, title="Media Library", file_type=None, previous_dir=None, message=None):
    return render_template('library.html',
        library=library,
        title=title,
        message=message,
        file_type=file_type,
        previous_dir=previous_dir,
        show_info=get_setting_value('library_show_info') == '1',
        show_music=get_setting_value('library_show_music') == '1',
        show_files=get_setting_value('library_show_files') == '1',
        library_show_power_buttons=get_setting_value('library_show_power_buttons', '1') == '1',
        bannerart=get_setting_value('library_use_bannerart') == '1',
    )
