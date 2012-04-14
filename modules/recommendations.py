try:
    import json
except ImportError:
    import simplejson as json

from flask import Flask, jsonify, render_template, request
import hashlib, jsonrpclib, urllib, random
from pprint import pprint

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *
from jinja2.filters import FILTERS

def small_poster(poster):

    if 'poster-small' in poster:
      return poster
    else:
        x = poster.rfind('.')
        return poster[:x] + '-138' + poster[x:]

FILTERS['small_poster'] = small_poster

@app.route('/xhr/recommendations')
def xhr_recommendations():
    TRAKT_API_KEY = get_setting_value('trakt_api_key')
    TRAKT_USERNAME = get_setting_value('trakt_username')
    TRAKT_PASSWORD = get_setting_value('trakt_password')

    rand = random.randint(0,10)

    # setting up username and password to pass to POST request
    try:
        params = {
          'username': TRAKT_USERNAME,
          'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest()
        }
    except:
        params = {}

    # Movie show recommendation request
    url = 'http://api.trakt.tv/recommendations/movies/%s' % (TRAKT_API_KEY)
    params = urllib.urlencode(params)
    result = urllib.urlopen(url, params).read()
    result = json.JSONDecoder().decode(result)

    # if result is empty, set mov object as empty
    if not result:
        mov = {}
    else:
        movie = result[rand]

        # checking if imdb id is present, otherwise, use tvdb id as per trakt instructions
        if movie['imdb_id'] != '':
            movie_id = movie['imdb_id']
        else:
            movie_id = movie['tmdb_id']

        # creating movie object to pass to template
        mov = {}
        mov['url'] = movie['url']
        mov['title'] = movie['title']
        mov['overview'] = movie['overview']
        mov['year'] = movie['year']
        mov['liked'] = movie['ratings']['percentage']
        mov['id'] = movie_id
        mov['watchlist'] = movie['in_watchlist']
        mov['poster'] = movie['images']['poster']

    # making TV Show Recommendation request
    url = 'http://api.trakt.tv/recommendations/shows/%s' % (TRAKT_API_KEY)
    result = urllib.urlopen(url, params).read()
    result = json.JSONDecoder().decode(result)

    #if result is empty, set tv object as empty
    if not result:
        tv = {}

    else:
        tv_result = result[rand]

        # checking if imdb id is present, otherwise, use tvdb id as per trakt instructions
        if tv_result['imdb_id'] != '':
            tv_id = tv_result['imdb_id']
        else:
            tv_id = tv_result['tmdb_id']

        # creating movie object to pass to template
        tv = {}
        tv['url'] = tv_result['url']
        tv['title'] = tv_result['title']
        tv['overview'] = tv_result['overview']
        tv['year'] = tv_result['year']
        tv['liked'] = tv_result['ratings']['percentage']
        tv['id'] = tv_id
        tv['watchlist'] = tv_result['in_watchlist']
        tv['poster'] = tv_result['images']['poster']

    return render_template('recommendations.html',
        movie = mov,
        tv = tv,
    )
