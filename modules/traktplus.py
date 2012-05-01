try:
    import json
except ImportError:
    import simplejson as json

from flask import Flask, jsonify, render_template, request
import hashlib, jsonrpclib, urllib, random, time
from threading import Thread

from Maraschino import app
from Maraschino import rundir
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *
import maraschino.logger as logger

global url_error
url_error = 'There was a problem connecting to trakt.tv. Please check your settings.'
threads = []

def create_dir(dir):
    if not os.path.exists(dir):
        try:
            logger.log('TRAKT :: Creating dir %s' % dir, 'INFO')
            os.makedirs(dir)
        except:
            logger.log('TRAKT :: Problem creating dir %s' % dir, 'ERROR')

create_dir('%s/static/images/trakt/shows' % rundir)
create_dir('%s/static/images/trakt/movies' % rundir)

def small_poster(image):
    if not 'poster-small' in image:
        x = image.rfind('.')
        image = image[:x] + '-138' + image[x:]
    return image

def download_image(image, file_path):
    try:
        logger.log('TRAKT :: Creating file %s' % file_path, 'INFO')
        downloaded_image = file(file_path, 'wb')
    except:
        logger.log('TRAKT :: Failed to create file %s' % file_path, 'ERROR')
        logger.log('TRAKT :: Using remote image', 'INFO')
        threads.pop()
        return image

    try:
        logger.log('TRAKT :: Downloading %s' % image, 'INFO')
        image_on_web = urllib.urlopen(image)
        while True:
            buf = image_on_web.read(65536)
            if len(buf) == 0:
                break
            downloaded_image.write(buf)
        downloaded_image.close()
        image_on_web.close()
    except:
        logger.log('TRAKT :: Failed to download %s' % image, 'ERROR')

    threads.pop()

    return

def cache_image(image, type):

    if type == 'shows':
        dir = '%s/static/images/trakt/shows' % rundir
    else:
        dir = '%s/static/images/trakt/movies' % rundir

    image = small_poster(image)

    x = image.rfind('/')
    filename = image[x:]
    file_path = "%s%s" % (dir, filename)

    if not os.path.exists(file_path):
        Thread(target=download_image, args=(image, file_path)).start()
        threads.append(len(threads) + 1)

    if type == 'shows':
        dir = '/static/images/trakt/shows'
    else:
        dir = '/static/images/trakt/movies'

    file_path = "%s%s" % (dir, filename)

    return file_path

@app.route('/xhr/traktplus')
def xhr_traktplus():
    render_template('trakt-base.html')
    return xhr_trakt_trending(type = 'shows')

@app.route('/xhr/trakt/recommendations')
def xhr_recommendations():
    logger.log('TRAKT :: Fetching recommendations', 'INFO')
    username = get_setting_value('trakt_username')
    password = get_setting_value('trakt_password')
    apikey = get_setting_value('trakt_api_key')

    rand = random.randint(0,10)

    # setting up username and password to pass to POST request
    try:
        params = {
          'username': username,
          'password': hashlib.sha1(password).hexdigest()
        }
    except:
        params = {}

    # Movie show recommendation request
    url = 'http://api.trakt.tv/recommendations/movies/%s' % (apikey)
    params = urllib.urlencode(params)

    try:
        result = urllib.urlopen(url, params).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

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
        mov['poster'] = cache_image(movie['images']['poster'], 'movies')

    # making TV Show Recommendation request
    url = 'http://api.trakt.tv/recommendations/shows/%s' % (apikey)

    try:
        result = urllib.urlopen(url, params).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

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
        tv['poster'] = cache_image(tv_result['images']['poster'], 'shows')

    while threads:
        time.sleep(1)

    return render_template('trakt-recommendations.html',
        recommendations = True,
        movie = mov,
        tv = tv,
        title = 'Recommendations',
    )

@app.route('/xhr/trakt/trending/<type>')
@requires_auth
def xhr_trakt_trending(type):
    logger.log('TRAKT :: Fetching trending %s' % type, 'INFO')
    apikey = get_setting_value('trakt_api_key')

    url = 'http://api.trakt.tv/%s/trending.json/%s' % (type, apikey)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    if len(trakt) > 20:
        trakt = trakt[:20]

    for item in trakt:
        item['images']['poster'] = cache_image(item['images']['poster'], type)

    while threads:
        time.sleep(1)

    return render_template('trakt-trending.html',
        trending = trakt,
        type = type.title(),
        title = 'Trending',
    )

@app.route('/xhr/trakt/friends')
@requires_auth
def xhr_trakt_friends():
    logger.log('TRAKT :: Fetching friends list', 'INFO')
    apikey = get_setting_value('trakt_api_key')
    username = get_setting_value('trakt_username')

    url = 'http://api.trakt.tv/user/friends.json/%s/%s' % (apikey, username)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    return render_template('trakt-friends.html',
        friends = trakt,
        title = 'Friends',
    )

@app.route('/xhr/trakt/profile')
@app.route('/xhr/trakt/profile/<user>')
@requires_auth
def xhr_trakt_profile(user=None):
    if not user:
        user = get_setting_value('trakt_username')

    logger.log('TRAKT :: Fetching %s\'s profile information' % user, 'INFO')
    apikey = get_setting_value('trakt_api_key')

    url = 'http://api.trakt.tv/user/profile.json/%s/%s/' % (apikey, user)

    try:
        result = urllib.urlopen(url).read()

    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    if 'status' in trakt and trakt['status'] == 'error':
        logger.log('TRAKT :: Error accessing user profile', 'INFO')
        movies_progress = 0
        episodes_progress = 0

    else:
        for item in trakt['watched']:
            item['watched'] = time.ctime(int(item['watched']))

        movies = trakt['stats']['movies']

        try:
            movies_progress = 100 * float(movies['watched_unique']) / float(movies['collection'])

        except:
            movies_progress = 0

        episodes = trakt['stats']['episodes']

        try:
            episodes_progress = 100 * float(episodes['watched_unique']) / float(episodes['collection'])

        except:
            episodes_progress = 0

    return render_template('trakt-user_profile.html',
        profile = trakt,
        movies_progress = int(movies_progress),
        episodes_progress = int(episodes_progress),
        title = 'Profile',
    )

@app.route('/xhr/trakt/library/<user>/<type>')
@requires_auth
def xhr_trakt_library(user, type):
    logger.log('TRAKT :: Fetching %s\'s %s library' % (user, type), 'INFO')
    apikey = get_setting_value('trakt_api_key')

    url = 'http://api.trakt.tv/user/library/%s/all.json/%s/%s' % (type, apikey, user)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    return render_template('trakt-library.html',
        library = trakt,
        user = user,
        type = type.title(),
        title = 'Library',
    )

@app.route('/xhr/trakt/watchlist/<user>/<type>')
@requires_auth
def xhr_trakt_watchlist(user, type):
    logger.log('TRAKT :: Fetching %s\'s %s watchlist' % (user, type), 'INFO')
    apikey = get_setting_value('trakt_api_key')

    url = 'http://api.trakt.tv/user/watchlist/%s.json/%s/%s/' % (type, apikey, user)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    if trakt == []:
        trakt = [{'empty': True}]

    return render_template('trakt-watchlist.html',
        watchlist = trakt,
        type = type.title(),
        user = user,
        title = 'Watchlist',
    )

@app.route('/xhr/trakt/loved/<user>/<type>')
@requires_auth
def xhr_trakt_loved(user, type):
    logger.log('TRAKT :: Fetching %s\'s loved %s' % (user, type), 'INFO')
    apikey = get_setting_value('trakt_api_key')

    url = 'http://api.trakt.tv/user/library/%s/loved.json/%s/%s/' % (type, apikey, user)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    amount = len(trakt)

    if trakt == []:
        trakt = [{'empty': True}]

    return render_template('trakt-loved.html',
        loved = trakt,
        amount = amount,
        type = type.title(),
        user = user,
        title = 'Loved',
    )

@app.route('/xhr/trakt/hated/<user>/<type>')
@requires_auth
def xhr_trakt_hated(user, type):
    logger.log('TRAKT :: Fetching %s\'s hated %s' % (user, type), 'INFO')
    apikey = get_setting_value('trakt_api_key')

    url = 'http://api.trakt.tv/user/library/%s/hated.json/%s/%s/' % (type, apikey, user)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)

    amount = len(trakt)

    if trakt == []:
        trakt = [{'empty': True}]

    return render_template('trakt-hated.html',
        hated = trakt,
        amount = amount,
        type = type.title(),
        user = user,
        title = 'Hated',
    )

@app.route('/xhr/trakt/calendar/<type>')
@requires_auth
def xhr_trakt_calendar(type):
    logger.log('TRAKT :: Fetching %s calendar' % type, 'INFO')
    apikey = get_setting_value('trakt_api_key')
    username = get_setting_value('trakt_username')

    if type == 'my shows':
        url = 'http://api.trakt.tv/user/calendar/shows.json/%s/%s' % (apikey, username)
    else:
        url = 'http://api.trakt.tv/calendar/%s.json/%s/' % (type, apikey)

    try:
        result = urllib.urlopen(url).read()
    except:
        logger.log('TRAKT :: Problem fething URL', 'ERROR')
        return render_template('trakt-base.html', message=url_error)

    trakt = json.JSONDecoder().decode(result)


    return render_template('trakt-calendar.html',
        calendar = trakt,
        type = type.title(),
        title = 'Calendar',
    )
