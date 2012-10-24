from flask import render_template, jsonify, request, json
from maraschino.noneditable import server_api_address
from maraschino.models import Setting
from maraschino.database import db_session
from maraschino.tools import requires_auth, get_setting, get_setting_value, natural_sort
from maraschino import app, logger
import jsonrpclib, random, os

back_id = {}
file_sources = {}
library_settings = {
    'movies': [
        {
            'key': 'xbmc_movies_sort',
            'value': 'label',
            'description': 'Sort movies by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'sorttitle', 'label': 'Sort Title'},
                {'value': 'year', 'label': 'Year'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'playcount', 'label': 'Play Count'},
                {'value': 'top250', 'label': 'Top 250'},
                {'value': 'votes', 'label': 'Votes'},
                {'value': 'country', 'label': 'Country'},
                {'value': 'mpaa', 'label': 'Classification'},
                {'value': 'lastplayed', 'label': 'Last Played'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_movies_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_movies_view',
            'value': 'list',
            'description': 'Movies view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'poster', 'label': 'Poster'},
            ]
        },
        {
            'key': 'xbmc_movies_view_sets',
            'value': '0',
            'description': 'Show movie sets',
            'type': 'bool',
        },
        {
            'key': 'xbmc_movies_hide_watched',
            'value': '0',
            'description': 'Hide watched movies',
            'type': 'bool',
        },
    ],
    'tvshows': [
        {
            'key': 'xbmc_tvshows_sort',
            'value': 'label',
            'description': 'Sort TV shows by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'sorttitle', 'label': 'Sort Title'},
                {'value': 'year', 'label': 'Year'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'votes', 'label': 'Votes'},
                {'value': 'studio', 'label': 'Studio'},
                {'value': 'mpaa', 'label': 'Classification'},
                {'value': 'totalepisodes', 'label': 'Total Episodes'},
                {'value': 'watchedepisodes', 'label': 'Watched Episodes'},
                {'value': 'dateadded', 'label': 'Date Added'},
                {'value': 'lastplayed', 'label': 'Last Played'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_tvshows_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_tvshows_view',
            'value': 'list',
            'description': 'TV shows view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'poster', 'label': 'Poster'},
                {'value': 'banner', 'label': 'Banner'},
            ]
        },
        {
            'key': 'xbmc_tvshows_hide_watched',
            'value': '0',
            'description': 'Hide watched TV shows',
            'type': 'bool',
        },
        {
            'key': 'xbmc_tvshows_prefer_banners',
            'value': '0',
            'description': 'Show banner on info screen',
            'type': 'bool',
        },
    ],
    'seasons': [
        {
            'key': 'xbmc_seasons_view',
            'value': 'list',
            'description': 'Seasons view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'poster', 'label': 'Poster'},
            ]
        },
        {
            'key': 'xbmc_seasons_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_seasons_hide_watched',
            'value': '0',
            'description': 'Hide watched seasons',
            'type': 'bool',
        },
    ],
    'episodes': [
        {
            'key': 'xbmc_episodes_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_episodes_view',
            'value': 'list',
            'description': 'Episodes view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
            ]
        },
        {
            'key': 'xbmc_episodes_hide_watched',
            'value': '0',
            'description': 'Hide watched episodes',
            'type': 'bool',
        },
    ],
    'artists': [
        {
            'key': 'xbmc_artists_sort',
            'value': 'label',
            'description': 'Sort artists by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'genre', 'label': 'Genre'},
            ]
        },
        {
            'key': 'xbmc_artists_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_artists_view',
            'value': 'list',
            'description': 'Artists view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
            ]
        },
        {
            'key': 'xbmc_artists_albumartistsonly',
            'value': '0',
            'description': 'Include artists only appearing in compilations',
            'type': 'bool',
        },
    ],
    'albums': [
        {
            'key': 'xbmc_albums_sort',
            'value': 'label',
            'description': 'Sort albums by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'genre', 'label': 'Genre'},
            ]
        },
        {
            'key': 'xbmc_albums_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_albums_view',
            'value': 'list',
            'description': 'Albums view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
            ]
        },
    ],

    'songs': [
        {
            'key': 'xbmc_songs_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_songs_view',
            'value': 'list',
            'description': 'Songs view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
            ]
        },
    ],
    'files': [
        {
            'key': 'xbmc_files_view',
            'value': 'list',
            'description': 'Files view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
            ]
        },
    ],
    'channelgroups': [
        {
            'key': 'xbmc_channelgroups_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_channelgroups_view',
            'value': 'list',
            'description': 'Channel groups view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
            ]
        },
    ],
    'channels': [
        {
            'key': 'xbmc_channels_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_channels_view',
            'value': 'list',
            'description': 'Channels view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
            ]
        },
    ],
}

def init_xbmc_media_settings():
    '''
    If library settings are not in
    database, add them with default value.
    '''
    for setting in library_settings:
        for s in library_settings[setting]:
            if get_setting(s['key']) == None:
                new_setting = Setting(key=s['key'], value=s['value'])
                db_session.add(new_setting)
    db_session.commit()

    return

init_xbmc_media_settings()

def get_xbmc_media_settings(media_type):
    '''
    Return settings for media type.
    '''

    settings = library_settings[media_type]

    for s in settings:
        s['value'] = get_setting_value(s['key'])

    return settings

@app.route('/xhr/library/save/<media_type>/', methods=['POST'])
@requires_auth
def save_xbmc_settings(media_type):
    """Save options in settings dialog"""
    try:
        settings = json.loads(request.form['settings'])

        for s in settings:
            setting = get_setting(s['name'])

            setting.value = s['value']
            db_session.add(setting)

        db_session.commit()
    except:
        return jsonify(error=True)

    return jsonify(success=True)


def xbmc_sort(media_type):
    '''
    Return sort values for media type.
    '''
    sort = {}
    sort['method'] = get_setting_value('xbmc_'+media_type+'_sort')
    sort['ignorearticle'] = get_setting_value('library_ignore_the') == '1'
    sort['order'] = get_setting_value('xbmc_'+media_type+'_sort_order')

    return sort


@app.route('/xhr/library/')
@app.route('/xhr/library/<media_type>')
@requires_auth
def xhr_xbmc_library_media(media_type=None):
    global back_id
    path = None
    back_path = '/'
    library = None

    if not server_api_address():
        logger.log('LIBRARY :: No XBMC server defined', 'ERROR')
        return render_xbmc_library(message="You need to configure XBMC server settings first.")

    try:
        #Reset back positions when rendering home
        if not media_type:
            back_id = {}

            return render_xbmc_library()

        xbmc = jsonrpclib.Server(server_api_address())
        template = 'library/media.html'


        #MOVIES
        if media_type == 'movies':
            file_type = 'video'

            if 'movieid' in request.args: #Movie details
                movieid = request.args['movieid']
                back_id['movies'] = movieid
                library = xbmc_get_details(xbmc, 'movie', int(movieid))
                template = 'library/details.html'
                title = '%s (%s)' % (library['label'], library['year'])
                if 'setid' in request.args:
                    back_path = '/movies?setid=%s' % request.args['setid']
                else:
                    back_path = '/movies'

            elif 'setid' in request.args: #Movie set
                setid = request.args['setid']
                back_id['movies'] = 'set' + setid
                library = xbmc_get_moviesets(xbmc, int(setid))
                title = library[0]['set']
                path = '/movies?setid=%s' % setid
                back_path = '/movies'

            else:
                library = xbmc_get_movies(xbmc)
                title = 'Movies'
                path = '/movies'


        #TVSHOWS
        elif media_type == 'tvshows':
            file_type = 'video'

            if 'tvshowid' in request.args: #TV show details
                tvshowid = request.args['tvshowid']
                back_id['tvshows'] = tvshowid
                library = xbmc_get_details(xbmc, 'tvshow', int(tvshowid))
                template = 'library/details.html'
                title = library['label']
                path = '/tvshows?tvshowid=%s' % tvshowid
                back_path = '/tvshows'

            else:
                library = xbmc_get_tvshows(xbmc)
                title = 'TV Shows'
                path = '/tvshows'


        elif media_type == 'seasons':
            file_type = 'video'
            tvshowid = request.args['tvshowid']
            back_id['tvshows'] = tvshowid
            library = xbmc_get_seasons(xbmc, int(tvshowid))
            title = library[0]['showtitle']
            path = '/seasons?tvshowid=%s' % tvshowid
            back_path = '/tvshows'


        elif media_type == 'episodes':
            file_type = 'video'
            tvshowid = request.args['tvshowid']
            season = request.args['season']
            back_id['tvshows'] = tvshowid
            back_id['seasons'] = season
            path = '/episodes?tvshowid=%s&season=%s' % (tvshowid, season)

            if 'episodeid' in request.args: #Episode details
                episodeid = request.args['episodeid']
                back_id['episodes'] = episodeid
                library = xbmc_get_details(xbmc, 'episode', int(episodeid))
                template = 'library/details.html'
                title = library['label']
                back_path = path

            else:
                library = xbmc_get_episodes(xbmc, int(tvshowid), int(season))
                title = '%s - Season %s' % (library[0]['showtitle'], library[0]['season'])
                back_path = '/seasons?tvshowid=%s' % tvshowid


        #MUSIC
        elif media_type == 'artists':
            file_type = 'audio'

            if 'artistid' in request.args: #Artist details
                artistid = request.args['artistid']
                back_id['artists'] = artistid
                library = xbmc_get_details(xbmc, 'artist', int(artistid))
                template = 'library/details.html'
                title = library['label']
                back_path = '/artists'

            else:
                library = xbmc_get_artists(xbmc)
                title = 'Artists'
                path = '/artists'


        elif media_type == 'albums':
            file_type = 'audio'
            artistid = request.args['artistid']
            back_id['artists'] = artistid
            path = '/albums?artistid=%s' % artistid

            if 'albumid' in request.args: #Album details
                albumid = request.args['albumid']
                back_id['albums'] = albumid
                library = xbmc_get_details(xbmc, 'album', int(albumid))
                template = 'library/details.html'
                title = library['label']
                back_path = path

            else:
                library = xbmc_get_albums(xbmc, int(artistid))
                title = library[0]['artist']
                back_path = '/artists'
            

        elif media_type == 'songs':
            file_type = 'audio'
            artistid = request.args['artistid']
            albumid = request.args['albumid']
            back_id['artists'] = artistid
            back_id['albums'] = albumid

            library = xbmc_get_songs(xbmc, int(artistid), int(albumid))
            title = '%s (%s)' % (library[0]['album'], library[0]['year'])
            path = '/songs?artistid=%s&albumid=%s' % (artistid, albumid)
            back_path = '/albums?artistid=%s' % artistid


        #PVR
        elif media_type == 'pvr': #PVR home
            file_type = None
            title = 'PVR'
            path = '/pvr'
            library = [
                {'label': 'TV', 'channeltype': 'tv'},
                {'label': 'Radio', 'channeltype': 'radio'}
            ]


        elif media_type == 'channelgroups': #CHANNEL GROUPS
            channeltype = request.args['type']
            if channeltype == 'tv':
                file_type = 'video'
                title = 'Live TV'
            else:
                file_type = 'audio'
                title = 'Live Radio'

            library = xbmc_get_channelgroups(xbmc, channeltype)
            path = '/channelgroups?type=%s' % channeltype
            back_path = '/pvr'


        elif media_type == 'channels': #CHANNELS
            channeltype = request.args['type']
            if channeltype == 'tv':
                file_type = 'video'
            else:
                file_type = 'audio'

            channelgroupid = request.args['channelgroupid']

            library = xbmc_get_channels(xbmc, channeltype, int(channelgroupid))
            path = '/channels?type=%s&channelgroupid=%s' % (channeltype, channelgroupid)
            back_path = '/channelgroups?type=%s' % channeltype
            title = library[0]['grouplabel']
            back_id['channelgroups'] = channelgroupid


        #FILES
        elif media_type == 'files':
            global file_sources

            if 'files' in request.args:
                file_type = request.args['files']

                if 'path' in request.args: #Path
                    title = request.args['path']
                    if title in file_sources[file_type]:
                        back_path = '/files?files=%s' % file_type
                    else:
                        back_path = '/files?files=%s&path=%s' % (file_type, os.path.dirname(title))
                        if back_path.endswith('/') or back_path.endswith('\\'):
                            back_path = back_path[:-1]

                    library = xbmc_get_file_path(xbmc, file_type, title)

                else: #Sources
                    file_sources = {}
                    library = xbmc_get_sources(xbmc, file_type)
                    title = '%s Sources' % file_type.title()
                    path = '/files?files=%s' % file_type
                    back_path = '/files'

            else: #Files home
                file_type = None
                title = 'Files'
                path = '/files'
                library = [
                    {'label': 'Video', 'filetype': 'video'},
                    {'label': 'Music', 'filetype': 'music'}
                ]

    except Exception as e:
        logger.log('LIBRARY :: Problem fetching %s' % media_type, 'ERROR')
        logger.log('EXCEPTION :: %s' % e, 'DEBUG')
        return render_xbmc_library(message='There was a problem connecting to the XBMC server')

    return render_xbmc_library(
        template=template,
        library=library,
        title=title,
        media=media_type,
        file=file_type,
        path=path,
        back_path=back_path
    )


def xbmc_get_movies(xbmc):
    logger.log('LIBRARY :: Retrieving movies', 'INFO')

    sort = xbmc_sort('movies')
    properties = ['playcount', 'thumbnail', 'year', 'rating', 'set']

    movies = xbmc.VideoLibrary.GetMovies(sort=sort, properties=properties)['movies']

    if get_setting_value('xbmc_movies_view_sets') == '1':
        movies = xbmc_movies_with_sets(xbmc, movies)

    if get_setting_value('xbmc_movies_hide_watched') == '1':
        movies = [x for x in movies if not x['playcount']]

    return movies


def xbmc_movies_with_sets(xbmc, movies):
    sort = xbmc_sort('movies')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']
    sets = xbmc.VideoLibrary.GetMovieSets(sort=sort, properties=['thumbnail', 'playcount'])['sets']

    #Find movies with sets and copy them into the set
    for set in sets:
        if version == 11:
            set['movies'] = [x for x in movies if set['label'] in x['set']]

        #Frodo
        else:
            set['movies'] = [x for x in movies if set['label'] == x['set']]

    #If set only has 1 movie, remove it from sets
    single_set_movies = [s['movies'][0] for s in [x for x in sets if len(x['movies']) == 1]]
    sets = [x for x in sets if len(x['movies']) > 1]

    #Add year and rating properties to set
    for set in sets:
        years = []
        ratings = []
        for movie in set['movies']:
            years.append(movie['year'])
            ratings.append(movie['rating'])

        set['year'] = max(years)
        set['rating'] = float(sum(ratings))/len(ratings)
        set['movieset'] = True

    #Remove movies in sets from movies list
    movies = [x for x in movies if not x['set'] or x in single_set_movies]
    #Add the movie sets to the movie list
    movies.extend(sets)

    #We need to re-sort the movies after adding sets
    if sort['method'] != 'random':

        if sort['method'] == 'label':
            #Remove 'The ' from labels if thats what the user wants
            if get_setting_value('library_ignore_the') == '1':
                the_movieids = {'movies': [], 'sets': []}
                for movie in movies:
                    if movie['label'].startswith('The '):
                        movie['label'] = movie['label'][4:]
                        if 'movieid' in movie:
                            the_movieids['movies'].append(movie['movieid'])
                        else:
                            the_movieids['sets'].append(movie['setid'])

            #Sort alphanumerically
            natural_sort(movies, key=lambda k: k[sort['method']])

            #Add 'The ' back in if it was removed
            if get_setting_value('library_ignore_the') == '1':
                for movie in movies:
                    if 'movieid' in movie:
                        if movie['movieid'] in the_movieids['movies']:
                            movie['label'] = 'The ' + movie['label']
                    else:
                        if movie['setid'] in the_movieids['sets']:
                            movie['label'] = 'The %s' % movie['label']

        else:
            movies = sorted(movies, key=lambda k: k[sort['method']])


        if sort['order'] == 'descending':
            movies.reverse()

    else:
        random.shuffle(movies)

    return movies


def xbmc_get_moviesets(xbmc, setid):
    logger.log('LIBRARY :: Retrieving movie set: %s' % setid, 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']

    sort = xbmc_sort('movies')
    properties = ['playcount', 'thumbnail', 'year', 'rating', 'set']
    params = {'sort': sort, 'properties': properties}

    if version == 11: #Eden
        params['properties'].append('setid')

    else: #Frodo
        params['filter'] = {'setid':setid}

    movies = xbmc.VideoLibrary.GetMovies(**params)['movies']

    if version == 11: #Eden
        movies = [x for x in movies if setid in x['setid']]
        setlabel = xbmc.VideoLibrary.GetMovieSetDetails(setid=setid)['setdetails']['label']
        for movie in movies:
            movie['set'] = setlabel

    if get_setting_value('xbmc_movies_hide_watched') == '1':
        movies = [x for x in movies if not x['playcount']]

    movies[0]['setid'] = setid
    return movies


def xbmc_get_tvshows(xbmc):
    logger.log('LIBRARY :: Retrieving TV shows', 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']

    sort = xbmc_sort('tvshows')
    properties = ['playcount', 'thumbnail', 'premiered', 'rating', 'file']

    if version > 11: #Frodo
        properties.append('art')

    tvshows = xbmc.VideoLibrary.GetTVShows(sort=sort, properties=properties)['tvshows']

    if get_setting_value('xbmc_tvshows_hide_watched') == '1':
        tvshows = [x for x in tvshows if not x['playcount']]

    return tvshows


def xbmc_get_seasons(xbmc, tvshowid):
    logger.log('LIBRARY :: Retrieving seasons for tvshowid: %s' % tvshowid, 'INFO')
    properties = ['playcount', 'showtitle', 'tvshowid', 'season', 'thumbnail', 'episode']

    seasons = xbmc.VideoLibrary.GetSeasons(tvshowid=tvshowid, properties=properties)['seasons']

    if get_setting_value('xbmc_seasons_hide_watched') == '1':
        seasons = [x for x in seasons if not x['playcount']]

    #Add episode playcounts to seasons
    for season in seasons:
        episodes = xbmc.VideoLibrary.GetEpisodes(
            tvshowid=tvshowid,
            season=season['season'],
            properties=['playcount']
        )['episodes']
        season['unwatched'] = len([x for x in episodes if not x['playcount']])

    #Sort broken on Eden, so doing it the manual way
    if xbmc_sort('seasons')['order'] != 'ascending':
        seasons = sorted(seasons, key=lambda k: k['season'], reverse=True)
    return seasons


def xbmc_get_episodes(xbmc, tvshowid, season):
    logger.log('LIBRARY :: Retrieving episodes for tvshowid: %s season: %s' % (tvshowid, season), 'INFO')

    properties = ['playcount', 'season', 'episode', 'tvshowid', 'showtitle', 'thumbnail', 'firstaired', 'rating']

    episodes = xbmc.VideoLibrary.GetEpisodes(
        tvshowid=tvshowid,
        season=season,
        properties=properties
    )['episodes']

    if get_setting_value('xbmc_episodes_hide_watched') == '1':
        episodes = [x for x in episodes if not x['playcount']]

    #Sort broken on Eden, so doing it the manual way
    if xbmc_sort('episodes')['order'] != 'ascending':
        episodes = sorted(episodes, key=lambda k: k['episode'], reverse=True)

    return episodes


def xbmc_get_artists(xbmc):
    logger.log('LIBRARY :: Retrieving artists', 'INFO')

    properties = ['thumbnail', 'genre', 'yearsactive']
    sort = xbmc_sort('artists')

    params = {
        'sort': sort,
        'properties': properties
    }

    if get_setting_value('xbmc_artists_albumartistsonly') == '0':
        params['albumartistsonly'] = True

    artists = xbmc.AudioLibrary.GetArtists(**params)['artists']

    for artist in artists:
        for k in artist:
            if isinstance(artist[k], list): #Frodo
                artist[k] = " / ".join(artist[k])

    return artists


def xbmc_get_albums(xbmc, artistid):
    logger.log('LIBRARY :: Retrieving albums for artistid: %s' % artistid, 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']
    params = {}

    params['sort'] = xbmc_sort('albums')
    params['properties'] = ['year', 'rating', 'thumbnail']

    if version == 11: #Eden
        params['artistid'] =  artistid
        params['properties'].extend(['artistid', 'artist'])

    else: #Frodo
        params['filter'] = {'artistid':artistid}

    albums = xbmc.AudioLibrary.GetAlbums(**params)['albums']

    if version > 11: #Frodo
        artist = xbmc.AudioLibrary.GetArtistDetails(artistid=artistid)['artistdetails']['label']
        for album in albums:
            album['artistid'] = artistid
            album['artist'] = artist

    return albums


def xbmc_get_songs(xbmc, artistid, albumid):
    logger.log('LIBRARY :: Retrieving songs for albumid: %s' % albumid, 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']
    params = {}

    params['properties'] = ['album', 'track', 'playcount', 'year', 'albumid']

    if version == 11: #Eden
        params['artistid'] = artistid
        params['albumid'] = albumid

    else: #Frodo
        params['filter'] = {
            'albumid': albumid
        }

    songs = xbmc.AudioLibrary.GetSongs(**params)['songs']

    for song in songs:
        song['artistid'] = artistid
        song['label'] = '%02d. %s' % (song['track'], song['label'])

    #Sort broken on Eden, so doing it the manual way
    if xbmc_sort('songs')['order'] != 'ascending':
        songs = sorted(songs, key=lambda k: k['track'], reverse=True)

    return songs


def xbmc_get_sources(xbmc, file_type):
    logger.log('LIBRARY :: Retrieving %s sources' % file_type, 'INFO')
    global file_sources

    sources = xbmc.Files.GetSources(media=file_type)['sources']

    for s in sources:
        if s['file'].endswith('/') or s['file'].endswith('\\'):
            s['file'] = s['file'][:-1]

    file_sources[file_type] = [x['file'] for x in sources]

    return sources


def xbmc_get_file_path(xbmc, file_type, path):
    logger.log('LIBRARY :: Retrieving %s path: %s' % (file_type, path), 'INFO')
    files = xbmc.Files.GetDirectory(media=file_type, directory=path)['files']

    if not files:
        files = [{'label': 'Directory is empty', 'file': path}]
    for f in files:
        if f['file'].endswith('/') or f['file'].endswith('\\'):
            f['file'] = f['file'][:-1]

    return files


def xbmc_get_channelgroups(xbmc, channeltype):
    return xbmc.PVR.GetChannelGroups(channeltype=channeltype)['channelgroups']

def xbmc_get_channels(xbmc, channeltype, channelgroupid):

    properties = ['channeltype', 'thumbnail', 'channel', 'locked']
    channels = xbmc.PVR.GetChannels(channelgroupid=channelgroupid, properties=properties)['channels']

    #Get channel group label
    groups = xbmc.PVR.GetChannelGroups(channeltype=channeltype)['channelgroups']
    for group in groups:
        if group['channelgroupid'] == channelgroupid:
            channels[0]['grouplabel'] = group['label']
            break

    return channels


def xbmc_get_details(xbmc, media_type, mediaid):
    logger.log('LIBRARY :: Retrieving %s details for %sid: %s' % (media_type, media_type, mediaid), 'INFO')

    if media_type == 'movie':
        properties = ['title', 'rating', 'year', 'genre', 'plot', 'director', 'thumbnail', 'trailer', 'playcount', 'resume']
        details = xbmc.VideoLibrary.GetMovieDetails(movieid=mediaid, properties=properties)['moviedetails']

    elif media_type == 'tvshow':
        properties = ['title', 'rating', 'year', 'genre', 'plot', 'premiered', 'thumbnail', 'playcount', 'studio']
        details = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=mediaid, properties=properties)['tvshowdetails']

    elif media_type == 'episode':
        properties = ['season', 'tvshowid', 'title', 'rating', 'plot', 'thumbnail', 'playcount', 'firstaired', 'resume']
        details = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=mediaid, properties=properties)['episodedetails']

    elif media_type == 'artist':
        properties = ['description', 'thumbnail', 'genre']
        details = xbmc.AudioLibrary.GetArtistDetails(artistid=mediaid, properties=properties)['artistdetails']

    elif media_type == 'album':
        properties = ['title', 'artist', 'year', 'genre', 'description', 'albumlabel', 'rating', 'thumbnail']
        details = xbmc.AudioLibrary.GetAlbumDetails(albumid=mediaid, properties=properties)['albumdetails']

    for k in details:
        if isinstance(details[k], list):
            details[k] = " / ".join(details[k])
    return details


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


def render_xbmc_library(template='library.html',
                        library=None,
                        title='XBMC Library',
                        message=None,
                        media=None,
                        file=None,
                        path='/',
                        back_path='/',
                        back_pos=None):

    if media:
        if media != 'pvr':
            settings = get_xbmc_media_settings(media)
            view = get_setting_value('xbmc_%s_view' % media)
        else:
            settings = None
            view = 'list'

        if media in back_id:
            back_pos = back_id[media]

    else:
        settings = None,
        view = 'list'

    return render_template(
        template,
        library=library,
        title=title,
        message=message,
        settings=settings,
        view=view,
        media=media,
        file=file,
        path=path,
        back_path=back_path,
        back_pos=back_pos,
        show_info=get_setting_value('library_show_info') == '1',
        show_music=get_setting_value('library_show_music') == '1',
        show_pvr=get_setting_value('library_show_pvr') == '1',
        show_files=get_setting_value('library_show_files') == '1',
        show_power=get_setting_value('library_show_power_buttons') == '1'
    )