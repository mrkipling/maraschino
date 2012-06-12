try:
    import json
except ImportError:
    import simplejson as json
from flask import Flask, jsonify, render_template, request
import hashlib, jsonrpclib, urllib

from Maraschino import app
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/trakt')
@requires_auth
def xhr_trakt():
    trakt = {}
    TRAKT_API_KEY = None

    try:
        xbmc = jsonrpclib.Server(server_api_address())
        TRAKT_API_KEY = get_setting_value('trakt_api_key')

        if not TRAKT_API_KEY:
            raise Exception()

    except:
        return render_template('trakt.html',
            trakt = trakt,
        )

    TRAKT_USERNAME = get_setting_value('trakt_username')
    TRAKT_PASSWORD = get_setting_value('trakt_password')

    try:
        currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['tvshowid', 'season', 'episode', 'imdbnumber', 'title'])['item']
        trakt['itemid'] = currently_playing['imdbnumber']

        # if watching a TV show
        if currently_playing['tvshowid'] != -1:
            show = xbmc.VideoLibrary.GetTVShowDetails(tvshowid = currently_playing['tvshowid'], properties = ['imdbnumber'])['tvshowdetails']
            trakt['itemid'] = show['imdbnumber']

    except:
        currently_playing = None

    if currently_playing and TRAKT_API_KEY:
        trakt['title'] = currently_playing['title']

        if currently_playing['tvshowid'] != -1:
            trakt['type'] = 'episode'
            trakt['season'] = currently_playing['season']
            trakt['episode'] = currently_playing['episode']
            url = 'http://api.trakt.tv/show/episode/shouts.json/%s/%s/%s/%s' % (TRAKT_API_KEY, trakt['itemid'], currently_playing['season'], currently_playing['episode'])

        else:
            trakt['type'] = 'movie'
            url = 'http://api.trakt.tv/movie/shouts.json/%s/%s' % (TRAKT_API_KEY, trakt['itemid'])

        result = urllib.urlopen(url).read()
        trakt['shouts'] = json.JSONDecoder().decode(result)

    else:
        trakt = None

    show_add_shout = False

    try:
        if TRAKT_PASSWORD:
            show_add_shout = True

    except:
        pass

    try:
        if not trakt['shouts'] and not show_add_shout:
            trakt = None

    except:
        pass

    return render_template('trakt.html',
        trakt = trakt,
        trakt_username = TRAKT_USERNAME,
        show_add_shout = show_add_shout,
    )

@app.route('/xhr/trakt/add_shout', methods=['POST'])
@requires_auth
def xhr_trakt_add_shout():
    TRAKT_API_KEY = get_setting_value('trakt_api_key')
    TRAKT_USERNAME = get_setting_value('trakt_username')
    TRAKT_PASSWORD = get_setting_value('trakt_password')

    try:
        itemtype = request.form['type']

        params = {
            'username': TRAKT_USERNAME,
            'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest(),
            'shout': request.form['shout'],
        }

        spoiler = request.form['spoiler']

        if spoiler == 'true':
            params['spoiler'] = True

        if itemtype == 'episode':
            params['season'] = request.form['season']
            params['tvdb_id'] = request.form['itemid']
            params['episode'] = request.form['episode']

        else:
            params['imdb_id'] = request.form['itemid']

    except:
        return jsonify({ 'status': 'error' })

    try:
        url = 'http://api.trakt.tv/shout/%s/%s' % (itemtype, TRAKT_API_KEY)
        params = urllib.urlencode(params)
        result = urllib.urlopen(url, params).read()
        result = json.JSONDecoder().decode(result)

        if result['status'] == 'success':
            return xhr_trakt()

    except:
        pass

    return jsonify({ 'status': 'error' })
