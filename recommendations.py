from flask import Flask, jsonify, render_template, request
import hashlib, json, jsonrpclib, urllib

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/recommendations')
@requires_auth
def xhr_recom():
    trakt = {}
    TRAKT_API_KEY = None
    TRAKT_USERNAME = None
    TRAKT_PASSWORD = None

    try:
	    TRAKT_API_KEY = get_setting_value('trakt_api_key')
	    TRAKT_USERNAME = get_setting_value('trakt_username')
	    TRAKT_PASSWORD = get_setting_value('trakt_password')
	    
	    params = {
	        'username': TRAKT_USERNAME,
	        'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest()
	    }

	  
	  except:
      return render_template('recommend.html',
          trakt = trakt
        )

	   
    
    try:
      url = 'http://api.trakt.tv/recommendations/movies/%s' % (TRAKT_API_KEY)
      params = urllib.urlencode(params)
      result = urllib.urlopen(url, params).read()
      result = json.JSONDecoder().decode(result)

      if result['status'] == 'success':
        return render_template('recommend.html',
            trakt = result
          )

    except:
        pass

    return jsonify({ 'status': 'error' })

    
@app.route('/trakt/movies/', methods=['POST'])
@requires_auth
def movie_recommendations():
    TRAKT_API_KEY = get_setting_value('trakt_api_key')
    TRAKT_USERNAME = get_setting_value('trakt_username')
    TRAKT_PASSWORD = get_setting_value('trakt_password')

    params = {
        'username': TRAKT_USERNAME,
        'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest()
    }
    
    try:
      url = 'http://api.trakt.tv/recommendations/movies/%s' % (TRAKT_API_KEY)
      params = urllib.urlencode(params)
      result = urllib.urlopen(url, params).read()
      result = json.JSONDecoder().decode(result)

      if result['status'] == 'success':
        return result

    except:
        pass

    return jsonify({ 'status': 'error' })


