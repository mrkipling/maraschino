from flask import Flask, jsonify, render_template, request
import hashlib, json, jsonrpclib, urllib
from pprint import pprint

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/recommendations')
def xhr_recommendations():
	  TRAKT_API_KEY = get_setting_value('trakt_api_key')
	  TRAKT_USERNAME = get_setting_value('trakt_username')
	  TRAKT_PASSWORD = get_setting_value('trakt_password')
	    
	  params = {
	      'username': TRAKT_USERNAME,
	      'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest()
	  }
	   
    
    try:
      url = 'http://api.trakt.tv/recommendations/movies/%s' % (TRAKT_API_KEY)
#       params = urllib.urlencode(params)
      movie = urllib.urlopen(url, params).read()
      result = json.JSONDecoder().decode(movie)
			
			movie = dir(movie)
			pprint(movie)
						
      if result['status'] == 'success':
        return render_template('recommendations.html',
             result = result,
          )

    except:
        return render_template('recommendations.html',
             result = {},
          )
