from flask import render_template, request, jsonify, json
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


def couchpotato_api(method, params=None):
    if params:
        params = '/?%s' % params
    else:
        params = ''
    try:
        url = '%s/%s%s' % (couchpotato_url(), method, params)
        result = urllib.urlopen(url).read()
        return result
    except:
        return jsonify({'success': False})


@app.route('/xhr/couchpotato/')
def xhr_couchpotato():
    try:
        logger.log('CouchPotato :: Fetching wanted list', 'INFO')
        url = '%s/movie.list/' % (couchpotato_url())
        result = urllib.urlopen(url).read()
        couchpotato = json.JSONDecoder().decode(result)

        if couchpotato['success'] and not couchpotato['empty']:
            couchpotato = couchpotato['movies']

    except:
        couchpotato = None

    compact_view = get_setting_value('couchpotato_compact') == '1'

    logger.log('CouchPotato :: Finished fetching wanted list', 'INFO')
    return render_template('couchpotato.html',
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

        except:
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
        url = '%s/movie.add/?identifier=%s&title=%s' % (couchpotato_url(), imdbid, title)
        result = urllib.urlopen(url).read()
        return jsonify({'status': True})
    except:
        return jsonify({'status': False})


@app.route('/xhr/couchpotato/restart/')
@requires_auth
def restart():
    try:
        logger.log('CouchPotato :: Restarting', 'INFO')
        return couchpotato_api('app.restart')
    except:
        return jsonify({'success': False})


@app.route('/xhr/couchpotato/available/')
@requires_auth
def available():
    try:
        logger.log('CouchPotato :: Checking if CouchPotato is available', 'INFO')
        return couchpotato_api('app.available')
    except:
        return jsonify({'success': False})


@app.route('/xhr/couchpotato/shutdown/')
@requires_auth
def shutdown():
    try:
        logger.log('CouchPotato :: Shutting down', 'INFO')
        return couchpotato_api('app.shutdown')
    except:
        return jsonify({'success': False})


@app.route('/xhr/couchpotato/version/')
@requires_auth
def version():
    try:
        return couchpotato_api('app.version')
    except:
        return jsonify({'success': False})


@app.route('/xhr/couchpotato/profiles/')
@requires_auth
def profiles():
    try:
        logger.log('CouchPotato :: Getting profiles', 'INFO')
        result = couchpotato_api('profile.list')
        result = json.JSONDecoder().decode(result)
        if result.success:
            return result
    except:
        pass

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/quality/')
@requires_auth
def quality():
    try:
        logger.log('CouchPotato :: Getting quality', 'INFO')
        result = couchpotato_api('quality.list')
        result = json.JSONDecoder().decode(result)
        if result.success:
            return result
    except:
        pass

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/update/check/')
@requires_auth
def update_check():
    try:
        logger.log('CouchPotato :: Getting update', 'INFO')
        result = couchpotato_api('updater.check')
        result = json.JSONDecoder().decode(result)
        if result.success:
            return result
    except:
        pass

    return jsonify({'success': False})


@app.route('/xhr/couchpotato/delete_movie/<id>')
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
        return result
    except Exception as e:
        print e

    return jsonify({'success': False})
