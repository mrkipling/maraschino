from flask import Flask, render_template
import jsonrpclib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

try:
    NUM_RECENT_VIDEOS = int(get_setting('num_recent_videos').value)
except:
    NUM_RECENT_VIDEOS = 3

@app.route('/xhr/recently_added')
@requires_auth
def xhr_recently_added():
    return render_recently_added_videos()

@app.route('/xhr/recently_added/<int:episode_offset>/<int:movie_offset>')
@requires_auth
def xhr_recently_added_offset(episode_offset, movie_offset):
    return render_recently_added_videos(episode_offset, movie_offset)

def render_recently_added_videos(episode_offset=0, movie_offset=0):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_episodes = get_recently_added_episodes(xbmc, episode_offset)
        recently_added_movies = get_recently_added_movies(xbmc, movie_offset)
        vfs_url = '%s/vfs/' % (safe_server_address())

    except:
        recently_added_episodes = []
        recently_added_movies = []
        vfs_url = None

    return render_template('recently_added.html',
        recently_added_episodes = recently_added_episodes,
        recently_added_movies = recently_added_movies,
        vfs_url = vfs_url,
        episode_offset = episode_offset,
        movie_offset = movie_offset,
    )


def get_recently_added_episodes(xbmc, episode_offset=0):
    try:
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'lastplayed', 'thumbnail'])
        
        recently_added_episodes = recently_added_episodes['episodes'][episode_offset:NUM_RECENT_VIDEOS + episode_offset]
        
    except:
        recently_added_episodes = []
        
    return recently_added_episodes


def get_recently_added_movies(xbmc, movie_offset=0):
    try:
        recently_added_movies = xbmc.VideoLibrary.GetRecentlyAddedMovies(properties = ['title', 'year', 'rating', 'lastplayed', 'fanart'])
        
        recently_added_movies = recently_added_movies['movies'][movie_offset:NUM_RECENT_VIDEOS + movie_offset]
        
    except:
        recently_added_movies = []
        
    return recently_added_movies
