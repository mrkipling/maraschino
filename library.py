from flask import Flask, render_template
import jsonrpclib

from htpcfrontend import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/library')
@requires_auth
def xhr_library():
    return render_library()

@app.route('/xhr/library/<item_type>')
@requires_auth
def xhr_library_root(item_type):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    library = []
    title = "Movies"

    if item_type == 'movies':
        sort = { 'method': 'label' }
        library = xbmc.VideoLibrary.GetMovies(sort=sort)

    if item_type == 'shows':
        title = "TV shows"
        library = xbmc.VideoLibrary.GetTVShows()

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>')
@requires_auth
def xhr_library_show(show):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)
    library = xbmc.VideoLibrary.GetSeasons(tvshowid=show, properties=['tvshowid', 'season', 'showtitle'])

    title = library['seasons'][0]['showtitle']

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>/<int:season>')
@requires_auth
def xhr_library_season(show, season):
    xbmc = jsonrpclib.Server(SERVER_API_ADDRESS)

    sort = { 'method': 'episode' }
    library = xbmc.VideoLibrary.GetEpisodes(tvshowid=show, season=season, sort=sort, properties=['tvshowid', 'season', 'showtitle', 'episode', 'plot'])

    episode = library['episodes'][0]
    title = '%s - Season %s' % (episode['showtitle'], episode['season'])

    return render_library(library, title)

def render_library(library=None, title="Media library"):
    return render_template('library.html',
        library = library,
        title = title,
    )
