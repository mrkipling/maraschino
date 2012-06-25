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


@app.route('/xhr/couchpotato/')
def xhr_couchpotato():
    try:
        logger.log('CouchPotato :: Fetching wanted list', 'INFO')
        url = '%s/movie.list/' % (couchpotato_url())
        result = urllib.urlopen(url).read()
        print result
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
        logger.log('CouchPotato :: Adding %s (%s) to CouchPotato\'s wanted list' % (title, imdbid), 'INFO')
        url = '%s/movie.add/?identifier=%s&title=%s' % (couchpotato_url(), imdbid, title)
        result = urllib.urlopen(url).read
        print url
        print result
    except:
        return jsonify({'status': False})

    return jsonify({'status': True})
