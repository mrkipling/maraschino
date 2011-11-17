from flask import Flask, jsonify, render_template, request
import hashlib, json, jsonrpclib, urllib, random
from pprint import pprint

from maraschino import app
from settings import *
from noneditable import *
from tools import *

TRAKT_API_KEY = get_setting_value('trakt_api_key')
TRAKT_USERNAME = get_setting_value('trakt_username')
TRAKT_PASSWORD = get_setting_value('trakt_password')

@app.route('/xhr/recommendations')
def xhr_recommendations():
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
	
	if movie['imdb_id'] != '':
		movie_id = movie['imdb_id']
	else:
		movie_id = movie['tmdb_id']
		
	return render_template('recommendations.html',
	  url = movie['url'],
	  title = movie['title'],
	  image = movie['images']['poster'],
	  overview = movie['overview'],
	  year = movie['year'],
	  liked = movie['ratings']['percentage'],
	  id = movie_id,
	  watchlist = movie['in_watchlist']
	  )
	  
@app.route('/trakt/add_to_watchlist/<movieid>/<title>/<year>/')
@requires_auth
def add_to_watchlist(movieid, title, year):
		try:
			params = {
		  	'username': TRAKT_USERNAME,
		  	'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest(),
				'movies': {	'imdb_id': movieid, 
										'title': title, 
										'year': year
									}
			}
		except:
			raise Exception
			
		try:
			url = 'http://api.trakt.tv/movie/watchlist/%s' % (TRAKT_API_KEY)
			params = urllib.urlencode(params)
			result = urllib.urlopen(url, params).read()
			result = json.JSONDecoder().decode(result)
			
			if result['status'] == 'success':
				return 'Item successfully added to Watchlist'
			else:
				return 'I\'m sorry, an error ocurred: %s' % (result)
		
		except:
			return ''

@app.route('/trakt/dismiss_rec/<movieid>/<title>/<year>/')
@requires_auth
def dimiss_reccomendation(movieid, title, year):
		try:
			params = {
		  	'username': TRAKT_USERNAME,
		  	'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest(),
				'imdb_id': movieid, 
				'title': title, 
				'year': year
			}
		except:
			raise Exception
			
		try:
			url = 'http://api.trakt.tv/recommendations/movies/dismiss/%s' % (TRAKT_API_KEY)
			params = urllib.urlencode(params)
			result = urllib.urlopen(url, params).read()
			result = json.JSONDecoder().decode(result)
			
			if result['status'] == 'success':
				return '%s: %s' % (result['status'], result['message'])
			else:
				return 'I\'m sorry, an error ocurred: %s' % (result)
		
		except:
			return ''
