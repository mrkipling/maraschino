from flask import Flask, jsonify, render_template, request
import hashlib, json, jsonrpclib, urllib, random
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
	rand = random.randint(0,10)
	
	try:
		params = {
	  	'username': TRAKT_USERNAME,
	  	'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest()
		}
	except:
		params = {}
		
	url = 'http://api.trakt.tv/recommendations/movies/%s' % (TRAKT_API_KEY)
	params = urllib.urlencode(params)
	result = urllib.urlopen(url, params).read()
	result = json.JSONDecoder().decode(result)
	movie = result[rand]
# 	pprint(movie)
# 	title = movie['title']
# 	url = movie['url']
	#pprint(movie)
	return render_template('recommendations.html',
	  url = movie['url'],
	  title = movie['title'],
	  image = movie['images']['poster'],
	  overview = movie['overview'],
	  year = movie['year'],
	  liked = movie['ratings']['percentage']
	  )