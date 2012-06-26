from flask import render_template, request, jsonify
import json
import urllib

from Maraschino import app
from maraschino.tools import *
from maraschino import logger


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


@app.route('/xhr/couchpotato/')
@app.route('/xhr/couchpotato/<status>/')
def xhr_couchpotato(status=False):
    if status:
        status = '?status=%s' % status
        template = 'couchpotato-all.html'
    else:
        status = ''
        template = 'couchpotato.html'
    try:
        logger.log('CouchPotato :: Fetching wanted list', 'INFO')
        url = '%s/movie.list/%s' % (couchpotato_url(), status)
        result = urllib.urlopen(url).read()
        couchpotato = json.JSONDecoder().decode(result)

        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except:
        couchpotato = None

    compact_view = get_setting_value('couchpotato_compact') == '1'

    logger.log('CouchPotato :: Finished fetching wanted list', 'INFO')
    return render_template(template,
        url=couchpotato_url(),
        couchpotato=couchpotato,
        compact_view=compact_view,
    )


@app.route('/xhr/couchpotato/search/')
def cp_search():
    couchpotato = {}
    params = ''

    try:
        params = request.args['name']
    except:
        pass

    if params is not '':
        try:
            logger.log('CouchPotato :: Searching for movie: %s' % (params), 'INFO')
            url = '%s/movie.search/?q=%s' % (couchpotato_url(), params)
            result = urllib.urlopen(url).read()
            couchpotato = json.JSONDecoder().decode(result)
            amount = len(couchpotato['movies'])
            logger.log('CouchPotato :: found %i movies for %s' % (amount, params), 'INFO')
            if couchpotato['success'] and amount != 0:
                couchpotato = couchpotato['movies']
            else:
                return render_template('couchpotato-search.html', error='No movies with "%s" were found' % (params), couchpotato='results')

        except Exception as e:
            log_exception(e)
            couchpotato = None

    else:
        logger.log('CouchPotato :: Loading search template', 'DEBUG')
        couchpotato = None

    return render_template('couchpotato-search.html',
        data=couchpotato,
        couchpotato='results',
    )


@app.route('/xhr/couchpotato/add_movie/<imdbid>/<title>/')
def add_movie(imdbid, title):
    try:
        logger.log('CouchPotato :: Adding %s (%s) to wanted list' % (title, imdbid), 'INFO')
        result = couchpotato_api('movie.add', 'identifier=%s&title=%s' % (imdbid, title), dev=True)
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
        print result
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
        print e

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
        print e

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
        return render_template('couchpotato-settings.html',
            couchpotato=result,
        )
    except Exception as e:
        log_exception(e)

    return jsonify({'success': False})
