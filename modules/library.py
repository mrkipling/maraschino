from flask import Flask, render_template
import jsonrpclib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/library')
@requires_auth
def xhr_library():
    return render_library()

@app.route('/xhr/library/<item_type>')
@requires_auth
def xhr_library_root(item_type):
    api_address = server_api_address()

    if not api_address:
        return render_library(message="You need to configure XBMC server settings first.")

    try:
        xbmc = jsonrpclib.Server(api_address)
        library = []
        title = "Movies"

        if item_type == 'movies':
            library = xbmc.VideoLibrary.GetMovies(sort={ 'method': 'label', 'ignorearticle' : True }, properties=['playcount'])

        if item_type == 'shows':
            title = "TV Shows"
            library = xbmc.VideoLibrary.GetTVShows(sort={ 'method': 'label', 'ignorearticle' : True }, properties=['playcount'])

        if item_type == 'artists':
            title = "Music"
            library = xbmc.AudioLibrary.GetArtists(sort={ 'method': 'label', 'ignorearticle' : True })

    except:
        return render_library(message="There was a problem connecting to the XBMC server.")

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>')
@requires_auth
def xhr_library_show(show):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.VideoLibrary.GetSeasons(tvshowid=show, properties=['tvshowid', 'season', 'showtitle', 'playcount'])
    library['tvshowid'] = show

    title = library['seasons'][0]['showtitle']

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>/<int:season>')
@requires_auth
def xhr_library_season(show, season):
    xbmc = jsonrpclib.Server(server_api_address())

    sort = { 'method': 'episode' }
    library = xbmc.VideoLibrary.GetEpisodes(tvshowid=show, season=season, sort=sort, properties=['tvshowid', 'season', 'showtitle', 'episode', 'plot', 'playcount'])

    episode = library['episodes'][0]
    title = '%s - Season %s' % (episode['showtitle'], episode['season'])

    return render_library(library, title)

@app.route('/xhr/library/artists/<int:artist>')
@requires_auth
def xhr_library_artist(artist):
    xbmc = jsonrpclib.Server(server_api_address())

    sort = { 'method': 'year' }
    library = xbmc.AudioLibrary.GetAlbums(artistid=artist, sort=sort, properties=['artistid', 'title', 'artist', 'year'])
    library['artistid'] = artist

    title = library['albums'][0]['artist']

    return render_library(library, title)

@app.route('/xhr/library/artists/<int:artist>/<int:album>')
@requires_auth
def xhr_library_album(artist, album):
    xbmc = jsonrpclib.Server(server_api_address())

    sort = { 'method': 'track' }
    library = xbmc.AudioLibrary.GetSongs(artistid=artist, albumid=album, sort=sort, properties=['artistid', 'artist', 'album', 'track', 'playcount', 'year'])

    song = library['songs'][0]
    title = '%s - %s (%s)' % (song['artist'], song['album'], song['year'])

    return render_library(library, title)

@app.route('/xhr/library/movies/info/<int:movieid>')
@requires_auth
def xhr_library_info_movie(movieid):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties=['title', 'rating', 'year', 'genre', 'plot', 'director', 'thumbnail', 'trailer', 'playcount'])
    movie = library['moviedetails']
    title = movie['title']
    itemart_url = movie['thumbnail']
    try:
        itemart = '%s/vfs/%s' % (safe_server_address(), itemart_url)
    except:
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        movie = movie,
        itemart = itemart,
    )

@app.route('/xhr/library/shows/info/<int:tvshowid>')
@requires_auth
def xhr_library_info_show(tvshowid):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=tvshowid, properties=['title', 'rating', 'year', 'genre', 'plot', 'premiered', 'thumbnail', 'playcount', 'studio'])
    show = library['tvshowdetails']
    title = show['title']
    itemart_url = show['thumbnail']
    try:
        itemart = '%s/vfs/%s' % (safe_server_address(), itemart_url)
    except:
        itemart = None

    bannerart = get_setting_value('library_use_bannerart') == '1'

    return render_template('library.html',
        library = library,
        title = title,
        show = show,
        itemart = itemart,
        bannerart = bannerart,
    )

@app.route('/xhr/library/episodes/info/<int:episodeid>')
@requires_auth
def xhr_library_info_episode(episodeid):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=episodeid, properties=['season', 'tvshowid', 'title', 'rating', 'plot', 'thumbnail', 'playcount', 'firstaired'])
    episode = library['episodedetails']
    title = episode['title']
    itemart_url = episode['thumbnail']
    try:
        itemart = '%s/vfs/%s' % (safe_server_address(), itemart_url)
    except:
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        episode = episode,
        itemart = itemart,
    )

@app.route('/xhr/library/artists/info/<int:artistid>')
@requires_auth
def xhr_library_info_artist(artistid):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.AudioLibrary.GetArtistDetails(artistid=artistid, properties=['description', 'thumbnail', 'formed', 'genre'])
    artist = library['artistdetails']
    title = artist['label']
    itemart_url = artist['thumbnail']
    try:
        itemart = '%s/vfs/%s' % (safe_server_address(), itemart_url)
    except:
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        artist = artist,
        itemart = itemart,
    )

@app.route('/xhr/library/albums/info/<int:albumid>')
@requires_auth
def xhr_library_info_album(albumid):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.AudioLibrary.GetAlbumDetails(albumid=albumid, properties=['artistid', 'title', 'artist', 'year', 'genre', 'description', 'albumlabel', 'rating', 'thumbnail'])
    album = library['albumdetails']
    title = '%s - %s' % (album['artist'], album['title'])
    itemart_url = album['thumbnail']
    try:
        itemart = '%s/vfs/%s' % (safe_server_address(), itemart_url)
    except:
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        album = album,
        itemart = itemart,
    )

def render_library(library=None, title="Media Library", message=None):
    show_info = get_setting_value('library_show_info') == '1'

    return render_template('library.html',
        library = library,
        title = title,
        message = message,
        show_info = show_info,
    )
