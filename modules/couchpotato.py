from flask import render_template, request, jsonify, json, send_file
from jinja2.filters import FILTERS
from maraschino.tools import get_setting_value, requires_auth
from maraschino import logger, app, WEBROOT
import urllib
import StringIO


def login_string():
    try:
        login = '%s:%s@' % (get_setting_value('couchpotato_user'), get_setting_value('couchpotato_password'))

    except:
        login = ''

    return login


def couchpotato_url():
    return 'http://%s%s:%s/api/%s' % (login_string(), get_setting_value('couchpotato_ip'), get_setting_value('couchpotato_port'), get_setting_value('couchpotato_api'))


def couchpotato_url_no_api():
    return 'http://%s%s:%s/' % (login_string(), get_setting_value('couchpotato_ip'), get_setting_value('couchpotato_port'))


def couchpotato_api(method, params=None, use_json=True, dev=False):
    if params:
        params = '/?%s' % params
    else:
        params = '/'

    url = '%s/%s%s' % (couchpotato_url(), method, params)
    data = urllib.urlopen(url).read()
    if dev:
        print url
        print data
    if use_json:
        data = json.JSONDecoder().decode(data)
    return data


def log_exception(e):
    logger.log('CouchPotato :: EXCEPTION -- %s' % e, 'DEBUG')


def couchpotato_image(path):
    if path.startswith('/'):
        path = path[1:]
    return '%s/xhr/couchpotato/image/%s' % (WEBROOT, path)


FILTERS['cp_img'] = couchpotato_image


@app.route('/xhr/couchpotato/image/<path:url>')
def couchpotato_proxy(url):
    url = '%s/file.cache/%s' % (couchpotato_url(), url)
    img = StringIO.StringIO(urllib.urlopen(url).read())
    return send_file(img, mimetype='image/jpeg')


@app.route('/xhr/couchpotato/')
@app.route('/xhr/couchpotato/<status>/')
def xhr_couchpotato(status=False):
    if status:
        status_string = 'status=%s' % status
        template = 'couchpotato-all.html'
    else:
        status = 'wanted'
        status_string = False
        template = 'couchpotato.html'
    try:
        logger.log('CouchPotato :: Fetching "%s movies" list' % status, 'INFO')
        couchpotato = couchpotato_api('movie.list', params=status_string)
        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except Exception as e:
        log_exception(e)
        couchpotato = None

    logger.log('CouchPotato :: Fetching "%s movies" list (DONE)' % status, 'INFO')
    return render_template(template,
        url=couchpotato_url(),
        couchpotato=couchpotato,
        compact_view=get_setting_value('couchpotato_compact') == '1',
    )


@app.route('/xhr/couchpotato/search/')
def cp_search():
    couchpotato = {}
    params = False
    profiles = {}

    try:
        params = 'q=' + request.args['name']
    except:
        pass

    if params:
        try:
            logger.log('CouchPotato :: Searching for movie: %s' % (params), 'INFO')
            couchpotato = couchpotato_api('movie.search', params=params)
            amount = len(couchpotato['movies'])
            logger.log('CouchPotato :: found %i movies for %s' % (amount, params), 'INFO')
            if couchpotato['success'] and amount != 0:
                couchpotato = couchpotato['movies']
                try:
                    logger.log('CouchPotato :: Getting quality profiles', 'INFO')
                    profiles = couchpotato_api('profile.list')
                except Exception as e:
                    log_exception(e)
            else:
                return render_template('couchpotato-search.html', error='No movies with "%s" were found' % (params[2:]), couchpotato='results')

        except Exception as e:
            log_exception(e)
            couchpotato = None

    else:
        logger.log('CouchPotato :: Loading search template', 'DEBUG')
        couchpotato = None

    return render_template('couchpotato-search.html',
        data=couchpotato,
        couchpotato='results',
        profiles=profiles,
    )


@app.route('/xhr/couchpotato/add_movie/<imdbid>/<title>/')
@app.route('/xhr/couchpotato/add_movie/<imdbid>/<title>/<profile>/')
def add_movie(imdbid, title, profile=False):
    if profile:
        params = 'identifier=%s&title=%s&profile_id=%s' % (imdbid, title, profile)
    else:
        params = 'identifier=%s&title=%s' % (imdbid, title)

    try:
        logger.log('CouchPotato :: Adding %s (%s) to wanted list' % (title, imdbid), 'INFO')
        result = couchpotato_api('movie.add', params)
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/restart/')
@requires_auth
def cp_restart():
    try:
        logger.log('CouchPotato :: Restarting', 'INFO')
        result = couchpotato_api('app.restart', use_json=False)
        if 'restarting' in result:
            return jsonify({'success': True})
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/available/')
@requires_auth
def cp_available():
    try:
        logger.log('CouchPotato :: Checking if CouchPotato is available', 'INFO')
        result = couchpotato_api('app.available')
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/shutdown/')
@requires_auth
def cp_shutdown():
    try:
        logger.log('CouchPotato :: Shutting down', 'INFO')
        result = couchpotato_api('app.shutdown', use_json=False)
        if 'shutdown' in result:
            return jsonify({'success': True})
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/version/')
@requires_auth
def cp_version():
    try:
        result = couchpotato_api('app.version')
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/profiles/')
@requires_auth
def cp_profiles():
    try:
        logger.log('CouchPotato :: Getting profiles', 'INFO')
        result = couchpotato_api('profile.list')
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/quality/')
@requires_auth
def cp_quality():
    try:
        logger.log('CouchPotato :: Getting quality', 'INFO')
        result = couchpotato_api('quality.list')
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/update/check/')
@requires_auth
def cp_update_check():
    try:
        logger.log('CouchPotato :: Getting update', 'INFO')
        result = couchpotato_api('updater.check')
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/delete_movie/<id>/')
@requires_auth
def movie_delete(id):
    """
    Delete a movie from list
    ----- Params -----
    id                  int (comma separated)                       Movie ID(s) you want to delete.
    delete_from         string: all (default), wanted, manage       Delete movie from this page
    """
    try:
        logger.log('CouchPotato :: Deleting movie %s' % id, 'INFO')
        result = couchpotato_api('movie.delete', 'id=%s' % id)
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/refresh_movie/<id>/')
def movie_refresh(id):
    """
    Refresh a movie from list
    ----- Params -----
    id                  int (comma separated)                       Movie ID(s) you want to refresh.
    """
    try:
        logger.log('CouchPotato :: Refreshing movie %s' % id, 'INFO')
        result = couchpotato_api('movie.refresh', 'id=%s' % id)
        return jsonify(result)
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/settings/')
def cp_settings():
    """
    Retrieve settings from CP
    """
    try:
        logger.log('CouchPotato :: Retrieving settings', 'INFO')
        result = couchpotato_api('settings')
        logger.log('CouchPotato :: Retrieving settings (DONE)', 'INFO')
        return render_template('couchpotato-settings.html',
            couchpotato=result,
        )
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/get_movie/<id>/')
def cp_get_movie(id):
    """
    Retrieve movie from CP
    ---- Params -----
    id                  int (comma separated)                       The id of the movie
    """
    try:
        logger.log('CouchPotato :: Retrieving movie info', 'INFO')
        result = couchpotato_api('movie.get', 'id=%s' % id)
        try:
            logger.log('CouchPotato :: Getting quality profiles', 'INFO')
            profiles = couchpotato_api('profile.list')
        except Exception as e:
            log_exception(e)
        logger.log('CouchPotato :: Retrieving movie info (DONE)', 'INFO')
        return render_template('couchpotato-info.html',
            couchpotato=result,
            profiles=profiles,
        )
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/edit_movie/<movieid>/<profileid>/')
def cp_edit_movie(movieid, profileid):
    """
    Edit movie in CP
    ---- Params -----
    movieid                  int (comma separated)                       The id of the movie
    profileid                int                                         Id of the profile to go to
    """
    try:
        logger.log('CouchPotato :: Retrieving movie info', 'INFO')
        result = couchpotato_api('movie.edit', 'id=%s&profile_id=%s' % (movieid, profileid))
        if result['success']:
            logger.log('CouchPotato :: Retrieving movie info (DONE)', 'INFO')
            return jsonify({'success': True})
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/log/')
@app.route('/xhr/couchpotato/log/<type>/<lines>/')
def cp_log(type='all', lines=30):
    """
    Edit movie in CP
    ---- Params -----
    type <optional>          all, error, info, debug                     Type of log
    lines <optional>         int                                         Number of lines - last to first
    """
    try:
        logger.log('CouchPotato :: Retrieving "%s" log' % type, 'INFO')
        result = couchpotato_api('logging.partial', 'type=%s&lines=%s' % (type, lines))
        if result['success']:
            logger.log('CouchPotato :: Retrieving "%s" log (DONE)' % type, 'INFO')
            return render_template('couchpotato-log.html',
                couchpotato=result,
                level=type,
            )
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})
