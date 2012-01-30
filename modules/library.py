from flask import Flask, render_template
import jsonrpclib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/library/<library_type>')
@requires_auth
def xhr_library(library_type):
    return render_library(library_type)

@app.route('/xhr/library/<library_type>/<item_type>')
@requires_auth
def xhr_library_root(library_type, item_type):
    api_address = server_api_address()

    if not api_address:
        return render_library(message="You need to configure XBMC server settings first.", library_type=library_type)

    try:
        xbmc = jsonrpclib.Server(api_address)
        library = []
        title = "Movies"

        if item_type == 'movies':
            library = xbmc.VideoLibrary.GetMovies(sort={ 'method': 'label', 'ignorearticle' : True }, properties=['playcount', 'thumbnail', 'fanart', 'plotoutline', 'genre', 'year'],)

        if item_type == 'shows':
            title = "TV Shows"
            library = xbmc.VideoLibrary.GetTVShows(sort={ 'method': 'label', 'ignorearticle' : True }, properties=['playcount', 'thumbnail', 'fanart', 'genre', 'year'])

        if item_type == 'artists':
            title = "Music"
            library = xbmc.AudioLibrary.GetArtists(sort={ 'method': 'label', 'ignorearticle' : True })

    except:
        return render_library(message="There was a problem connecting to the XBMC server.", library_type=library_type)

    return render_library(library_type, library, title)

@app.route('/xhr/library/<library_type>/shows/<int:show>')
@requires_auth
def xhr_library_show(library_type, show):
    xbmc = jsonrpclib.Server(server_api_address())
    library = xbmc.VideoLibrary.GetSeasons(tvshowid=show, properties=['tvshowid', 'season', 'showtitle', 'playcount', 'thumbnail', 'fanart'])
    library['tvshowid'] = show
    title = library['seasons'][0]['showtitle']

    return render_library(library_type, library, title)

@app.route('/xhr/library/<library_type>/shows/<int:show>/<int:season>')
@requires_auth
def xhr_library_season(library_type, show, season):
    xbmc = jsonrpclib.Server(server_api_address())

    sort = { 'method': 'episode' }
    library = xbmc.VideoLibrary.GetEpisodes(tvshowid=show, season=season, sort=sort, properties=['tvshowid', 'season', 'showtitle', 'episode', 'plot', 'playcount'])

    episode = library['episodes'][0]
    title = '%s - Season %s' % (episode['showtitle'], episode['season'])

    return render_library(library_type, library, title)

@app.route('/xhr/library/<library_type>/artists/<int:artist>')
@requires_auth
def xhr_library_artist(library_type, artist):
    xbmc = jsonrpclib.Server(server_api_address())

    sort = { 'method': 'year' }
    library = xbmc.AudioLibrary.GetAlbums(artistid=artist, sort=sort, properties=['artistid', 'title', 'artist', 'year', 'thumbnail', 'fanart'])
    library['artistid'] = artist

    title = library['albums'][0]['artist']

    return render_library(library_type, library, title)

@app.route('/xhr/library/<library_type>/artists/<int:artist>/<int:album>')
@requires_auth
def xhr_library_album(library_type, artist, album):
    xbmc = jsonrpclib.Server(server_api_address())
	
    sort = { 'method': 'track' }
    library = xbmc.AudioLibrary.GetSongs(artistid=artist, albumid=album, sort=sort, properties=['artistid', 'artist', 'album', 'track', 'playcount', 'year'])

    song = library['songs'][0]
    title = '%s - %s (%s)' % (song['artist'], song['album'], song['year'])

    return render_library(library_type, library, title)

def render_library(library_type='module', library=None, title="Media Library", message=None):
    if library_type == 'expanded':
        template = 'library_expanded.html'
        vfs_url = '%s/vfs/' % (safe_server_address())

    else:
        template = 'library.html'
        vfs_url = None

    return render_template(template,
        library = library,
        title = title,
        message = message,
        vfs_url = vfs_url,
    )
