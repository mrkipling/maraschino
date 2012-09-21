from flask import jsonify, render_template, request, json, send_file
import hashlib, urllib2, base64, random, time, datetime, os
from threading import Thread
from maraschino.tools import get_setting_value, requires_auth, create_dir, download_image
from maraschino import logger, app, WEBROOT, DATA_DIR, THREADS


def trak_api(url, params={}, dev=False):
    username = get_setting_value('trakt_username')
    password = hashlib.sha1(get_setting_value('trakt_password')).hexdigest()

    params = json.JSONEncoder().encode(params)
    request = urllib2.Request(url, params)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)

    response = urllib2.urlopen(request)
    response = response.read()
    response = json.JSONDecoder().decode(response)

    if dev:
        print url
        print json.dumps(response, sort_keys=True, indent=4)

    return response


def trakt_apikey():
    return get_setting_value('trakt_api_key')


def trakt_exception(e):
    logger.log('TRAKT :: EXCEPTION -- %s' % e, 'DEBUG')
    return e

create_dir(os.path.join(DATA_DIR, 'cache', 'trakt', 'shows'))
create_dir(os.path.join(DATA_DIR, 'cache', 'trakt', 'movies'))


def small_poster(image):
    if not 'poster-small' in image:
        x = image.rfind('.')
        image = image[:x] + '-138' + image[x:]
    return image


def cache_image(image, type):
    if type == 'shows':
        dir = '%s/cache/trakt/shows' % DATA_DIR
    else:
        dir = '%s/cache/trakt/movies' % DATA_DIR

    image = small_poster(image)

    x = image.rfind('/')
    filename = image[x:]
    file_path = "%s%s" % (dir, filename)

    if not os.path.exists(file_path):
        Thread(target=download_image, args=(image, file_path)).start()
        THREADS.append(len(THREADS) + 1)

    return '%s/cache/trakt/%s/%s' % (WEBROOT, type, filename[1:])


@app.route('/cache/trakt/<type>/<filename>')
@requires_auth
def img_cache(type, filename):
    img = os.path.join(DATA_DIR, 'cache', 'trakt', type, filename)
    return send_file(img, mimetype='image/jpeg')


@app.route('/xhr/traktplus/')
def xhr_traktplus():
    default = get_setting_value('trakt_default_view')

    if default == 'trending_shows':
        return xhr_trakt_trending('shows')
    elif default == 'trending_movies':
        return xhr_trakt_trending('movies')
    elif default == 'activity_friends':
        return xhr_trakt_activity('friends')
    elif default == 'activity_community':
        return xhr_trakt_activity('community')
    elif default == 'friends':
        return xhr_trakt_friends()
    elif default == 'calendar':
        return xhr_trakt_calendar('my shows')
    elif default == 'recommendations_shows':
        return xhr_trakt_recommendations('shows')
    elif default == 'recommendations_movies':
        return xhr_trakt_recommendations('movies')
    elif default == 'profile':
        return xhr_trakt_profile()


@app.route('/xhr/trakt/recommendations')
@app.route('/xhr/trakt/recommendations/<type>')
def xhr_trakt_recommendations(type=None):
    if not type:
        type = get_setting_value('trakt_default_media')

    logger.log('TRAKT :: Fetching %s recommendations' % type, 'INFO')

    url = 'http://api.trakt.tv/recommendations/%s/%s' % (type, trakt_apikey())

    params = {
        'hide_collected': True,
        'hide_watchlisted': True
    }
    try:
        recommendations = trak_api(url, params)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    random.shuffle(recommendations)

    for item in recommendations:
        item['poster'] = cache_image(item['images']['poster'], type)

    while THREADS:
        time.sleep(1)

    return render_template('traktplus/trakt-recommendations.html',
        type=type.title(),
        recommendations=recommendations,
        title='Recommendations',
    )


@app.route('/xhr/trakt/trending')
@app.route('/xhr/trakt/trending/<type>')
@requires_auth
def xhr_trakt_trending(type=None):
    if not type:
        type = get_setting_value('trakt_default_media')

    limit = int(get_setting_value('trakt_trending_limit'))
    logger.log('TRAKT :: Fetching trending %s' % type, 'INFO')

    url = 'http://api.trakt.tv/%s/trending.json/%s' % (type, trakt_apikey())
    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    if len(trakt) > limit:
        trakt = trakt[:limit]

    for item in trakt:
        item['images']['poster'] = cache_image(item['images']['poster'], type)

    while THREADS:
        time.sleep(1)

    return render_template('traktplus/trakt-trending.html',
        trending=trakt,
        type=type.title(),
        title='Trending',
    )


@app.route('/xhr/trakt/activity')
@app.route('/xhr/trakt/activity/<type>')
@requires_auth
def xhr_trakt_activity(type='friends'):
    logger.log('TRAKT :: Fetching %s activity' % type, 'INFO')

    url = 'http://api.trakt.tv/activity/%s.json/%s' % (type, trakt_apikey())
    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    return render_template('traktplus/trakt-activity.html',
        activity=trakt,
        type=type.title(),
        title='Activity',
    )


@app.route('/xhr/trakt/friends')
@app.route('/xhr/trakt/friends/<user>')
@requires_auth
def xhr_trakt_friends(user=None):
    logger.log('TRAKT :: Fetching friends list', 'INFO')
    pending = []
    if not user:
        friends_url = 'http://api.trakt.tv/user/friends.json/%s/%s' % (trakt_apikey(), get_setting_value('trakt_username'))
        pending_url = 'http://api.trakt.tv/friends/requests/%s' % trakt_apikey()
    else:
        friends_url = 'http://api.trakt.tv/user/friends.json/%s/%s' % (trakt_apikey(), user)

    try:
        friends = trak_api(friends_url)
        if not user:
            pending = trak_api(pending_url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    return render_template('traktplus/trakt-friends.html',
        friends=friends,
        pending=pending,
        title='Friends',
    )


@app.route('/xhr/trakt/friend/<action>/<user>')
@requires_auth
def xhr_trakt_friend_action(action, user):
    url = 'http://api.trakt.tv/friends/%s/%s' % (action, trakt_apikey())
    params = {'friend': user}

    try:
        trakt = trak_api(url, params)
    except Exception as e:
        trakt_exception(e)
        return jsonify(status='%s friend failed\n%s' % (action.title(), e))

    if trakt['status'] == 'success':
        return jsonify(status='successful')
    else:
        return jsonify(status=action.title() + ' friend failed')


@app.route('/xhr/trakt/profile')
@app.route('/xhr/trakt/profile/<user>')
@requires_auth
def xhr_trakt_profile(user=None):
    if not user:
        user = get_setting_value('trakt_username')

    logger.log('TRAKT :: Fetching %s\'s profile information' % user, 'INFO')

    url = 'http://api.trakt.tv/user/profile.json/%s/%s/' % (trakt_apikey(), user)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

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

    return render_template('traktplus/trakt-user_profile.html',
        profile=trakt,
        user=user,
        movies_progress=int(movies_progress),
        episodes_progress=int(episodes_progress),
        title='Profile',
    )


@app.route('/xhr/trakt/progress/<user>')
@app.route('/xhr/trakt/progress/<user>/<type>')
@requires_auth
def xhr_trakt_progress(user, type=None):
    if not type:
        type = 'watched'

    logger.log('TRAKT :: Fetching %s\'s %s progress' % (user, type), 'INFO')
    url = 'http://api.trakt.tv/user/progress/%s.json/%s/%s' % (type, trakt_apikey(), user)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    return render_template('traktplus/trakt-progress.html',
        progress=trakt,
        user=user,
        type=type,
    )


@app.route('/xhr/trakt/library/<user>')
@app.route('/xhr/trakt/library/<user>/<type>')
@requires_auth
def xhr_trakt_library(user, type=None):
    if not type:
        type = get_setting_value('trakt_default_media')

    logger.log('TRAKT :: Fetching %s\'s %s library' % (user, type), 'INFO')
    url = 'http://api.trakt.tv/user/library/%s/all.json/%s/%s' % (type, trakt_apikey(), user)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    return render_template('traktplus/trakt-library.html',
        library=trakt,
        user=user,
        type=type.title(),
        title='Library',
    )


@app.route('/xhr/trakt/watchlist/<user>')
@app.route('/xhr/trakt/watchlist/<user>/<type>')
@requires_auth
def xhr_trakt_watchlist(user, type=None):
    if not type:
        type = get_setting_value('trakt_default_media')

    logger.log('TRAKT :: Fetching %s\'s %s watchlist' % (user, type), 'INFO')
    url = 'http://api.trakt.tv/user/watchlist/%s.json/%s/%s/' % (type, trakt_apikey(), user)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    if trakt == []:
        trakt = [{'empty': True}]

    return render_template('traktplus/trakt-watchlist.html',
        watchlist=trakt,
        type=type.title(),
        user=user,
        title='Watchlist',
    )


@app.route('/xhr/trakt/rated/<user>/<type>')
@app.route('/xhr/trakt/rated/<user>')
@requires_auth
def xhr_trakt_rated(user, type=None):
    if not type:
        type = get_setting_value('trakt_default_media')
    logger.log('TRAKT :: Fetching %s\'s rated %s' % (user, type), 'INFO')
    url = 'http://api.trakt.tv/user/ratings/%s.json/%s/%s/all/extended' % (type, trakt_apikey(), user)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    total = len(trakt)
    loved = 0
    hated = 0
    rated = {
        'loved': [],
        'hated': []
    }

    if trakt:
        for item in trakt:
            if item['rating'] == 'love':
                rated['loved'].append(item)
            elif item['rating'] == 'hate':
                rated['hated'].append(item)
        loved = len(rated['loved'])
        hated = len(rated['hated'])

    return render_template('traktplus/trakt-rated.html',
        rated=rated,
        total=total,
        loved=loved,
        hated=hated,
        type=type.title(),
        user=user,
        title='Rated',
    )


@app.route('/xhr/trakt/calendar/<type>')
@requires_auth
def xhr_trakt_calendar(type):
    logger.log('TRAKT :: Fetching %s calendar' % type, 'INFO')
    username = get_setting_value('trakt_username')

    if type == 'my shows':
        url = 'http://api.trakt.tv/user/calendar/shows.json/%s/%s' % (trakt_apikey(), username)
    else:
        url = 'http://api.trakt.tv/calendar/%s.json/%s/' % (type, trakt_apikey())

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    return render_template('traktplus/trakt-calendar.html',
        calendar=trakt,
        type=type.title(),
        title='Calendar',
    )


@app.route('/xhr/trakt/summary/<type>/<id>')
@app.route('/xhr/trakt/summary/<type>/<id>/<season>/<episode>')
@requires_auth
def xhr_trakt_summary(type, id, season=None, episode=None):

    if type == 'episode':
        url = 'http://api.trakt.tv/show/%s/summary.json/%s/%s/%s/%s' % (type, trakt_apikey(), id, season, episode)
    else:
        url = 'http://api.trakt.tv/%s/summary.json/%s/%s' % (type, trakt_apikey(), id)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    if type != 'episode':
        trakt['images']['poster'] = cache_image(trakt['images']['poster'], type + 's')
        if type == 'show':
            trakt['first_aired'] = datetime.datetime.fromtimestamp(int(trakt['first_aired'])).strftime('%B %d, %Y')
    else:
        trakt['episode']['first_aired'] = datetime.datetime.fromtimestamp(int(trakt['episode']['first_aired'])).strftime('%B %d, %Y')

    while THREADS:
        time.sleep(1)

    if type == 'episode':
        return render_template('traktplus/trakt-episode.html',
            episode=trakt,
            type=type,
            title=trakt['episode']['title'],
            )
    elif type == 'show':
        return render_template('traktplus/trakt-show.html',
            show=trakt,
            type=type,
            title=trakt['title'],
            )
    else:
        return render_template('traktplus/trakt-movie.html',
            movie=trakt,
            type=type,
            title=trakt['title'],
            )


@app.route('/xhr/trakt/get_lists/', methods=['POST'])
@app.route('/xhr/trakt/get_lists/<user>', methods=['GET'])
@requires_auth
def xhr_trakt_get_lists(user=None):
    if not user:
        user = get_setting_value('trakt_username')

    logger.log('TRAKT :: Fetching %s\'s custom lists' % user, 'INFO')
    url = 'http://api.trakt.tv/user/lists.json/%s/%s' % (trakt_apikey(), user)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    if request.method == 'GET':
        return render_template('traktplus/trakt-custom_lists.html',
            lists=trakt,
            user=user,
            title='lists'
        )

    else:
        return render_template('traktplus/trakt-add_to_list.html',
            lists=trakt,
            custom_lists=True,
            media=request.form,
        )


@app.route('/xhr/trakt/list/<slug>/<user>')
@requires_auth
def xhr_trakt_custom_list(slug, user):

    logger.log('TRAKT :: Fetching %s' % slug, 'INFO')
    url = 'http://api.trakt.tv/user/list.json/%s/%s/%s' % (trakt_apikey(), user, slug)

    try:
        trakt = trak_api(url)
    except Exception as e:
        trakt_exception(e)
        return render_template('traktplus/trakt-base.html', message=e)

    return render_template('traktplus/trakt-custom_lists.html',
        list=trakt,
        title=trakt['name'],
    )


@app.route('/xhr/trakt/add_to_list/', methods=['POST'])
@requires_auth
def xhr_trakt_add_to_list():
    media = json.JSONDecoder().decode(request.form['media'])
    list = json.JSONDecoder().decode(request.form['list'])
    exist = request.form['exist']

    if exist == 'false':
        logger.log('TRAKT :: Creating new custom list: %s' % (list[0]['value']), 'INFO')
        url = 'http://api.trakt.tv/lists/add/%s' % trakt_apikey()

        list_params = {}
        for item in list:
            if item['value'] == '0':
                item['value'] = False
            elif item['value'] == '1':
                item['value'] == True
            list_params[item['name']] = item['value']

        list = list_params

        try:
            trakt = trak_api(url, list)
        except Exception as e:
            trakt_exception(e)
            return jsonify(status='Failed to add %s to %s\n%s' % (media['title'], list['name'], e))

        list['slug'] = list['name'].replace(' ', '-')

    logger.log('TRAKT :: Adding %s to %s' % (media['title'], list['name']), 'INFO')
    url = 'http://api.trakt.tv/lists/items/add/%s' % (trakt_apikey())
    params = {
        'slug': list['slug'],
        'items': [media]
    }

    try:
        trakt = trak_api(url, params)
    except Exception as e:
        trakt_exception(e)
        return jsonify(status='Failed to add %s to %s\n%s' % (media['title'], list['name'], e))

    if trakt['status'] == 'success':
        return jsonify(status='successful')
    else:
        return jsonify(status='Failed to add %s to %s' % (media['title'], list['name']))


@app.route('/xhr/trakt/action/<action>/<type>/', methods=['POST'])
@requires_auth
def xhr_trakt_action(type, action):
    #rate, seen, watchlist, library, dismiss
    logger.log('TRAKT :: %s: %s' % (type, action), 'INFO')
    url = 'http://api.trakt.tv/%s/%s/%s' % (type, action, trakt_apikey())
    params = {}

    if action == 'rate':
        url = 'http://api.trakt.tv/rate/%s/%s' % (type, trakt_apikey())
        for k, v in request.form.iteritems():
            params[k] = v

    if action == 'library' and type == 'show':
        for k, v in request.form.iteritems():
            params[k] = v

    elif action == 'dismiss':
        url = 'http://api.trakt.tv/recommendations/%ss/dismiss/%s' % (type, trakt_apikey())
        for k, v in request.form.iteritems():
            params[k] = v

    else:
        params[type + 's'] = [{}]

        for k, v in request.form.iteritems():
            params[type + 's'][0][k] = v

    if action == 'seen':
        params[type + 's'][0]['plays'] = 1
        params[type + 's'][0]['last_played'] = int(time.time())

    try:
        trakt = trak_api(url, params)
    except Exception as e:
        trakt_exception(e)
        return jsonify(status='Action failed\n%s' % e)

    if trakt['status'] == 'success':
        return jsonify(status='successful')
    else:
        return jsonify(status='Action failed')
