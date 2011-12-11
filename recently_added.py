from flask import Flask, render_template
import jsonrpclib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/recently_added')
@requires_auth
def xhr_recently_added():
    return render_recently_added_episodes()


@app.route('/xhr/recently_added_movies')
@requires_auth
def xhr_recently_added_movies():
    return render_recently_added_movies()


@app.route('/xhr/recently_added/<int:episode_offset>')
@requires_auth
def xhr_recently_added_episodes_offset(episode_offset):
    return render_recently_added_episodes(episode_offset)


@app.route('/xhr/recently_added_movies/<int:movie_offset>')
@requires_auth
def xhr_recently_added_movies_offset(movie_offset):
    return render_recently_added_movies(movie_offset)


def render_recently_added_episodes(episode_offset=0):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_episodes = get_recently_added_episodes(xbmc, episode_offset)
        vfs_url = '%s/vfs/' % (safe_server_address())

    except:
        recently_added_episodes = []
        vfs_url = None

    return render_template('recently_added.html',
        recently_added_episodes = recently_added_episodes,
        vfs_url = vfs_url,
        episode_offset = episode_offset,
    )


def render_recently_added_movies(movie_offset=0):
    try:
        xbmc = jsonrpclib.Server(server_api_address())
        recently_added_movies = get_recently_added_movies(xbmc, movie_offset)
        vfs_url = '%s/vfs/' % (safe_server_address())

    except:
        recently_added_movies = []
        vfs_url = None

    return render_template('recently_added_movies.html',
        recently_added_movies = recently_added_movies,
        vfs_url = vfs_url,
        movie_offset = movie_offset,
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


def get_recently_added_episodes(xbmc, episode_offset=0):
    num_recent_videos = get_num_recent_episodes()

    try:
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'lastplayed', 'thumbnail'])

        recently_added_episodes = recently_added_episodes['episodes'][episode_offset:num_recent_videos + episode_offset]

    except:
        recently_added_episodes = []

    return recently_added_episodes


def get_recently_added_movies(xbmc, movie_offset=0):
    num_recent_videos = get_num_recent_movies()

    try:
        recently_added_movies = xbmc.VideoLibrary.GetRecentlyAddedMovies(properties = ['title', 'year', 'rating', 'lastplayed', 'fanart'])

        recently_added_movies = recently_added_movies['movies'][movie_offset:num_recent_videos + movie_offset]

    except:
        recently_added_movies = []

    return recently_added_movies
